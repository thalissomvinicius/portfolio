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

def get_filters():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscar lista de empresas e obras únicas (usando nome fantasia se disponível)
    # No UAU, CadastroEmpreendimento costuma guardar as obras
    cursor.execute("SELECT DISTINCT Empresa_Ven FROM Vendas")
    empresas = [str(r[0]) for r in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT Obra_Ven FROM Vendas")
    obras = [str(r[0]) for r in cursor.fetchall()]
    
    conn.close()
    return {"empresas": sorted(empresas), "obras": sorted(obras)}

def search_vendas(query_text, empresa_id=None, obra_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Base SQL
    sql = """
    SELECT TOP 50
        v.Num_Ven as id_venda,
        p.Nome_Pes as nome_cliente,
        p.Cpf_Pes as cpf_cliente,
        v.Data_Ven as data_venda,
        v.Empresa_Ven,
        v.Obra_Ven
    FROM Vendas v
    JOIN Pessoas p ON v.Cliente_Ven = p.Cod_Pes
    WHERE (p.Nome_Pes LIKE ? OR CAST(v.Num_Ven AS VARCHAR) LIKE ?)
    """
    
    params = [f"%{query_text}%", f"%{query_text}%"]
    
    if empresa_id:
        sql += " AND v.Empresa_Ven = ?"
        params.append(empresa_id)
    if obra_id:
        sql += " AND v.Obra_Ven = ?"
        params.append(obra_id)
        
    sql += " ORDER BY v.Data_Ven DESC"
    
    cursor.execute(sql, params)
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row.id_venda,
            "cliente": row.nome_cliente,
            "cpf": row.cpf_cliente,
            "data": row.data_venda.strftime("%d/%m/%Y") if row.data_venda else "",
            "empresa": row.Empresa_Ven,
            "obra": row.Obra_Ven
        })
    
    conn.close()
    return results

def get_venda_details(venda_id, empresa, obra):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQL robusto para buscar endereço (ContratoVenda ou Pessoas) e Lote (ItensVenda/Unidade)
    # Buscamos dados em ContratoVenda (cv) e também no cadastro da Pessoa (p) como fallback
    sql = """
    SELECT 
        v.Num_Ven,
        p.Nome_Pes,
        p.Cpf_Pes,
        p.DtNasc_Pes,
        v.Data_Ven,
        v.ValorTot_Ven,
        -- Endereço da Venda
        cv.EnderEntrega_conv as ender_conv,
        cv.SetorEntrega_conv as bairro_conv,
        cv.CidadeEntrega_conv as cidade_conv,
        cv.UfEntrega_conv as uf_conv,
        cv.CepEntrega_conv as cep_conv,
        -- Lote/Unidade
        u.Descricao_Un as desc_lote
    FROM Vendas v
    JOIN Pessoas p ON v.Cliente_Ven = p.Cod_Pes
    LEFT JOIN ContratoVenda cv ON 
        v.Num_Ven = cv.NumContrato_conv AND 
        v.Empresa_Ven = cv.Empresa_conv AND 
        v.Obra_Ven = CAST(cv.Obra_conv AS VARCHAR)
    LEFT JOIN ItensVenda iv ON 
        v.Num_Ven = iv.NumVend_Itv AND 
        v.Empresa_Ven = iv.Empresa_itv AND 
        v.Obra_Ven = CAST(iv.Obra_Itv AS VARCHAR)
    LEFT JOIN Unidade u ON CAST(iv.Produto_Itv AS VARCHAR) = CAST(u.Cod_Un AS VARCHAR)
    WHERE v.Num_Ven = ? AND v.Empresa_Ven = ? AND v.Obra_Ven = ?
    """
    
    try:
        cursor.execute(sql, (int(venda_id), int(empresa), str(obra)))
        row = cursor.fetchone()
        
        details = {}
        if row:
            columns = [column[0] for column in cursor.description]
            row_dict = dict(zip(columns, row))
            
            # Formatação do endereço com preferência para ContratoVenda
            ender = (row_dict.get('ender_conv') or '').strip()
            bairro = (row_dict.get('bairro_conv') or '').strip()
            cidade = (row_dict.get('cidade_conv') or '').strip()
            uf = (row_dict.get('uf_conv') or '').strip()
            cep = (row_dict.get('cep_conv') or '').strip()
            
            endereco_full = f"{ender}, {bairro} - {cidade}/{uf}".strip(" ,-/")
            if cep: endereco_full += f" (CEP: {cep})"
            
            # LOTE/QUADRA: Tenta extrair da descrição (ex: "QUADRA 01 LOTE 022")
            desc_lote = (row_dict.get('desc_lote') or '').upper()
            num_lote = "N/A"
            quadra = "N/A"
            
            if "LOTE" in desc_lote:
                try: num_lote = desc_lote.split("LOTE")[1].strip().split(" ")[0]
                except: pass
            if "QUADRA" in desc_lote:
                try: quadra = desc_lote.split("QUADRA")[1].strip().split(" ")[0]
                except: pass
            
            details = {
                "num_contrato": row_dict.get('Num_Ven'),
                "nome_cliente": row_dict.get('Nome_Pes'),
                "cpf_cliente": row_dict.get('Cpf_Pes'),
                "rg_cliente": "Consulte o UAU", 
                "data_nascimento": row_dict.get('DtNasc_Pes').strftime("%d/%m/%Y") if row_dict.get('DtNasc_Pes') and hasattr(row_dict.get('DtNasc_Pes'), 'strftime') else "",
                "data_venda": row_dict.get('Data_Ven').strftime("%d/%m/%Y") if row_dict.get('Data_Ven') and hasattr(row_dict.get('Data_Ven'), 'strftime') else "",
                "valor_total": f"R$ {row_dict.get('ValorTot_Ven', 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                "endereco_cliente": endereco_full if endereco_full else "Consulte endereço no UAU",
                "num_lote": num_lote, 
                "quadra": quadra,
                "residencial": "VALLE DO IPITINGA"
            }
        
        conn.close()
        return details
    except Exception as e:
        if conn: conn.close()
        print(f"Erro ao buscar detalhes para {venda_id}: {e}")
        return None
