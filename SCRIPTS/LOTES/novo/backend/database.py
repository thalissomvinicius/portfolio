"""
VallePrime Dashboard - FastAPI Backend
Database connection module
"""

import pyodbc
import os
from typing import Optional
from contextlib import contextmanager

# Database configuration
# Database configuration
DB_CONFIG = {
    "driver": os.getenv('DB_DRIVER', "SQL Server"),
    "server": os.getenv('DB_SERVER', 'DCWBD11\\VALLEPRIME_PRD'),
    "database": os.getenv('DB_DATABASE', 'UAU-VALLEPRIME'),
    "uid": os.getenv('DB_UID', 'consultasBD'),
    "pwd": os.getenv('DB_PWD', 'V@lle#2021'),
    "port": os.getenv('DB_PORT', ''),  # Optional port override
    "timeout": 30
}

def get_connection_string() -> str:
    """Build connection string from config"""
    # Handle port in server string if provided
    server = DB_CONFIG['server']
    if DB_CONFIG['port']:
        # If server already has comma, assume it might be specifying something else, but standard is server,port
        if ',' not in server:
             server = f"{server},{DB_CONFIG['port']}"
    
    return (
        f"Driver={{{DB_CONFIG['driver']}}};"
        f"Server={server};"
        f"Database={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['uid']};"
        f"PWD={DB_CONFIG['pwd']};"
        f"Timeout={DB_CONFIG['timeout']};"
    )

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = pyodbc.connect(get_connection_string())
        yield conn
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: Optional[tuple] = None) -> list:
    """Execute a query and return results as list of dicts"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results

def execute_query_df(query: str, params: Optional[tuple] = None):
    """Execute a query and return results as pandas DataFrame"""
    import pandas as pd
    with get_db_connection() as conn:
        if params:
            return pd.read_sql(query, conn, params=params)
        else:
            return pd.read_sql(query, conn)
