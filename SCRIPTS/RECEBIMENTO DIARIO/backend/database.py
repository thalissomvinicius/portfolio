import os
import pyodbc
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_db_connection() -> Optional[pyodbc.Connection]:
    """
    Establishes a connection to the SQL Server database.
    """
    try:
        connection_string = (
            "Driver={SQL Server};"
            f"Server={os.getenv('DB_SERVER', 'DCWBD11\\VALLEPRIME_PRD')};"
            f"Database={os.getenv('DB_DATABASE', 'UAU-VALLEPRIME')};"
            f"UID={os.getenv('DB_UID', 'consultasBD')};"
            f"PWD={os.getenv('DB_PWD', 'V@lle#2021')};"
            "Timeout=30;"
        )
        
        conn = pyodbc.connect(connection_string)
        return conn
        
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {e}")
        return None
