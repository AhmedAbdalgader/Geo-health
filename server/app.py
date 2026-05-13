# flask backend for the app
from flask import Flask, request, jsonify
# from flask_cors import CORS
from psycopg2.extras import RealDictCursor
from server_db import get_db_connection, init_db_pool
from routing_logic import get_closest_node, get_shortest_path, get_nearby_facilities, get_closest_facilities, get_routing_to_facility


#### FLASK CONFIGURATION
app = Flask(__name__)
# CORS(app)


#### ROUTES
@app.route('/routing', methods=['GET', 'POST'])
def routing():
    """
    Route handler for shortest path calculation

    Expected parameters:
    - source: "lat,lon" (comma-separated coordinates)
    - target: "lat,lon" (comma-separated coordinates)
    - srid: integer (spatial reference ID)

    Returns JSON with:
    - path: GeoJSON geometry
    - distance: calculated distance
    - error: error message if applicable
    """
    pg_conn = None
    try:
        if request.method == 'POST':
            data = request.get_json()
            source = data.get('source')  # type: ignore
            target = data.get('target')  # type: ignore
            srid = data.get('srid')  # type: ignore
        else:
            source = request.args.get('source')
            target = request.args.get('target')
            srid = request.args.get('srid')

        if not source or not target or not srid:
            return jsonify({"error": "Missing required parameters: source, target, or srid"}), 400

        source = source.split(",")
        target = target.split(",")

        # Borrow one connection and create cursor for multi-step operation
        pg_conn = get_db_connection()
        pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)

        result = get_shortest_path(source, target, srid, pg_cursor)

        if "error" in result and result["error"]:
            return jsonify(result), 400
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}", "path": None}), 500
    finally:
        if pg_conn:
            pg_conn.close()


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

#####
# This will be for searching the nearest Health facilities within a radius distance
# the inputs are: user coordinates, distance, SRID, and the type of facility (pharmacy, hospital, clinic) -later the type of the insurance.
# My idea for now is to make the type of the facility as a filter on the frontend.
# Another idea for integration is to introduce a traveling distance instead.
@app.route('/search_facilities', methods=['GET'])
def search_facilities():
    # return jsonify({"message": "This endpoint is under construction"}), 200
    """ I should document it later"""
    loc = request.args.get('loc')
    distance = request.args.get('distance')
    srid = request.args.get('srid')
    # facility_type = request.args.get('type')
    
    if not loc or not distance or not srid:
        return jsonify({"error": "Missing required parameters: loc, distance, or srid"}), 400
    
    loc = loc.split(",")
    try:
        loc_x, loc_y = float(loc[0]), float(loc[1])
        input_srid = int(srid)
        input_distance = float(distance)
        # If distance is zero
        if input_distance <= 0:
            return {"error": "Please choose distance bigger than 0", "path": None}
    except (ValueError, IndexError) as e:
        return jsonify({"error": f"Invalid input format: {str(e)}", "facilities": None}), 400
    
    result = get_nearby_facilities((loc_x, loc_y), input_distance, input_srid)
    if "error" in result and result["error"]:
        return jsonify(result), 400
    return jsonify(result), 200



###API endpoint for Search the nearest facilities one of each type. With calculating the distance from the selected location.
# The api will also calculate the shortest path.
# however upon pressing on the frontend the shortest path appears.
@app.route('/closest_facilities', methods=['GET'])
def closest_facilities():
    """ I should document it later """
    loc = request.args.get('loc')
    srid = request.args.get('srid')

    if not loc or not srid:
        return jsonify({"error": "Missing required parameters: loc or srid"}), 400
    
    loc = loc.split(",")
    try:
        loc_x, loc_y = float(loc[0]), float(loc[1])
        input_srid = int(srid)
    except (ValueError, IndexError) as e:
        return jsonify({"error": f"Invalid input format: {str(e)}", "facilities": None}), 400
    result = get_closest_facilities((loc_x, loc_y), input_srid)
    if "error" in result and result["error"]:
        return jsonify(result), 400
    return jsonify(result), 200



###Last API for the shortest route
# either two selected coordinates or facilities
# Routing between the user location and the closest facility of a type chosen by him.
# In this case I already have the closest_node_id.
# I will just compute the closest_node_id for the user's location then routing.
# The inputs user's loc, srid, facility's closest_node_id
@app.route('/routing_to_facility', methods=['GET'])
def routing_to_facility():
    """ I should document it later """
    loc = request.args.get('loc')
    srid = request.args.get('srid')
    closest_node_id = request.args.get('closest_node_id')
    
    if not loc or not srid or not closest_node_id:
        return jsonify({"error": "Missing required parameters: loc or srid"}), 400

    loc = loc.split(",")
    pg_conn = None
    pg_cursor = None
    try:
        loc_x, loc_y = float(loc[0]), float(loc[1])
        input_srid = int(srid)
        input_f_closest_node_id = int(closest_node_id)
        # Connect to database
        pg_conn = get_db_connection()
        pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)
        # Get fist the closest node to the user's location
        node = get_closest_node(loc,srid,pg_cursor)
        if node is None:
            return jsonify({"error": "Could not find closest node for the provided location", "path": None}), 400
        print('node:', node)
        u_closest_node_id = node['id']
        print('u_closest_node_id:', u_closest_node_id)

        result = get_routing_to_facility(u_closest_node_id, input_srid, input_f_closest_node_id, pg_cursor)
        if "error" in result and result["error"]:
            return jsonify(result), 400
        return jsonify(result), 200
    except (ValueError, IndexError) as e:
        return jsonify({"error": f"Invalid input format: {str(e)}", "facilities": None}), 400
    finally:
        if pg_conn:
            pg_conn.close()

####Coverage of facilities



####Coverage of insurances



#### RUNNING FLASK IN DEV MODE
if __name__ == '__main__':
    init_db_pool()
    app.run(debug=True)
