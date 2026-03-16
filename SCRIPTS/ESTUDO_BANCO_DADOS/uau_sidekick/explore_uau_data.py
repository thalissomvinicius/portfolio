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

def search_example_data():
    conn = get_conn()
    cursor = conn.cursor()

    # Search for Comprador
    print("\n--- PESQUISANDO CLIENTE: JALDECY PANCIERI ---")
    cursor.execute("SELECT TOP 5 * FROM Pessoa WHERE Nome_pes LIKE '%JALDECY PANCIERI%'")
    rows = cursor.fetchall()
    cols = [column[0] for column in cursor.description]
    for row in rows:
        for i, val in enumerate(row):
            print(f"  {cols[i]}: {val}")

    # Search for Contrato 284
    print("\n--- PESQUISANDO CONTRATO: 284 ---")
    # Trying different table names if 'Contratos' is not exact
    try:
        cursor.execute("SELECT TOP 1 * FROM Contratos WHERE Num_con = 284")
        rows = cursor.fetchall()
        cols = [column[0] for column in cursor.description]
        for row in rows:
            for i, val in enumerate(row):
                print(f"  {cols[i]}: {val}")
    except Exception as e:
        print(f"Contratos table error: {e}")

    # Search for Venda of this client
    print("\n--- PESQUISANDO VENDAS DO CLIENTE ---")
    try:
        cursor.execute("""
            SELECT TOP 5 v.* 
            FROM Vendas v
            JOIN Pessoa p ON v.Cod_cli = p.Cod_pes
            WHERE p.Nome_pes LIKE '%JALDECY PANCIERI%'
        """)
        rows = cursor.fetchall()
        cols = [column[0] for column in cursor.description]
        for row in rows:
            print(f"\n  Venda ID: {row[0]}")
            for i, val in enumerate(row):
                print(f"    {cols[i]}: {val}")
    except Exception as e:
        print(f"Vendas table error: {e}")

    conn.close()

if __name__ == "__main__":
    search_example_data()
