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

def deep_search():
    conn = get_conn()
    cursor = conn.cursor()
    
    # Search for any table associated with a Person ID that has columns for address
    print("\n--- BUSCANDO TABELAS DE ENDEREÇO/COMPLEMENTO ---")
    cursor.execute("""
        SELECT DISTINCT TABLE_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE COLUMN_NAME LIKE '%End%' OR COLUMN_NAME LIKE '%Bairro%' OR COLUMN_NAME LIKE '%Cidade%'
    """)
    tables = [r[0] for r in cursor.fetchall()]
    print(f"  Tabelas que podem conter endereço: {tables[:15]}...")

    # Search for Civil Status / Marriage fields
    print("\n--- BUSCANDO ESTADO CIVIL / REGIME BENS ---")
    cursor.execute("""
        SELECT DISTINCT TABLE_NAME, COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE COLUMN_NAME LIKE '%Civil%' OR COLUMN_NAME LIKE '%Regime%' OR COLUMN_NAME LIKE '%Conjuge%'
    """)
    for r in cursor.fetchall():
        print(f"  Table: {r[0]} | Column: {r[1]}")

    # Search for Lot details specifically
    print("\n--- BUSCANDO DETALHES DO LOTE (MATRICULA, FOLHA) ---")
    cursor.execute("""
        SELECT DISTINCT TABLE_NAME, COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE COLUMN_NAME LIKE '%Matricula%' OR COLUMN_NAME LIKE '%Folha%' OR COLUMN_NAME LIKE '%Livro%'
    """)
    for r in cursor.fetchall():
        if not any(x in r[0].lower() for x in ['calc', 'func', 'folha']): # Filter out payroll stuff
            print(f"  Table: {r[0]} | Column: {r[1]}")

    conn.close()

if __name__ == "__main__":
    deep_search()
