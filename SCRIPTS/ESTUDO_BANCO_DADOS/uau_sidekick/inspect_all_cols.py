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

def inspect_columns(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
        columns = [column[0] for column in cursor.description]
        print(f"\nColunas de {table_name}: {columns}")
        return columns
    except Exception as e:
        print(f"Erro ao inspecionar {table_name}: {e}")
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_columns("Vendas")
    inspect_columns("ContratoVenda")
    inspect_columns("Lotes")
    inspect_columns("Pessoas")
