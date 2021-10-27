SELECT s.seq, s.node, s.edge, s.cost,
b.gid, b.the_geom
FROM
(SELECT * FROM pgr_dijkstra(
    'SELECT gid AS id,
         source,
         target,
         cost_s AS cost,
         reverse_cost_s AS reverse_cost
        FROM ways',
    (SELECT source FROM ways
 ORDER BY the_geom <-> ST_SetSRID(ST_Point
 (-111.916621,40.390519),4326) LIMIT 1), (SELECT source FROM ways
 ORDER BY the_geom <-> ST_SetSRID(ST_Point
 (-111.919700,40.392619),4326) limit 1),
    directed := true)
) as s
LEFT JOIN ways b
ON (b.gid = s.edge)