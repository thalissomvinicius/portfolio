import pyodbc

DB_CONFIG = {
    "driver": "SQL Server",
    "server": "DCWBD11\\VALLEPRIME_PRD",
    "database": "UAU-VALLEPRIME",
    "uid": "consultasBD",
    "pwd": "V@lle#2021"
}

def check_more_marriages():
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
        
        # Search for any client with RegCasamento != 0
        cursor.execute("SELECT TOP 10 cod_pf, estciv_pf, RegCasamento_pf FROM PesFis WITH(NOLOCK) WHERE RegCasamento_pf <> 0")
        rows = cursor.fetchall()
        print("Clients with RegCasamento != 0:")
        for r in rows:
            print(f" Cod: {r[0]}, EstCiv: {r[1]}, RegCasamento: {r[2]}")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_more_marriages()
