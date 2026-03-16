import pyodbc

DB_CONFIG = {
    'server': 'DCWBD11\\VALLEPRIME_PRD',
    'database': 'UAU-VALLEPRIME',
    'uid': 'consultasBD',
    'pwd': 'V@lle#2021'
}

def get_db_connection():
    conn_str = f"Driver={{SQL Server}};Server={DB_CONFIG['server']};Database={DB_CONFIG['database']};UID={DB_CONFIG['uid']};PWD={DB_CONFIG['pwd']};"
    return pyodbc.connect(conn_str)

def inspect_prdsrv():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n--- Colunas de PrdSrv ---")
    cursor.execute("SELECT TOP 1 * FROM PrdSrv")
    cols = [column[0] for column in cursor.description]
    row = cursor.fetchone()
    if row:
        print(dict(zip(cols, row)))
    else:
        print(cols)

    conn.close()

if __name__ == "__main__":
    inspect_prdsrv()
