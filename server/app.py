# flask backend for the app
from flask import Flask, request, jsonify
from flask_cors import CORS

from routing_logic import get_shortest_path


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

        result = get_shortest_path(source, target, srid)

        if "error" in result and result["error"]:
            return jsonify(result), 400
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}", "path": None}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


#### RUNNING FLASK IN DEV MODE
if __name__ == '__main__':
    app.run(debug=True)
