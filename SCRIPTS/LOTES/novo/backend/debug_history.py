from database import execute_query

def debug_lot_history():
    print("=== Buscando tabelas de Cessão ===")
    query_tables = """
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_NAME LIKE '%Cessao%' OR TABLE_NAME LIKE '%Hist%'
    """
    tables = execute_query(query_tables)
    print("Tabelas encontradas:", [t['TABLE_NAME'] for t in tables])

    # 1. Descobrir Quadra e Lote da Venda 22118
    print("\n=== Descobrindo Lote da Venda 22118 ===")
    query_lote = """
    SELECT 
        V.Num_Ven, V.Empresa_Ven, V.Obra_Ven, V.Cliente_Ven,
        IV.Produto_Itv, IV.CodPerson_Itv, IV.Obra_Itv,
        U.C1_unid as Quadra, U.C2_unid as Lote, U.Identificador_Unid
    FROM ItensVenda IV WITH(NOLOCK)
    INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_Itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven
    INNER JOIN UnidadePer U WITH(NOLOCK) ON IV.Empresa_Itv = U.Empresa_unid AND IV.Obra_Itv = U.Obra_unid AND IV.Produto_Itv = U.Prod_unid AND IV.CodPerson_Itv = U.NumPer_unid
    WHERE V.Num_Ven = 22118
    
    UNION ALL

    SELECT 
        VR.Num_VRec, VR.Empresa_VRec, VR.Obra_VRec, VR.Cliente_VRec,
        IR.Produto_Itr, IR.CodPerson_Itr, IR.Obra_Itr,
        U.C1_unid as Quadra, U.C2_unid as Lote, U.Identificador_Unid
    FROM ItensRecebidas IR WITH(NOLOCK)
    INNER JOIN VendasRecebidas VR WITH(NOLOCK) ON IR.Empresa_Itr = VR.Empresa_VRec AND IR.NumVend_Itr = VR.Num_VRec
    INNER JOIN UnidadePer U WITH(NOLOCK) ON IR.Empresa_Itr = U.Empresa_unid AND IR.Obra_Itr = U.Obra_unid AND IR.Produto_Itr = U.Prod_unid AND IR.CodPerson_Itr = U.NumPer_unid
    WHERE VR.Num_VRec = 22118
    """
    lote_data = execute_query(query_lote)
    
    if lote_data:
        lote = lote_data[0]
        print(f"Lote encontrado: Quadra {lote['Quadra']} Lote {lote['Lote']} (Unid: {lote['Identificador_Unid']})")
        empresa = lote['Empresa_Ven']
        obra = lote['Obra_Ven']
        prod = lote['Produto_Itv']
        sub = lote['CodPerson_Itv']
        q = lote['Quadra']
        l = lote['Lote']
        
        # 2. Buscar TODAS as vendas para este mesmo lote
        print(f"\n=== Buscando TODAS as vendas para Quadra {q} Lote {l} ===")
        query_history = f"""
        SELECT 'Venda' as Tipo, V.Num_Ven, V.Data_Ven, V.Status_Ven, P.Nome_pes, V.ValorTot_Ven
        FROM ItensVenda IV WITH(NOLOCK)
        INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_Itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven
        LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
        WHERE IV.Empresa_Itv = {empresa}
          AND IV.Obra_Itv = '{obra}'
          AND IV.Produto_Itv = {prod} -- Filtrando pelo produto do lote
          AND IV.CodPerson_Itv = {sub}

        UNION ALL
        
        SELECT 'VendaRecebida' as Tipo, VR.Num_VRec, VR.Data_VRec, VR.Status_VRec, P.Nome_pes, VR.ValorTot_VRec
        FROM ItensRecebidas IR WITH(NOLOCK)
        INNER JOIN VendasRecebidas VR WITH(NOLOCK) ON IR.Empresa_Itr = VR.Empresa_VRec AND IR.NumVend_Itr = VR.Num_VRec
        LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
        WHERE IR.Empresa_Itr = {empresa}
          AND IR.Obra_Itr = '{obra}'
          AND IR.Produto_Itr = {prod}
          AND IR.CodPerson_Itr = {sub}
          
        ORDER BY 2 -- Ordenar pelo número da venda
        """
        history = execute_query(query_history)
        for h in history:
            print(h)
    else:
        print("Não foi possível identificar o lote da venda 22118.")

if __name__ == "__main__":
    debug_lot_history()
