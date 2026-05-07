-- pgRouting: Noding with ST_Node, create topology and shortest path example
-- Run section-by-section in pgAdmin. Adjust table/column names and tolerance.

-- 1) Extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- 2) Work on a copy
DROP TABLE IF EXISTS public.kh_roads_work;
CREATE TABLE public.kh_roads_work AS SELECT * FROM public.kh_roads;

-- 3) Repair invalid geometries
UPDATE public.kh_roads_work SET geom = ST_MakeValid(geom) WHERE NOT ST_IsValid(geom);
DELETE FROM public.kh_roads_work WHERE geom IS NULL OR ST_IsEmpty(geom);

-- 4) Ensure LineString singleparts
UPDATE public.kh_roads_work
SET geom = ST_LineMerge(ST_CollectionExtract(geom, 2))
WHERE GeometryType(geom) <> 'LINESTRING' OR ST_NumGeometries(geom) > 1;

-- 5) OPTIONAL: set SRID if missing
UPDATE public.kh_roads_work SET geom = ST_SetSRID(geom, 4326) WHERE ST_SRID(geom) = 0;

-- 6) Create a noded table using ST_Node (this forces explicit splitting at intersections)
    DROP TABLE IF EXISTS public.kh_roads_noded;
    CREATE TABLE public.kh_roads_noded AS
    SELECT (ST_Dump(ST_Node(geom))).geom::geometry(LineString, ST_SRID(geom)) AS geom, id
    FROM public.kh_roads_work;

-- 7) Remove empty rows
DELETE FROM public.kh_roads_noded WHERE geom IS NULL OR ST_IsEmpty(geom);

-- 8) Add routing columns to noded table
ALTER TABLE public.kh_roads_noded
  ADD COLUMN IF NOT EXISTS id BIGSERIAL PRIMARY KEY;

ALTER TABLE public.kh_roads_noded
  ADD COLUMN IF NOT EXISTS source BIGINT,
  ADD COLUMN IF NOT EXISTS target BIGINT,
  ADD COLUMN IF NOT EXISTS cost DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS reverse_cost DOUBLE PRECISION;

-- 9) Populate cost (length). If SRID is geographic (4326) consider using ST_LengthSphere or transform.
UPDATE public.kh_roads_noded
SET cost = ST_Length(geom), reverse_cost = ST_Length(geom);

-- 10) Create topology on the noded table
-- Choose tolerance: if SRID is degrees use small (1e-6). If meters use e.g. 0.5
-- There is no SRID WHEN I ran "SELECT f_table_schema, f_table_name, f_geometry_column, srid FROM geometry_columns WHERE f_table_name = 'kh_roads_noded';"


SELECT pgr_createTopology('public.kh_roads_noded', 0.00001, 'geom', 'id', 'source', 'target');

-- 11) Inspect generated vertices table
SELECT COUNT(*) FROM public.kh_roads_noded_vertices_pgr;
SELECT * FROM public.kh_roads_noded_vertices_pgr LIMIT 20;

-- 12) Quick diagnostics: components
SELECT * FROM pgr_connectedComponents('SELECT id, source, target, cost FROM public.kh_roads_noded') LIMIT 50;

-- 13) Find nearest vertices to coordinates (replace coords and SRID as needed)
-- Example coordinates (lon,lat)
SELECT id FROM public.kh_roads_noded_vertices_pgr
ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(103.8, 13.4), 4326)
LIMIT 1;

-- 14) Example shortest path between two vertex ids (replace 1 and 25 with ids found above)
SELECT seq, node, edge, cost FROM pgr_dijkstra(
  'SELECT id, source, target, cost, reverse_cost FROM public.kh_roads_noded',
  1, 25, directed := true
);

-- 15) Build geometry of route
WITH route AS (
  SELECT * FROM pgr_dijkstra('SELECT id, source, target, cost, reverse_cost FROM public.kh_roads_noded', 1, 25, directed := true)
)
SELECT ST_LineMerge(ST_Collect(rw.geom)) AS route_geom
FROM route
JOIN public.kh_roads_noded rw ON route.edge = rw.id;

-- 16) If still many disconnected components:
-- - Inspect sample edges that belong to tiny components, visualize in QGIS.
-- - Consider increasing tolerance for pgr_createTopology or run ST_Snap for endpoints before ST_Node.
-- Example snapping endpoints to a grid (careful, test on copy):
-- UPDATE public.kh_roads_work SET geom = ST_SnapToGrid(geom, 0.00001);

-- End of noding script.
