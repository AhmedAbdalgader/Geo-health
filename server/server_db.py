import os

import psycopg2
from psycopg2.pool import ThreadedConnectionPool


_connection_pool = None


def init_db_pool(minconn=1, maxconn=10):
    """Initialize the shared PostgreSQL connection pool once."""
    global _connection_pool

    if _connection_pool is not None:
        return _connection_pool

    cred_file = os.path.join(os.path.dirname(__file__), "db.credentials")
    with open(cred_file, 'r') as f:
        connection_string = f.read().strip()

    _connection_pool = ThreadedConnectionPool(minconn, maxconn, connection_string)
    return _connection_pool


def get_db_connection():
    """Borrow one PostgreSQL connection from the shared pool.
        The caller should close the connection when finished; with psycopg2 pool
        connections, close() returns the connection to the pool instead of tearing
        down the database connection.
    """
    try:
        pool = init_db_pool()
        return pool.getconn()
    except Exception as e:
        raise Exception(f"Database connection error: {str(e)}")
