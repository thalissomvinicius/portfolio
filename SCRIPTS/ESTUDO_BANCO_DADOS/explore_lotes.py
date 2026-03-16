import pyodbc

SERVER = 'DCWBD11\\VALLEPRIME_PRD'
DATABASE = 'UAU-VALLEPRIME'
UID = 'consultasBD'
PWD = 'V@lle#2021'

connection_string = f"Driver={{SQL Server}};Server={SERVER};Database={DATABASE};UID={UID};PWD={PWD};"

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    key_tables = ['Contratos', 'ProdutoContrato', 'Produtos', 'Lotes', 'CadastroEmpreendimento', 'LotesProducao']
    
    print("Verificando existencia de tabelas de lote/produto:")
    for table_prefix in ['Contrato', 'Produto', 'Lote']:
        cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_NAME LIKE '{table_prefix}%'")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"  {table_prefix}*: {tables[:10]}...")

    print("\nObtendo colunas para tabelas mais provaveis...")
    for table in ['Contratos', 'ProdutoContrato', 'Produtos', 'Lotes', 'CadastroEmpreendimento']:
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", (table,))
        rows = cursor.fetchall()
        if rows:
            print(f"\n=== COLUNAS: {table} ===")
            for r in rows:
                if any(k in r[0].lower() for k in ['quadra', 'lote', 'area', 'frente', 'fundo', 'lado', 'chanfro']):
                    print(f"  --> {r[0]} ({r[1]})")
                elif 'cod' in r[0].lower() or 'num' in r[0].lower() or 'id' in r[0].lower():
                    print(f"  {r[0]} ({r[1]})")

    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
