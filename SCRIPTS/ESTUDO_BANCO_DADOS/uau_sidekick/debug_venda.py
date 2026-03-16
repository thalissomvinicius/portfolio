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

def debug_sale():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    venda_id = 3680
    empresa = 6
    obra = 70400
    
    print(f"Buscando Venda {venda_id}, Empresa {empresa}, Obra {obra}...")
    
    # 1. Testar query simples
    cursor.execute("SELECT * FROM Vendas WHERE Num_Ven = ? AND Empresa_Ven = ? AND Obra_Ven = ?", (venda_id, empresa, obra))
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        print("\n[Vendas] Encontrada!")
        print(dict(zip(columns, row)))
    else:
        print("\n[Vendas] NÃO ENCONTRADA com os 3 parâmetros.")
        # Tentar apenas por Num_Ven
        cursor.execute("SELECT Empresa_Ven, Obra_Ven FROM Vendas WHERE Num_Ven = ?", (venda_id,))
        rows = cursor.fetchall()
        print(f"Vendas com Num_Ven {venda_id}: {rows}")

    # 2. Verificar o JOIN que falhou no database.py
    sql_fail = """
    SELECT 
        v.Num_Ven,
        p.Nome_Pes
    FROM Vendas v
    JOIN Pessoas p ON v.Cliente_Ven = p.Cod_Pes
    LEFT JOIN ContratoVenda cv ON v.Num_Ven = cv.Num_Ven AND v.Empresa_Ven = cv.Empresa_Ven
    WHERE v.Num_Ven = ? AND v.Empresa_Ven = ? AND v.Obra_Ven = ?
    """
    try:
        cursor.execute(sql_fail, (venda_id, empresa, obra))
        row = cursor.fetchone()
        if row:
            print("\n[JOIN Simples] Sucesso!")
        else:
            print("\n[JOIN Simples] Falhou (nada retornado).")
    except Exception as e:
        print(f"\n[JOIN Simples] Erro: {e}")

    conn.close()

if __name__ == "__main__":
    debug_sale()
