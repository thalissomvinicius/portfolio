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

def inspect_itens_venda():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n--- Colunas de ItensVenda ---")
    cursor.execute("SELECT TOP 0 * FROM ItensVenda")
    cols = [column[0] for column in cursor.description]
    print(cols)
    
    # Ver FKs de ItensVenda
    sql_fk = """
    SELECT 
        tab1.name AS [TABLE_NAME],
        col1.name AS [COLUMN_NAME],
        tab2.name AS [REFERENCED_TABLE_NAME],
        col2.name AS [REFERENCED_COLUMN_NAME]
    FROM sys.foreign_key_columns fkc
    INNER JOIN sys.tables tab1 ON tab1.object_id = fkc.parent_object_id
    INNER JOIN sys.columns col1 ON col1.column_id = parent_column_id AND col1.object_id = tab1.object_id
    INNER JOIN sys.tables tab2 ON tab2.object_id = fkc.referenced_object_id
    INNER JOIN sys.columns col2 ON col2.column_id = referenced_column_id AND col2.object_id = tab2.object_id
    WHERE tab1.name = 'ItensVenda'
    """
    print("\n--- FKs de ItensVenda ---")
    cursor.execute(sql_fk)
    for r in cursor.fetchall():
        print(f"  {r.COLUMN_NAME} -> {r.REFERENCED_TABLE_NAME}.{r.REFERENCED_COLUMN_NAME}")

    conn.close()

if __name__ == "__main__":
    inspect_itens_venda()
