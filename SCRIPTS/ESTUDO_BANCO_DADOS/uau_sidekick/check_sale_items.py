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

def check_sale_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    venda_id = 3680
    
    print(f"--- Itens da Venda {venda_id} ---")
    cursor.execute("SELECT * FROM ItensVenda WHERE NumVend_Itv = ?", (venda_id,))
    rows = cursor.fetchall()
    cols = [column[0] for column in cursor.description]
    for r in rows:
        print(dict(zip(cols, r)))
    
    # Se Produto_Itv for 103 (exemplo), ver o que é em Unidade ou Predio
    if rows:
        prod_id = rows[0].Produto_Itv
        print(f"\nBuscando Produto/Lote {prod_id}...")
        
        # Tentar em Unidade
        cursor.execute("SELECT * FROM Unidade WHERE Cod_Un = ?", (prod_id,))
        u = cursor.fetchone()
        if u:
            print(f"Encontrado em Unidade: {u}")
        
    conn.close()

if __name__ == "__main__":
    check_sale_items()
