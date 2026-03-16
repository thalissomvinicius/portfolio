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

def find_specifics():
    conn = get_conn()
    cursor = conn.cursor()
    
    # Common UAU tables for personal extra info
    # Usually: PessoasFisicas, PessoasJuridicas, EndPessoas, etc.
    tables_to_check = ['PessoasFisicas', 'PessoasJuridicas', 'Enderecos', 'PessoasEnderecos', 'ComplementoPessoas']
    
    print("\n--- VERIFICANDO TABELAS ADICIONAIS ---")
    for t in tables_to_check:
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?", (t,))
        if cursor.fetchone()[0] > 0:
            print(f"  [+] Encontrada: {t}")
            cursor.execute(f"SELECT TOP 1 * FROM {t}")
            cols = [column[0] for column in cursor.description]
            print(f"      Colunas: {cols[:10]}...")
        else:
            print(f"  [-] Nao encontrada: {t}")

    # Search for Marital Status (Estado Civil)
    print("\n--- BUSCANDO ESTADO CIVIL ---")
    cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME LIKE '%Est%Civil%' OR COLUMN_NAME LIKE '%Reg%Bens%'")
    for r in cursor.fetchall():
        print(f"  {r[0]} -> {r[1]}")

    conn.close()

if __name__ == "__main__":
    find_specifics()
