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
def route_nogo(nogo_layers_list, long_s, lat_s, long_t, lat_t, nogo_layer_query_list="", nogo_pt_buff=.0005, nogo_ln_buff=.0001, nogo_cost='INFINITY', noise=0):
    s_geom = 'POINT({} {})'.format(long_s, lat_s)
    t_geom = 'POINT({} {})'.format(long_t, lat_t)

    # GET NOGO LAYER GEOMETRY AND CREATE nogo_query
    nogo_dict = dict(zip(nogo_layers_list, nogo_layer_query_list))
    nogo_query = "SELECT ST_GEOMFROMEWKT(ST_COLLECT(a.shape)) FROM (SELECT "
    for key, value in nogo_dict.items():
        geom_query = f"SELECT f_geometry_column, type FROM geometry_columns WHERE f_table_name = '{key}'"
        geom_field = fetch_all(pool, geom_query)[0]
        geom_type = geom_field['type']
        geom_colname = geom_field['f_geometry_column']
        if geom_type == "POINT":
            layer = f'ST_FORCE2D(ST_BUFFER({geom_colname}, {nogo_pt_buff})) as shape FROM {key}'
        elif geom_type == "MULTILINESTRING":
            layer = f'ST_FORCE2D(ST_BUFFER({geom_colname}, {nogo_ln_buff})) as shape FROM {key}'
        else:
            layer = f'ST_FORCE2D({geom_colname}) as shape FROM {key}'
        nogo_query += layer
        if value != "":
            nogo_query += f" WHERE {value}"
        else:
            pass
        if key != nogo_layers_list[-1]:
            nogo_query += " UNION SELECT "
        else:
            nogo_query += ") as a"

    print("NOGO QUERY: ", nogo_query)

    # GET STARTING POINT
    # s_query = f"SELECT id FROM ways_vertices_pgr ORDER BY the_geom <-> ST_GeometryFromText('{s_geom}',4326) LIMIT 1"
    s_query = f'''
 	SELECT v.id FROM (SELECT UNNEST(array[w.source, w.target]) as id, w.the_geom FROM ways as w WHERE NOT
	ST_INTERSECTS(w.the_geom, ({nogo_query}))
 	ORDER BY w.the_geom <-> ST_GeometryFromText('{s_geom}',4326) LIMIT 1) as ways2
 	JOIN ways_vertices_pgr as v
 	ON (v.id = ways2.id)
 	ORDER BY v.the_geom <-> ST_GeometryFromText('{s_geom}',4326) LIMIT 1
    '''
    source = fetch_all(pool, s_query)[0]
    print("START NODE: ", source['id'])

    # GET ENDING POINT
    #t_query = f"SELECT id FROM ways_vertices_pgr ORDER BY the_geom <-> ST_GeometryFromText('{t_geom}',4326) LIMIT 1"
    t_query = f'''
 	SELECT v.id FROM (SELECT UNNEST(array[w.source, w.target]) as id, w.the_geom FROM ways as w WHERE NOT
	ST_INTERSECTS(w.the_geom, ({nogo_query}))
 	ORDER BY w.the_geom <-> ST_GeometryFromText('{t_geom}',4326) LIMIT 1) as ways2
 	JOIN ways_vertices_pgr as v
 	ON (v.id = ways2.id)
 	ORDER BY v.the_geom <-> ST_GeometryFromText('{t_geom}',4326) LIMIT 1
    '''
    target = fetch_all(pool, t_query)[0]
    print("END NODE: ", target['id'])

    # GET ROUTE
    route_query = f'''
    SELECT ST_ASTEXT(ST_UNION(b.the_geom)) AS geojson, SUM(b.length_m) AS length
FROM
(SELECT
*
FROM
    pgr_nogo_dijkstra_random(
        'SELECT gid AS id, source, target, cost, reverse_cost, the_geom as geom FROM ways',
        {noise},
        ({nogo_query}),
        {nogo_cost},
        {source['id']},
        {target['id']},
        TRUE
    )) s
LEFT JOIN ways b
ON (b.gid = s.edge)
WHERE the_geom is not NULL'''
    route = fetch_all(pool, route_query)[0]
    print("LENGTH: ", route['length'])
    return [route['geojson'], route['length']]

## standard route with no obstacles
def route_standard(long_s, lat_s, long_t, lat_t, noise=0):
    s_geom = 'POINT({} {})'.format(long_s, lat_s)
    t_geom = 'POINT({} {})'.format(long_t, lat_t)

    # GET STARTING POINT
    s_query = f'''
     	SELECT v.id FROM (SELECT UNNEST(array[w.source, w.target]) as id, w.the_geom FROM ways as w
     	ORDER BY w.the_geom <-> ST_GeometryFromText('{s_geom}',4326) LIMIT 1) as ways2
     	JOIN ways_vertices_pgr as v
     	ON (v.id = ways2.id)
     	ORDER BY v.the_geom <-> ST_GeometryFromText('{s_geom}',4326) LIMIT 1
        '''
    source = fetch_all(pool, s_query)[0]
    print("START NODE: ", source['id'])

    # GET ENDING POINT
    # t_query = f"SELECT id FROM ways_vertices_pgr ORDER BY the_geom <-> ST_GeometryFromText('{t_geom}',4326) LIMIT 1"
    t_query = f'''
     	SELECT v.id FROM (SELECT UNNEST(array[w.source, w.target]) as id, w.the_geom FROM ways as w
     	ORDER BY w.the_geom <-> ST_GeometryFromText('{t_geom}',4326) LIMIT 1) as ways2
     	JOIN ways_vertices_pgr as v
     	ON (v.id = ways2.id)
     	ORDER BY v.the_geom <-> ST_GeometryFromText('{t_geom}',4326) LIMIT 1
        '''
    target = fetch_all(pool, t_query)[0]
    print("END NODE: ", target['id'])

    route_query = f'''
    SELECT ST_ASTEXT(ST_UNION(b.the_geom)) AS geojson, SUM(b.length_m) AS length
FROM
(SELECT
*
FROM
    pgr_dijkstra_random(
        'SELECT gid AS id, source, target, cost, reverse_cost FROM ways',
        {noise},
        {source['id']},
        {target['id']},
        TRUE
    )) s
LEFT JOIN ways b
ON (b.gid = s.edge)
WHERE the_geom is not NULL'''
    route = fetch_all(pool, route_query)[0]
    print("LENGTH: ", route['length'])
    return [route['geojson'], route['length']]

#print(route_nogo(['hgis_admin3', 'hgis_bridges_tunnels'], 36.751293, -1.271346, 36.726833, -1.190509, ["hgis_admin3.adm3_name = 'Kitisuru'", "hgis_bridges_tunnels.objectid = 810 OR hgis_bridges_tunnels.objectid = 811"]))
# print(route_standard(36.751293, -1.271346, 36.726833, -1.190509))