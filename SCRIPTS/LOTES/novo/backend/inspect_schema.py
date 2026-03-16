import pyodbc

DB_CONFIG = {
    "driver": "SQL Server",
    "server": "DCWBD11\\VALLEPRIME_PRD",
    "database": "UAU-VALLEPRIME",
    "uid": "consultasBD",
    "pwd": "V@lle#2021"
}

def inspect_all_pes_tables():
    conn_str = (
        f"Driver={{{DB_CONFIG['driver']}}};"
        f"Server={DB_CONFIG['server']};"
        f"Database={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['uid']};"
        f"PWD={DB_CONFIG['pwd']};"
    )
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        tables_to_check = ['VendaClientes', 'VendaRecClientes', 'PesFis', 'PessoasDoc', 'PesConj']
        
        for table in tables_to_check:
            print(f"\n--- TABLE: {table} ---")
            try:
                cursor.execute(f"SELECT TOP 1 * FROM {table} WITH(NOLOCK)")
                cols = [c[0] for c in cursor.description]
                print(f"Columns: {cols}")
                
                # Check sample row for Venda 2 if applicable
                if table in ['VendaClientes', 'VendaRecClientes']:
                    # Try flexible search for empresa/obra/venda
                    emp_col = next((c for c in cols if 'emp' in c.lower()), None)
                    num_col = next((c for c in cols if 'num' in c.lower() and 'ven' in c.lower()), None)
                    obra_col = next((c for c in cols if 'obra' in c.lower()), None)
                    
                    if emp_col and num_col and obra_col:
                        q = f"SELECT * FROM {table} WITH(NOLOCK) WHERE {emp_col} = 999 AND {num_col} = 2 AND {obra_col} = '70100'"
                        cursor.execute(q)
                        rows = cursor.fetchall()
                        print(f"Rows for Venda 2: {len(rows)}")
                        for r in rows:
                            print(f" - {dict(zip(cols, r))}")
            except Exception as e:
                print(f"Error checking {table}: {e}")
                
        # Search for marital status column globally
        print("\n--- Searching for marriage/civil status columns ---")
        cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME LIKE '%Civil%' OR COLUMN_NAME LIKE '%Casam%'")
        for row in cursor.fetchall():
            print(f" - {row[0]}.{row[1]}")

        # Search for RG columns globally
        print("\n--- Searching for RG/Registro/Ident columns ---")
        cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME LIKE '%RG%' OR COLUMN_NAME LIKE '%Regis%'")
        for row in cursor.fetchall():
            if 'Pes' in row[0] or row[0] == 'Pessoas':
                print(f" - {row[0]}.{row[1]}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_all_pes_tables()
