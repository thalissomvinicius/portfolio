import pyodbc

SERVER = 'DCWBD11\\VALLEPRIME_PRD'
DATABASE = 'UAU-VALLEPRIME'
UID = 'consultasBD'
PWD = 'V@lle#2021'

connection_string = f"Driver={{SQL Server}};Server={SERVER};Database={DATABASE};UID={UID};PWD={PWD};"

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    print("CONNECTED!")

    # Get columns of Vendas table
    key_tables = ['Vendas', 'VendaClientes', 'VendaClienteHist', 'VendasIntermediaria']
    for table in key_tables:
        print(f"\n=== COLUNAS: {table} ===")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, (table,))
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                print(f"  {r[0]} ({r[1]})")
        else:
            print("  (tabela nao encontrada ou vazia)")

    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
