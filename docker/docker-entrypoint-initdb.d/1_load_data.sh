set -e

pg_restore -d xlab-routing -U postgres /docker-entrypoint-initdb.d/nairobi-routing.dump
