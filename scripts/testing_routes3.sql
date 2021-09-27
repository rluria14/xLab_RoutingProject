SELECT ST_UNION(b.the_geom) AS geojson
FROM
(SELECT
*
FROM
    pgr_nogo_astar(
        'SELECT gid AS id, source, target, cost, reverse_cost, x1, y1, x2, y2, the_geom AS geom FROM ways',
        (SELECT shape FROM hgis_admin3 WHERE adm3_name = 'Kitisuru'),
        63169,
        67860,
        TRUE,
        5,
        1.0,
        1.0
    )) s
LEFT JOIN ways b
ON (b.gid = s.edge)
WHERE the_geom is not NULL