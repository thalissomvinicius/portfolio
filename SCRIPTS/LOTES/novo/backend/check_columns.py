import pyodbc

DB_CONFIG = {
    "driver": "SQL Server",
    "server": "DCWBD11\\VALLEPRIME_PRD",
    "database": "UAU-VALLEPRIME",
    "uid": "consultasBD",
    "pwd": "V@lle#2021"
}

def check_is_view():
    conn_str = (
        f"Driver={{{DB_CONFIG['driver']}}};"
        f"Server={DB_CONFIG['server']};"
        f"Database={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['uid']};"
        f"PWD={DB_CONFIG['pwd']};"
    )
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Pessoas'")
        row = cursor.fetchone()
        print(f"Pessoas TABLE_TYPE: {row[0] if row else 'NOT FOUND'}")
        
        # Check columns of Pessoas via sys.columns to be thorough
        cursor.execute("""
            SELECT c.name
            FROM sys.columns c
            JOIN sys.objects o ON c.object_id = o.object_id
            WHERE o.name = 'Pessoas'
            ORDER BY c.name
        """)
        print("\nAll columns in sys.columns for Pessoas:")
        for r in cursor.fetchall():
            print(f" - {r[0]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_is_view()
