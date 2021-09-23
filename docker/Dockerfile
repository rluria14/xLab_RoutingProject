FROM postgis/postgis
MAINTAINER Hans Kristian Flaatten <hans@starefossen.com>

ENV PGROUTING_MAJOR 2.5
ENV PGROUTING_VERSION 2.5.2

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wget \
      postgresql-13-pgrouting && \
    rm -rf /var/lib/apt/lists/*

COPY ./docker-entrypoint-initdb.d/0_initdb-pgrouting.sh /docker-entrypoint-initdb.d/0_routing.sh
COPY ./docker-entrypoint-initdb.d/1_load_data.sh /docker-entrypoint-initdb.d/1_load_data.sh
COPY ./docker-entrypoint-initdb.d/nairobi-routing.dump /docker-entrypoint-initdb.d/nairobi-routing.dump