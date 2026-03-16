import pyodbc

DB_CONFIG = {
    'server': 'DCWBD11\\VALLEPRIME_PRD',
    'database': 'UAU-VALLEPRIME',
    'uid': 'consultasBD',
    'pwd': 'V@lle#2021'
}

def get_conn():
    conn_str = f"Driver={{SQL Server}};Server={DB_CONFIG['server']};Database={DB_CONFIG['database']};UID={DB_CONFIG['uid']};PWD={DB_CONFIG['pwd']};"
    return pyodbc.connect(conn_str)

def find_tables():
    conn = get_conn()
    cursor = conn.cursor()
    
    patterns = ['%PES%', '%CLI%', '%LOT%', '%CON%']
    for p in patterns:
        print(f"\n--- TABLES LIKE {p} ---")
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE ?", (p,))
        tables = [r[0] for r in cursor.fetchall()]
        print(f"  {tables[:20]}...")

    conn.close()

if __name__ == "__main__":
    find_tables()
