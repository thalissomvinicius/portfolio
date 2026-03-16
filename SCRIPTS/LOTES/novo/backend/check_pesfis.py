import pyodbc

DB_CONFIG = {
    "driver": "SQL Server",
    "server": "DCWBD11\\VALLEPRIME_PRD",
    "database": "UAU-VALLEPRIME",
    "uid": "consultasBD",
    "pwd": "V@lle#2021"
}

def check_pesfis_structure():
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
        
        print("COLUMNS IN PesFis:")
        cursor.execute("SELECT TOP 1 * FROM PesFis WITH(NOLOCK)")
        cols = [c[0] for c in cursor.description]
        print(cols)
        
        # Search for marital status code mapping in some table
        print("\nSearching for any column named 'EstCivil' or similar...")
        cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME LIKE '%EstCivil%'")
        for row in cursor.fetchall():
            print(f" - {row[0]}.{row[1]}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_pesfis_structure()
