from database import execute_query

def debug_units():
    print("=== Debug Unidades - Venda 22118 ===")
    
    # Check ItensVenda for 22118 to confirm which product/person (unit) it is
    query_itens = """
    SELECT IV.Produto_Itv, IV.CodPerson_Itv, U.C1_unid as Quadra, U.C2_unid as Lote, U.Vendido_unid
    FROM ItensVenda IV WITH(NOLOCK)
    LEFT JOIN UnidadePer U WITH(NOLOCK) ON IV.Empresa_itv = U.Empresa_unid AND IV.Obra_Itv = U.Obra_unid AND IV.Produto_Itv = U.Prod_unid AND IV.CodPerson_Itv = U.NumPer_unid
    WHERE IV.NumVend_Itv = 22118 AND IV.Empresa_Itv = 999 AND IV.Obra_Itv = '70100'
    
    UNION ALL
    
    SELECT IR.Produto_Itr, IR.CodPerson_Itr, U.C1_unid as Quadra, U.C2_unid as Lote, U.Vendido_unid
    FROM ItensRecebidas IR WITH(NOLOCK)
    LEFT JOIN UnidadePer U WITH(NOLOCK) ON IR.Empresa_Itr = U.Empresa_unid AND IR.Obra_Itr = U.Obra_unid AND IR.Produto_Itr = U.Prod_unid AND IR.CodPerson_Itr = U.NumPer_unid
    WHERE IR.NumVend_Itr = 22118 AND IR.Empresa_Itr = 999 AND IR.Obra_Itr = '70100'
    """
    
    itens = execute_query(query_itens)
    print("Itens da Venda 22118:", itens)
    
    # Check Unit A-001 specifically
    print("\n=== Verificando Quadra A Lote 001 ===")
    query_a001 = """
    SELECT Identificador_Unid, C1_unid, C2_unid, Vendido_unid
    FROM UnidadePer WITH(NOLOCK)
    WHERE Empresa_unid = 999 AND Obra_unid = '70100'
      AND RTRIM(LTRIM(C1_unid)) = 'A' AND RTRIM(LTRIM(C2_unid)) = '001'
    """
    result_a001 = execute_query(query_a001)
    print(result_a001)

if __name__ == "__main__":
    debug_units()
