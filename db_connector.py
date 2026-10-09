"""
db_connector.py
----------------
Handles all MySQL connectivity for the project.

Two connection styles are provided:
  1. get_connection()  -> raw mysql.connector connection (good for cursor-based
     INSERT/UPDATE/DDL statements, e.g. running the .sql schema files).
  2. get_engine()      -> SQLAlchemy engine (required by pandas.read_sql /
     DataFrame.to_sql for fast bulk read/write).
"""

import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from src.config import DB_CONFIG


def get_connection():
    """Return a live mysql.connector connection. Caller is responsible for closing it."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
        )
        if conn.is_connected():
            return conn
    except Error as e:
        raise ConnectionError(f"Could not connect to MySQL: {e}") from e


def get_engine():
    """Return a SQLAlchemy engine for use with pandas.read_sql()/to_sql().

    Uses mysql-connector-python as the driver (not PyMySQL) because it has
    proven more reliable on some Windows setups where PyMySQL's socket
    resolution can fail with 'getaddrinfo failed' even for 127.0.0.1
    (usually caused by VPN/antivirus network filtering or IPv6 quirks).

    Builds the connection with sqlalchemy.engine.URL.create() instead of a
    raw f-string: this safely percent-encodes special characters (@, :, /,
    #, etc.) in the username/password. A raw f-string breaks if your MySQL
    password contains an '@' -- it gets misread as the start of the host,
    producing errors like "Unknown MySQL server host 'yourpassword@127.0.0.1'".
    """
    url = URL.create(
        drivername="mysql+mysqlconnector",
        username=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
    )
    return create_engine(url, pool_pre_ping=True)


def run_query(sql, params=None):
    """Convenience helper: run a SELECT and return a pandas DataFrame."""
    import pandas as pd
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(sql, conn, params=params)


def execute_script(sql_text):
    """Run a multi-statement .sql script (schema creation, etc.) via a raw connection."""
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    cursor = conn.cursor()
    for statement in sql_text.split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    # Quick connectivity smoke test: run `python -m src.db_connector`
    try:
        conn = get_connection()
        print("Connected to MySQL successfully:", conn.is_connected())
        conn.close()
    except ConnectionError as e:
        print(e)
