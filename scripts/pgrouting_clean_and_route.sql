-- pgRouting: Clean, build topology and find shortest path
-- Run this in pgAdmin Query Tool. Adjust names and tolerance where noted.

-- 0) IMPORTANT: Replace geometry column name if it's not "geom".
--    Replace schema/table names if your table isn't public.kh_roads

-- 1) Create required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- 2) Inspect table structure and SRID
-- Run and inspect results; adapt below if your geometry column has a different name.
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'kh_roads';

SELECT DISTINCT ST_SRID(geom) AS srid, COUNT(*)
FROM public.kh_roads
GROUP BY ST_SRID(geom);

-- 3) Make a working copy (do not modify the original yet)
DROP TABLE IF EXISTS public.kh_roads_work;
CREATE TABLE public.kh_roads_work AS
SELECT * FROM public.kh_roads;

-- 4) Fix invalid geometries
-- Count invalids
SELECT COUNT(*) AS invalid_count FROM public.kh_roads_work WHERE NOT ST_IsValid(geom);

-- Repair invalid geometries
UPDATE public.kh_roads_work
SET geom = ST_MakeValid(geom)
WHERE NOT ST_IsValid(geom);

-- 5) Convert multipart geometries to singlepart lines and ensure LineString
-- This will replace geometries with their line components and merge when possible
UPDATE public.kh_roads_work
SET geom = ST_LineMerge(ST_CollectionExtract(geom, 2))
WHERE GeometryType(geom) <> 'LINESTRING' OR ST_NumGeometries(geom) > 1;

-- 6) Remove or flag empty geometries created by previous steps
DELETE FROM public.kh_roads_work WHERE geom IS NULL OR ST_IsEmpty(geom);

-- 7) Ensure SRID is set and (optionally) transform to a suitable projected CRS
-- If your data is in geographic (EPSG:4326) routing and length measurements will be in degrees.
-- It's recommended to use a projected CRS (meters) for accurate lengths (e.g., UTM zone appropriate to your area).
-- Example: transform to EPSG:32736 (replace with appropriate projection for your country/area).
-- First inspect current SRID (from step 2). If srid=0, set it correctly using ST_SetSRID.

-- Example: set SRID if missing
UPDATE public.kh_roads_work
SET geom = ST_SetSRID(geom, 4326)
WHERE ST_SRID(geom) = 0;

-- Optional: transform to a metric CRS for better distance/cost calculations (uncomment and adjust SRID)
-- ALTER TABLE public.kh_roads_work ALTER COLUMN geom TYPE geometry(LINESTRING,3857) USING ST_Transform(geom,3857);

-- 8) Add routing columns
ALTER TABLE public.kh_roads_work
  ADD COLUMN IF NOT EXISTS id BIGSERIAL PRIMARY KEY;

ALTER TABLE public.kh_roads_work
  ADD COLUMN IF NOT EXISTS source BIGINT,
  ADD COLUMN IF NOT EXISTS target BIGINT,
  ADD COLUMN IF NOT EXISTS cost DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS reverse_cost DOUBLE PRECISION;

-- If id was just created above as BIGSERIAL, existing rows will have values; if your table already had an id, ensure it's unique and integer.
-- 9) Populate cost (length) — adjust ST_Length units based on CRS. If in degrees transform to metric or use ST_LengthSphere for rough metres.

-- If geometries are in a projected CRS (meters):
UPDATE public.kh_roads_work
SET cost = ST_Length(geom),
    reverse_cost = ST_Length(geom);

-- If geometries are in geographic CRS (lon/lat) and you didn't transform, use ST_LengthSphere for meters:
-- UPDATE public.kh_roads_work
-- SET cost = ST_LengthSphere(geom), reverse_cost = ST_LengthSphere(geom);

-- 10) (Optional) Set reverse_cost = -1 for forbidden reverse travel where your data indicates one-way.
-- Example: if you have a column "oneway" with values 'FT' or 'T' etc., adapt below.
-- UPDATE public.kh_roads_work SET reverse_cost = -1 WHERE oneway = 'yes';

-- 11) Run pgr_createTopology
-- Choose a tolerance appropriate to your CRS units.
-- If your data is in degrees (4326) use a tiny tolerance like 1e-6 or 1e-7.
-- If in meters use something like 0.5 to 10 depending on the dataset precision.
-- Set the variable below before running pgr_createTopology.

-- Example: set tolerance value here (replace as needed)
\-- -- TOLERANCE: adjust this value before running -- change the number and re-run the pgr_createTopology if needed
-- For degrees: 0.00001
-- For meters (projected): 0.5

-- Run topology creation (replace tolerance with your chosen value):
SELECT pgr_createTopology('public.kh_roads_work', 0.00001, 'geom', 'id', 'source', 'target');

-- If your table name is different or you transformed CRS, update the function arguments accordingly.

-- 12) Inspect/create vertices table
-- pgRouting creates a vertices table named <table>_vertices_pgr by default.
SELECT * FROM public.kh_roads_work_vertices_pgr LIMIT 20;

-- 13) Analyze the graph
SELECT pgr_analyzeGraph('public.kh_roads_work', 0.00001, 'geom', 'id', 'source', 'target');

-- Quick diagnostics: show vertices with degree (cnt) and incident edges
SELECT v.id, v.the_geom, v.x, v.y
FROM public.kh_roads_work_vertices_pgr v
LIMIT 20;

-- Find isolated vertices (degree 0) or vertices with low degree that may indicate dangling edges
SELECT v.id, v.x, v.y
FROM public.kh_roads_work_vertices_pgr v
LEFT JOIN (
  SELECT source AS vid FROM public.kh_roads_work
  UNION ALL
  SELECT target AS vid FROM public.kh_roads_work
) e ON v.id = e.vid
GROUP BY v.id, v.x, v.y
HAVING COUNT(e.vid) = 0;

-- 14) If many disconnected components exist, inspect components
-- You can find connected components using pgr_connectedComponents (pgr version dependent)
-- Example using pgr_connectedComponents (requires edges SQL-query)
SELECT * FROM pgr_connectedComponents(
  'SELECT id, source, target, cost FROM public.kh_roads_work'
) LIMIT 50;

-- 15) Find nearest vertex to a coordinate (example uses point in lon/lat - set SRID accordingly)
-- Replace coordinates with your start/end points
-- If your vertices are in a different SRID, transform the ST_SetSRID point accordingly.

-- Example: find nearest vertex to start point
SELECT id, x, y
FROM public.kh_roads_work_vertices_pgr
ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(103.8, 13.4), 4326)
LIMIT 1;

-- Example: nearest vertex to end point
SELECT id, x, y
FROM public.kh_roads_work_vertices_pgr
ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(103.9, 13.5), 4326)
LIMIT 1;

-- 16) Run pgr_dijkstra shortest path between two vertex ids (replace 1 and 25 with real ids)
SELECT seq, id1 AS node, id2 AS edge, cost
FROM pgr_dijkstra(
  'SELECT id, source, target, cost, reverse_cost FROM public.kh_roads_work',
  1, 25, directed := true
);

-- 17) Get the geometries of the path (lines) and build a single geometry route
WITH route AS (
  SELECT * FROM pgr_dijkstra('SELECT id, source, target, cost, reverse_cost FROM public.kh_roads_work', 1, 25, directed := true)
)
SELECT ST_Collect(rw.geom) AS route_geom
FROM route
JOIN public.kh_roads_work rw ON route.edge = rw.id;

-- 18) Iteration: if routing fails or the returned path is empty/partial
-- - Reevaluate tolerance and rerun pgr_createTopology (you may DROP the source/target columns and let pgr_createTopology repopulate them)
-- - Snap nearby endpoints: you can use ST_SnapToGrid or custom snapping scripts to snap vertices within a small distance
-- - Split lines at intersections explicitly using ST_Node (postgis topology function) before pgr_createTopology

-- Example: creating a noded network using ST_Node (careful: creates new table)
-- DROP TABLE IF EXISTS public.kh_roads_noded;
-- CREATE TABLE public.kh_roads_noded AS
-- SELECT (ST_Dump(ST_Node(geom))).geom AS geom
-- FROM public.kh_roads_work;

-- Then rebuild id/source/target/cost on kh_roads_noded and run pgr_createTopology on it.

-- End of script.
