UPDATE ways SET rule=TRUE FROM hgis_conflict_points
WHERE st_dwithin(ways.the_geom, hgis_conflict_points.shape, 1000)


SELECT ways.osm_id FROM ways, hgis_conflict_points
WHERE st_dwithin(ways.the_geom, hgis_conflict_points.shape, 1000)
limit 10

SELECT s.seq, s.node, s.edge, s.cost,
b.gid, b.the_geom
FROM
(SELECT * FROM pgr_dijkstra(
    'SELECT gid AS id,
         source,
         target,
         cost_s AS cost,
         reverse_cost_s AS reverse_cost
        FROM ways
        WHERE not st_dwithin(ways.the_geom, st_makepoint(37.1419,-0.4869)::geography, 1000)',
    51934, 208683,
    directed := true)
) s
LEFT JOIN ways b
ON (b.gid = s.edge)