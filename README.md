# PGRouting 
<br />

##### Run xlab-routing database

```
cd docker
docker-compose up -d
```

##### Exporting the database
If changes have been made to that data like adding tables or data
then the data should be exported with the following
`pg_dump -F t -d xlab-routing -h localhost -U postgres > routing.dump`
with the dump file being placed in the `docker-entrypoint-initdb.d`
directory

##### Refreshing the database
If someone else has made changes to the initial dataset the it can
be imported by the following
1. `docker compose down`
1. `rm -rf ./data/*`
1. `docker compose up -d`

##### Connect to database container via psql cmd line

```bash
$ docker run -it --link xlab_routingproject_xlab-routing_1:postgres --rm postgres \
  sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres'
```

##### Connect to an RDS database

```
$ psql --host=*******.us-east-1.rds.amazonaws.com --username=****** --dbname=routing

```

##### Download osm data with osm overpass api (kenya aoi)

```
http://overpass-api.de/api/xapi?way[bbox=36.15491910500003,-1.6056902019999484, 
37.914263872000035,0.2048727530000518][highway=*]
```

##### Prepare and upload osm data with osm2pgrouting 

```
$ cd osm2pgrouting/
$ osm2pgrouting -f ../data/kenya_clip.osm -h *******.us-east-1.rds.amazonaws.com -U **** -W **** -d routing --conf=../data/mapconfig_for_cars.xml
```
