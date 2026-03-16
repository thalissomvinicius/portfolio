"""Debug mais focado para quadra 008 lote 029"""
from database import execute_query

empresa = 6
obra = '70400'
quadra = '008'
lote = '029'

print("=" * 60)
print(f"DEBUG: Q{quadra} L{lote}, Obra {obra}, Emp {empresa}")
print("=" * 60)

# 1. Verificar vendas deste lote
print("\n1. VENDAS DESTE LOTE:")
query_vendas = f"""
SELECT 
    V.Num_Ven,
    V.Status_Ven,
    V.Cliente_Ven as CodCliente,
    P.Nome_pes as Cliente,
    P.cpf_pes as CPF_CNPJ
FROM ItensVenda IV WITH(NOLOCK)
INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_Itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven AND IV.Obra_Itv = V.Obra_Ven
INNER JOIN UnidadePer U WITH(NOLOCK) ON IV.Empresa_Itv = U.Empresa_unid AND IV.Obra_Itv = U.Obra_unid 
    AND IV.Produto_Itv = U.Prod_unid AND IV.CodPerson_Itv = U.NumPer_unid
LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
WHERE U.Empresa_unid = {empresa} AND U.Obra_unid = '{obra}' 
  AND RTRIM(LTRIM(U.C1_unid)) = '{quadra}' AND RTRIM(LTRIM(U.C2_unid)) = '{lote}'
ORDER BY V.Num_Ven DESC
"""
result = execute_query(query_vendas)
for r in result:
    print(f"  Venda {r.get('Num_Ven')}, Status: {r.get('Status_Ven')}, Cod: {r.get('CodCliente')}")
    print(f"    Cliente: {r.get('Cliente')}, CPF: {r.get('CPF_CNPJ')}")

# 2. Também verificar VendasRecebidas
print("\n2. VENDAS RECEBIDAS DESTE LOTE:")
query_vrec = f"""
SELECT 
    VR.Num_VRec as Num_Ven,
    VR.Status_VRec as Status_Ven,
    VR.Cliente_VRec as CodCliente,
    P.Nome_pes as Cliente,
    P.cpf_pes as CPF_CNPJ
FROM ItensRecebidas IR WITH(NOLOCK)
INNER JOIN VendasRecebidas VR WITH(NOLOCK) ON IR.Empresa_Itr = VR.Empresa_VRec AND IR.NumVend_Itr = VR.Num_VRec AND IR.Obra_Itr = VR.Obra_VRec
INNER JOIN UnidadePer U WITH(NOLOCK) ON IR.Empresa_Itr = U.Empresa_unid AND IR.Obra_Itr = U.Obra_unid 
    AND IR.Produto_Itr = U.Prod_unid AND IR.CodPerson_Itr = U.NumPer_unid
LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
WHERE U.Empresa_unid = {empresa} AND U.Obra_unid = '{obra}' 
  AND RTRIM(LTRIM(U.C1_unid)) = '{quadra}' AND RTRIM(LTRIM(U.C2_unid)) = '{lote}'
ORDER BY VR.Num_VRec DESC
"""
result_vrec = execute_query(query_vrec)
for r in result_vrec:
    print(f"  Venda {r.get('Num_Ven')}, Status: {r.get('Status_Ven')}, Cod: {r.get('CodCliente')}")
    print(f"    Cliente: {r.get('Cliente')}, CPF: {r.get('CPF_CNPJ')}")

# 3. Buscar BRUNO XAVIER CORREA (que tem endereço AL LEOPOLDINA QD K2, 24)
print("\n3. CLIENTE 'BRUNO XAVIER CORREA' (cod 63733):")
query_bruno = """
SELECT 
    PE.Tipo_pend,
    PE.Endereco_pend,
    PE.NumEnd_pend,
    PE.Bairro_pend,
    PE.Cidade_pend,
    PE.UF_pend,
    PE.CEP_pend
FROM PesEndereco PE WITH(NOLOCK)
WHERE PE.CodPes_pend = 63733
"""
result_bruno = execute_query(query_bruno)
for r in result_bruno:
    print(f"  Tipo: {r.get('Tipo_pend')} | {r.get('Endereco_pend')}, {r.get('NumEnd_pend')}")
    print(f"    Bairro: {r.get('Bairro_pend')}, Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')}")

# 4. Verificar se DN Construtora aparece em alguma venda do lote
print("\n4. DN CONSTRUTORA (cod 73309) - vendas relacionadas:")
query_dn_vendas = f"""
SELECT 
    V.Num_Ven,
    V.Empresa_Ven,
    V.Obra_Ven,
    V.Status_Ven
FROM Vendas V WITH(NOLOCK)
WHERE V.Cliente_Ven = 73309
AND V.Empresa_Ven = {empresa}
AND V.Obra_Ven = '{obra}'
"""
result_dn = execute_query(query_dn_vendas)
print(f"  Vendas encontradas: {len(result_dn)}")
for r in result_dn:
    print(f"    Venda {r.get('Num_Ven')}, Status: {r.get('Status_Ven')}")

# 5. Verificar endereços da DN Construtora
print("\n5. ENDEREÇOS DA DN CONSTRUTORA (cod 73309):")
query_dn_end = """
SELECT 
    PE.Tipo_pend,
    PE.Endereco_pend,
    PE.NumEnd_pend,
    PE.Bairro_pend,
    PE.Cidade_pend,
    PE.UF_pend,
    PE.CEP_pend
FROM PesEndereco PE WITH(NOLOCK)
WHERE PE.CodPes_pend = 73309
"""
result_dn_end = execute_query(query_dn_end)
for r in result_dn_end:
    print(f"  Tipo: {r.get('Tipo_pend')} | {r.get('Endereco_pend')}, {r.get('NumEnd_pend')}")
    print(f"    Bairro: {r.get('Bairro_pend')}, Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')}")
    print(f"    CEP: {r.get('CEP_pend')}")

# 6. Verificar histórico de transferencias para este lote via VendaHist
print("\n6. HISTÓRICO DE TRANSFERÊNCIAS:")
if result:
    # Pegar todas as vendas
    vendas_nums = [str(r.get('Num_Ven')) for r in result]
    vendas_in = ','.join(vendas_nums)
    query_hist = f"""
    SELECT 
        VH.NumVend_vhist as VendaAnterior,
        VH.NumNovaVend_vhist as VendaNova,
        VH.TipoMnt_vhist as TipoMnt,
        P.Nome_pes as ClienteAnterior,
        P.cod_pes as CodClienteAnterior
    FROM VendaHist VH WITH(NOLOCK)
    LEFT JOIN Vendas V ON VH.Empresa_vhist = V.Empresa_Ven AND VH.Obra_vhist = V.Obra_Ven AND VH.NumVend_vhist = V.Num_Ven
    LEFT JOIN Pessoas P ON V.Cliente_Ven = P.cod_pes
    WHERE VH.Empresa_vhist = {empresa} AND VH.Obra_vhist = '{obra}'
    AND (VH.NumNovaVend_vhist IN ({vendas_in}) OR VH.NumVend_vhist IN ({vendas_in}))
    ORDER BY VH.NumNovaVend_vhist
    """
    result_hist = execute_query(query_hist)
    for r in result_hist:
        print(f"  {r.get('VendaAnterior')} -> {r.get('VendaNova')} (Tipo: {r.get('TipoMnt')})")
        print(f"    Cliente Ant: {r.get('ClienteAnterior')} (cod: {r.get('CodClienteAnterior')})")

print("\n" + "=" * 60)
print("FIM")
print("=" * 60)
