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

def list_all_cols(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT TOP 0 * FROM {table_name}")
    columns = [column[0] for column in cursor.description]
    print(f"\nTABLE: {table_name}")
    print(columns)
    conn.close()

if __name__ == "__main__":
    list_all_cols("Vendas")
    list_all_cols("ContratoVenda")
    list_all_cols("Lotes")
    list_all_cols("Pessoas")
