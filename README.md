# README

```docker-compose up -d```

Once you have started a database container, you can then connect to the
database as follows:

```bash
$ docker run -it --link xlab_routingproject_xlab-routing_1:postgres --rm postgres \
  sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres'
```

osm overpass api

```http://overpass-api.de/api/map?way[bbox=36.15491910500003,-1.6056902019999484,37.914263872000035,0.2048727530000518][highway=*]```


osm2pgrouting configs

```
$ cd osm2pgrouting/
$ osm2pgrouting -f ../data/osmc.osm -h localhost -U postgres -W postgres -d xlab-routing --conf=mapconfig_for_cars.xml
```
