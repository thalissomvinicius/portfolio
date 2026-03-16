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

def inspect_pessoas():
    conn = get_conn()
    cursor = conn.cursor()
    
    print("\n--- COLUNAS: Pessoas ---")
    cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Pessoas' ORDER BY ORDINAL_POSITION")
    for r in cursor.fetchall():
        print(f"  {r[0]} ({r[1]})")

    print("\n--- BUSCANDO JALDECY NA Pessoas ---")
    cursor.execute("SELECT TOP 1 * FROM Pessoas WHERE Nome_pes LIKE '%JALDECY PANCIERI%'")
    row = cursor.fetchone()
    if row:
        cols = [column[0] for column in cursor.description]
        for i, val in enumerate(row):
            print(f"  {cols[i]}: {val}")
    else:
        print("  Client not found.")

    conn.close()

if __name__ == "__main__":
    inspect_pessoas()
