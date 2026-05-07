from psycopg2.extras import RealDictCursor

from server_db import get_db_connection


def get_closest_node(coord, srid, cursor):
    """Find the closest node on the network to the given coordinates"""
    try:
        x_coord = float(coord[0])
        y_coord = float(coord[1])
        input_srid = int(srid)

        selectQuery = """SELECT id,
            ST_Distance(the_geom, ST_Transform(ST_GeomFromText('POINT(%d %d)', %s), st_srid(the_geom))) AS distance
            FROM cleaned_kh_final_vertices_pgr
            ORDER BY distance ASC
            LIMIT 1""" % (x_coord, y_coord, input_srid)

        cursor.execute(selectQuery)
        result = cursor.fetchall()
        if len(result) > 0:
            return result[0]
        else:
            return None
    except Exception as e:
        raise Exception(f"Error finding closest node: {str(e)}")


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
            JOIN route_path rp ON r.id = rp.gid""" % (int(origin_id), int(target_id), input_srid)

        pg_cursor.execute(selectQuery)
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
