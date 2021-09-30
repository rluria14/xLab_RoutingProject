import csv
import os
from datetime import datetime
import json

import psycopg2

from scripts.database import get_conn_pool, execute, fetch_all

dirname = os.path.dirname(__file__)

pool = get_conn_pool({
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'xlab-routing'
})

## avoid polygon
def route_nogo(nogo_layer, long_s, lat_s, long_t, lat_t, nogo_layer_query=""):
    s_geom = 'POINT({} {})'.format(long_s, lat_s)
    t_geom = 'POINT({} {})'.format(long_t, lat_t)

    #s_query = f"SELECT id FROM ways_vertices_pgr ORDER BY the_geom <-> ST_GeometryFromText('{s_geom}',4326) LIMIT 1"
    s_query = f'''
 	SELECT v.id FROM (SELECT UNNEST(array[w.source, w.target]) as id, w.the_geom FROM ways as w WHERE NOT
	ST_INTERSECTS(w.the_geom, (SELECT ST_COLLECT(hgis_hydrology_polylines.shape, hgis_admin3.shape) from hgis_hydrology_polylines, 	hgis_admin3 WHERE hgis_admin3.adm3_name = 'Kitisuru' LIMIT 1))
 	ORDER BY w.the_geom <-> ST_GeometryFromText('{s_geom}',4326) LIMIT 1) as ways2
 	JOIN ways_vertices_pgr as v
 	ON (v.id = ways2.id)
 	ORDER BY v.the_geom <-> ST_GeometryFromText('{s_geom}',4326) LIMIT 1
    '''
    source = fetch_all(pool, s_query)[0]
    print(source['id'])
    #t_query = f"SELECT id FROM ways_vertices_pgr ORDER BY the_geom <-> ST_GeometryFromText('{t_geom}',4326) LIMIT 1"
    t_query = f'''
 	SELECT v.id FROM (SELECT UNNEST(array[w.source, w.target]) as id, w.the_geom FROM ways as w WHERE NOT
	ST_INTERSECTS(w.the_geom, (SELECT ST_COLLECT(hgis_hydrology_polylines.shape, hgis_admin3.shape) from hgis_hydrology_polylines, 	hgis_admin3 WHERE hgis_admin3.adm3_name = 'Kitisuru' LIMIT 1))
 	ORDER BY w.the_geom <-> ST_GeometryFromText('{t_geom}',4326) LIMIT 1) as ways2
 	JOIN ways_vertices_pgr as v
 	ON (v.id = ways2.id)
 	ORDER BY v.the_geom <-> ST_GeometryFromText('{t_geom}',4326) LIMIT 1
    '''
    target = fetch_all(pool, t_query)[0]
    print(target['id'])
    route_query = f'''
    SELECT ST_UNION(b.the_geom) AS geojson, SUM(b.length_m) AS length
FROM
(SELECT
*
FROM
    pgr_nogo_astar(
        'SELECT gid AS id, source, target, cost, reverse_cost, x1, y1, x2, y2, the_geom AS geom FROM ways',
        (SELECT string_agg(ST_COLLECT(hgis_hydrology_polylines.shape, hgis_admin3.shape),'') FROM {",".join(nogo_layer)} {nogo_layer_query}),
        {source['id']},
        {target['id']},
        TRUE,
        5,
        1.0,
        1.0
    )) s
LEFT JOIN ways b
ON (b.gid = s.edge)
WHERE the_geom is not NULL'''
    route = fetch_all(pool, route_query)[0]
    return route['geojson'], route['length']

#print(route_nogo('hgis_admin3', 36.79718, -1.24822, 36.730310, -1.216682, "WHERE adm3_name = 'Kitisuru'"))


## avoid points
def route_nogo_withindistance(nogo_layer, long_s, lat_s, long_t, lat_t, nogo_layer_query=""):
    s_geom = 'POINT({} {})'.format(long_s, lat_s)
    t_geom = 'POINT({} {})'.format(long_t, lat_t)

    s_query = "SELECT id FROM ways_vertices_pgr ORDER BY the_geom <-> ST_GeometryFromText('{}',4326) LIMIT 1".format(s_geom)
    source = fetch_all(pool, s_query)[0]
    print(source['id'])
    t_query = "SELECT id FROM ways_vertices_pgr ORDER BY the_geom <-> ST_GeometryFromText('{}',4326) LIMIT 1".format(t_geom)
    target = fetch_all(pool, t_query)[0]
    print(target['id'])
    route_query = '''
    SELECT ST_UNION(b.the_geom) AS geojson, SUM(b.length_m) AS length
FROM
(SELECT
*
FROM
    pgr_nogo_withindistance_astar(
        'SELECT gid AS id, source, target, cost, reverse_cost, x1, y1, x2, y2, the_geom AS geom FROM ways',
        (SELECT ST_UNION(shape) FROM {} {}),
        {},
        {},
        TRUE,
        5,
        1.0,
        1.0
    )) s
LEFT JOIN ways b
ON (b.gid = s.edge)
WHERE the_geom is not NULL'''.format(nogo_layer, nogo_layer_query, source['id'], target['id'])
    route = fetch_all(pool, route_query)[0]
    return route['geojson'], route['length']

# print(route_nogo_withindistance('hgis_bridges_tunnels', 36.7749665,-1.2681415, 36.730310, -1.216682))

print(route_nogo(['hgis_hydrology_polylines', 'hgis_admin3'], 36.756149,-1.225946, 36.699016,-1.209493, "WHERE hgis_hydrology_polylines.objectid = 230 OR hgis_hydrology_polylines.objectid = 446 OR hgis_admin3.adm3_name = 'Kitisuru'"))