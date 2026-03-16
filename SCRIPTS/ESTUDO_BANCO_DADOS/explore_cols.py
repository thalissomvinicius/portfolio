import pyodbc

SERVER = 'DCWBD11\\VALLEPRIME_PRD'
DATABASE = 'UAU-VALLEPRIME'
UID = 'consultasBD'
PWD = 'V@lle#2021'

connection_string = f"Driver={{SQL Server}};Server={SERVER};Database={DATABASE};UID={UID};PWD={PWD};"

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    print("=== BUSCANDO COLUNAS COM PALAVRAS-CHAVE ===")
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE LOWER(COLUMN_NAME) LIKE '%frente%' 
           OR LOWER(COLUMN_NAME) LIKE '%fundo%'
           OR LOWER(COLUMN_NAME) LIKE '%lado%'
           OR LOWER(COLUMN_NAME) LIKE '%chanfro%'
           OR LOWER(COLUMN_NAME) LIKE '%area%'
           OR LOWER(COLUMN_NAME) LIKE '%quadra%'
        ORDER BY TABLE_NAME
    """)
    rows = cursor.fetchall()

    tables = {}
    for r in rows:
        tname, cname, dtype = r
        if tname not in tables:
            tables[tname] = []
        tables[tname].append(f"{cname} ({dtype})")
        
    for tname, cols in tables.items():
        if "Historico" not in tname and "Hist" not in tname and "BKP" not in tname:
            print(f"\n[{tname}]")
            for c in cols:
                print(f"  {c}")

    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
