import pyodbc

DB_CONFIG = {
    "driver": "SQL Server",
    "server": "DCWBD11\\VALLEPRIME_PRD",
    "database": "UAU-VALLEPRIME",
    "uid": "consultasBD",
    "pwd": "V@lle#2021"
}

def debug_venda_final():
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
        
        empresa = 999
        obra = '70100'
        venda = 2
        
        print(f"--- Querying VendaRecClientes for {venda} with CORRECT names ---")
        query = f"""
        SELECT 
            Cliente_vrc, Tipo_vrc, PorcTitular_Vrc 
        FROM VendaRecClientes WITH(NOLOCK) 
        WHERE Empresa_vrc = {empresa} 
          AND Num_Vrc = {venda} 
          AND Obra_Vrc = '{obra}'
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f" Found {len(rows)} clients")
        for r in rows:
            print(f"  Cod: {r[0]}, Tipo: {r[1]}, Porc: {r[2]}")
            
            # Check Pessoas
            cursor.execute(f"SELECT nome_pes FROM Pessoas WITH(NOLOCK) WHERE cod_pes = {r[0]}")
            p = cursor.fetchone()
            print(f"   Nome: {p[0] if p else 'NOT FOUND'}")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_venda_final()
