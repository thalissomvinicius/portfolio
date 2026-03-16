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

def list_pessoas_cols():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 0 * FROM Pessoas")
    cols = [column[0] for column in cursor.description]
    print("\nCOLUNAS PESSOAS:")
    for c in cols:
        print(f" - {c}")
    conn.close()

if __name__ == "__main__":
    list_pessoas_cols()
