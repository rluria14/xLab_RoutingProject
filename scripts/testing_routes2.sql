-- Create ways table that avoids bridges
CREATE TABLE ways_no_bridges AS
SELECT
  w.*
FROM
  ways AS w
LEFT JOIN
  hgis_bridges_tunnels AS h
ON
  st_dwithin(w.the_geom,h.shape, .0001)
WHERE h.objectid IS NULL;


-- Create ways table that avoids polygons
SELECT
  w.*
FROM
  ways AS w
LEFT JOIN
  hgis_admin3 AS h
ON
  st_intersects(w.the_geom,h.shape)
AND h.adm3_name = 'Kitisuru'  --If you want to get specific
WHERE h.objectid IS NULL


-- Find ways where bridges are close/connecting
SELECT w.* FROM ways w
	INNER JOIN hgis_bridges_tunnels h
		ON st_dwithin(w.the_geom, h.shape, .0001);


-- Generate route to avoid bridges from node to node
SELECT s.seq, s.node, s.edge, s.cost,
b.gid, b.the_geom
FROM
(SELECT * FROM pgr_astar(
    'SELECT gid AS id,
         source,
         target,
         cost_s AS cost,
		 x1, y1, x2, y2,
         reverse_cost_s AS reverse_cost
        FROM t_intersect',
    57177, 38590,
    directed := true)
) s
LEFT JOIN ways b
ON (b.gid = s.edge)