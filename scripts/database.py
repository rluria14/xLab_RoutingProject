import logging

from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

logger = logging.getLogger()


def get_conn_pool(config):
    logger.info(
        "Creating DB connection pool with settings: %r",
        {**config, **{"password": "*****"}},
    )
    db_pool = SimpleConnectionPool(1, 4, **config)
    return db_pool


def execute(pool, statement, *args):
    try:
        with pool.getconn() as db_conn:
            with db_conn.cursor() as curs:
                curs.execute(statement, *args)
    finally:
        pool.putconn(db_conn)


def fetch_all(pool, statement, *args):
    try:
        with pool.getconn() as db_conn:
            with db_conn.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute(statement, *args)
                record = curs.fetchall()
    finally:
        pool.putconn(db_conn)
    return record
