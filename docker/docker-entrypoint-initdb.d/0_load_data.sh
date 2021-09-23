set -e

pg_restore -d xlab-routing -U postgres -p 5432 /docker-entrypoint-initdb.d/nairobi-routing.sql
