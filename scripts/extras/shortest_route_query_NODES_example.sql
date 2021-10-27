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
    692, 219,
    directed := true)
) s
LEFT JOIN ways b
ON (b.gid = s.edge)