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

def find_lote_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("--- Buscando tabelas de Lotes/Unidades ---")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%Lote%' OR TABLE_NAME LIKE '%Unid%'")
    for r in cursor.fetchall():
        print(f"  [Table] {r[0]}")
    
    # Inspecionar CadastroLote ou Lote se existirem
    target_tables = ['Lote', 'CadastroLote', 'Unidade']
    for t in target_tables:
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?", (t,))
        if cursor.fetchone()[0] > 0:
            print(f"\nColunas de {t}:")
            cursor.execute(f"SELECT TOP 0 * FROM {t}")
            cols = [column[0] for column in cursor.description]
            print(cols)

    conn.close()

if __name__ == "__main__":
    find_lote_tables()
