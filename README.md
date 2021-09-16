# PGRouting 
<br />

## Docker (if building local database)

##### Run docker-compose

```
cd docker-xlab-routing
docker-compose up -d
```

##### Connect to database container

```bash
$ docker run -it --link xlab_routingproject_xlab-routing_1:postgres --rm postgres \
  sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres'
```
<br />

## Connect to existing database

##### Connect to RDS database

```
$ psql --host=*******.us-east-1.rds.amazonaws.com --username=****** --dbname=routing

```

##### Download osm data with osm overpass api (kenya aoi)

```
http://overpass-api.de/api/map?way[bbox=36.15491910500003,-1.6056902019999484, 
37.914263872000035,0.2048727530000518][highway=*]
```

##### Prepare and upload osm data with osm2pgrouting 

```
$ cd osm2pgrouting/
$ osm2pgrouting -f ../data/kenya_clip.osm -h *******.us-east-1.rds.amazonaws.com -U **** -W **** -d routing --conf=../data/mapconfig_for_cars.xml
```
