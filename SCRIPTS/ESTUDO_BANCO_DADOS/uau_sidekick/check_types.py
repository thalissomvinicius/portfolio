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

def check_types(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT TOP 0 * FROM {table_name}")
    print(f"\nTABLE: {table_name}")
    for col in cursor.description:
        print(f" - {col[0]}: {col[1]}") # col[1] is the type
    conn.close()

if __name__ == "__main__":
    check_types("Vendas")
    check_types("ContratoVenda")
    check_types("ItensVenda")
    check_types("Unidade")
