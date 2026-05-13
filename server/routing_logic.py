from psycopg2.extras import RealDictCursor
from server_db import get_db_connection

# Function to find the cloeset node to the given coordinates
# I believe I don't need it. As I already compute the closest node as a column for all the facilities.
# I will leave it in case the location is for a user not for a facility.
def get_closest_node(coord, srid, cursor):
    """Find the closest node on the network to the given coordinates"""
    try:
        x_coord = float(coord[0])
        y_coord = float(coord[1])
        input_srid = int(srid)

        selectQuery = """SELECT id,
            ST_Distance(the_geom, ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), %s), st_srid(the_geom))) AS distance
            FROM cleaned_kh_final_vertices_pgr
            ORDER BY distance ASC
            LIMIT 1"""

        params = (x_coord, y_coord, input_srid)

        cursor.execute(selectQuery, params)
        result = cursor.fetchall()
        if len(result) > 0:
            return result[0]
        else:
            return None
    except Exception as e:
        raise Exception(f"Error finding closest node: {str(e)}")

#  Function for Routing
def get_shortest_path(source_coord, target_coord, srid):
    """Calculate the shortest path between two coordinates using pgr_dijkstra"""
    pg_conn = None
    try:
        # Validate input coordinates
        try:
            source_x, source_y = float(source_coord[0]), float(source_coord[1])
            target_x, target_y = float(target_coord[0]), float(target_coord[1])
            input_srid = int(srid)
        except (ValueError, IndexError) as e:
            return {"error": f"Invalid coordinate format: {str(e)}", "path": None}

        # Connect to database
        pg_conn = get_db_connection()
        pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)

        # Find closest nodes
        origin_node = get_closest_node(source_coord, srid, pg_cursor)
        target_node = get_closest_node(target_coord, srid, pg_cursor)

        if origin_node is None:
            return {"error": "Could not find closest node to source coordinates", "path": None}
        if target_node is None:
            return {"error": "Could not find closest node to target coordinates", "path": None}

        origin_id = origin_node["id"]
        target_id = target_node["id"]

        if origin_id == target_id:
            return {"error": "Source and target resolve to the same node", "path": None}

        # Query shortest path using pgr_dijkstra
        selectQuery = """
            WITH route_path AS (
            SELECT edge::integer as gid, seq
            FROM pgr_dijkstra(
                'SELECT id::bigint, source::bigint, target::bigint, cost, reverse_cost FROM cleaned_kh_final',
                %s ::bigint, %s ::bigint, true)
                )
            SELECT
            ST_AsGeoJSON(ST_Transform(ST_LineMerge(ST_Union(r.geom ORDER BY rp.seq)), %s ))::json as path,
            sum(ST_Length(r.geom)) as distance
            FROM cleaned_kh_final r
            JOIN route_path rp ON r.id = rp.gid"""

        params = (int(origin_id), int(target_id), input_srid)

        pg_cursor.execute(selectQuery, params)
        result = pg_cursor.fetchall()

        if len(result) > 0 and result[0]['path'] is not None:
            return {"path": result[0]['path'], "distance": float(result[0]['distance'])}
        else:
            return {"error": "No route found between the specified points", "path": None}

    except Exception as e:
        return {"error": str(e), "path": None}
    finally:
        if pg_conn:
            pg_conn.close()

# Function for Searching for nearby facilities
def get_nearby_facilities(loc, distance, srid):
    """ Retrieve the nearest facilities within selected distance -regardless of the types- """
    pg_conn = None
    try:
        # Validate inputs
        # Better to validate the inputs before calling the function
        # try:
        #     loc_x, loc_y = float(loc[0]), float(loc[1])
        #     input_distance = float(distance)
        #     input_srid = int(srid)
        # except (ValueError, IndexError) as e:
        #     return {"error": f"Invalid Input format: {str(e)}", "path": None}

        # Connect to database
        pg_conn = get_db_connection()
        pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)
        
        # Query
        # Watch the SRID I test the only working is 4326
        # 32.53319106 15.57396079
        #  The idea for now is to show all of the facilities with the selected distance regardless of the type.
        # Then each of the type will be displayed differently (symbol) 
        # Again with a possiblity of filtering based on the type/insurance
        # # However this query is to show each of the types close to the user location. (so no distance.)
        # SELECT *
        #     FROM (	
        #         SELECT *, 
        #                 ROW_NUMBER() OVER(PARTITION BY amenity ORDER BY geom <->  ST_GeomFromText('POINT(%s %s)',%d)) AS rn
        #         FROM facilities_kh
        #     ) AS ranked_table
        #     WHERE rn = 1;
        # # to test
        #  SELECT a.name_en, a.amenity, a.nearest_node_id, a.geom,  ST_AsGeoJSON(ST_Transform(a.geom, 4326)) as geom_tr
        #     FROM facilities_kh AS a
        #     WHERE (ST_DWithin(ST_Transform(a.geom, 3857), ST_GeomFromText('POINT(3622560 1755301)', 3857), 900)) 
        selectQuery = """
            SELECT a.name_en, a.amenity, a.nearest_node_id, ST_AsGeoJSON(ST_Transform(a.geom, %s)) as geom
            FROM facilities_kh AS a
            WHERE ST_DWithin(ST_Transform(a.geom, %s), ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), %s), %s), %s)
        """

        params = (
            int(srid),
            int(srid),
            # int(srid),
            float(loc[0]),
            float(loc[1]),
            int(srid),
            int(srid),
            float(distance),
        )
        
        pg_cursor.execute(selectQuery, params)
        result = pg_cursor.fetchall()
        print('result:', len(result))
        print("result:", result)
        print("""
            SELECT a.name_en, a.amenity, a.nearest_node_id, ST_AsGeoJSON(ST_Transform(a.geom, %s)) as geom
            FROM facilities_kh AS a
            WHERE ST_DWithin(ST_Transform(a.geom, %s), ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), %s), %s), %s)
        """%(int(srid), int(srid), float(loc[0]), float(loc[1]), int(srid), int(srid), float(distance)))
        # if len(result) > 0 and result[0]['path'] is not None:
        #     return {"path": result[0]['path'], "distance": float(result[0]['distance'])}
        if len(result) > 0:
            return {"rows": result, "number": len(result)}
        else:
            return {"error": "No facilities found with the specified distance", "rows": None}

    except Exception as e:
        return {"error": str(e), "rows": None}
    finally:
        if pg_conn:
            pg_conn.close()

# Function to find the closest facilities
def get_closest_facilities(loc, srid):
    """ Retrieve the nearest facilities -One of each type-"""
    pg_conn = None
    try:
        # Connect to database
        pg_conn = get_db_connection()
        pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)
        
        selectQuery = """
            SELECT *
            FROM (
                SELECT gid, name_en, amenity, nearest_node_id, geom,
                    ROW_NUMBER() OVER(PARTITION BY amenity ORDER BY geom <-> ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), %s), %s)) AS rn
                FROM facilities_kh
            ) AS ranked_table
            WHERE rn = 1;
        """

        params = (
            float(loc[0]),
            float(loc[1]),
            int(srid),
            int(srid),
        )
        
        pg_cursor.execute(selectQuery, params)
        result = pg_cursor.fetchall()
        print('result:', len(result))
        print("result:", result)
        print("""
            SELECT *
            FROM (
                SELECT gid, name_en, amenity, nearest_node_id, geom,
                    ROW_NUMBER() OVER(PARTITION BY amenity ORDER BY geom <-> ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), %s), %s)) AS rn
                FROM facilities_kh
            ) AS ranked_table
            WHERE rn = 1;
        """%(float(loc[0]), float(loc[1]), int(srid), int(srid)))

        if len(result) > 0:
            return {"rows": result, "number": len(result)}
        else:
            return {"error": "No facilities closer to you, choose another location", "rows": None}
    except Exception as e:
        return {"error": str(e), "rows": None}
    finally:
        if pg_conn:
            pg_conn.close()

#Function to compute the closest route to a facility
def get_routing_to_facility(u_closest_node_id, srid, closest_node_id):
    """ Routing between the user's location and the closest facility of a selected type."""
    pg_conn = None
    try:
        # Connect to database
        pg_conn = get_db_connection()
        pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)
        # Query shortest path using pgr_dijkstra
        selectQuery = """
            WITH route_path AS (
            SELECT edge::integer as gid, seq
            FROM pgr_dijkstra(
                'SELECT id::bigint, source::bigint, target::bigint, cost, reverse_cost FROM cleaned_kh_final',
                %s ::bigint, %s ::bigint, true)
                )
            SELECT
            ST_AsGeoJSON(ST_Transform(ST_LineMerge(ST_Union(r.geom ORDER BY rp.seq)), %s ))::json as path,
            sum(ST_Length(r.geom)) as distance
            FROM cleaned_kh_final r
            JOIN route_path rp ON r.id = rp.gid"""

        params = (int(u_closest_node_id), int(closest_node_id), int(srid))

        pg_cursor.execute(selectQuery, params)
        result = pg_cursor.fetchall()

        if len(result) > 0 and result[0]['path'] is not None:
            return {"path": result[0]['path'], "distance": float(result[0]['distance'])}
        else:
            return {"error": "No route found between the specified points", "path": None}

    except Exception as e:
        return {"error": str(e), "path": None}
    finally:
        if pg_conn:
            pg_conn.close()