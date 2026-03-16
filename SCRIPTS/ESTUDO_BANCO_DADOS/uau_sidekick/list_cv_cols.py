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

def list_cv_cols():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 0 * FROM ContratoVenda")
    cols = [column[0] for column in cursor.description]
    print("\nCOLUNAS CONTRATOVENDA:")
    for c in cols:
        print(c)
    conn.close()

if __name__ == "__main__":
    list_cv_cols()
