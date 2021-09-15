# README

```docker-compose up -d```

Once you have started a database container, you can then connect to the
database as follows:

```bash
$ docker run -it --link xlab_routingproject_xlab-routing_1:postgres --rm postgres \
  sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres'
```

osm2pgrouting configs

```
cd osm2pgrouting/
$ osm2pgrouting -f ../data/osmc.osm -h localhost -U postgres -W postgres -d xlab-routing --conf=../data/mapconfig_for_cars.xml
```