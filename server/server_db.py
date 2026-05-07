import os

import psycopg2


def get_db_connection():
    """Create and return a database connection using credentials file"""
    try:
        cred_file = os.path.join(os.path.dirname(__file__), "db.credentials")
        with open(cred_file, 'r') as f:
            connection_string = f.read().strip()
        return psycopg2.connect(connection_string)
    except Exception as e:
        raise Exception(f"Database connection error: {str(e)}")
