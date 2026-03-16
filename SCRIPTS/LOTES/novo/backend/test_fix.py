"""Teste após correção - Verificar endereço do cliente 73309"""
from database import execute_query

empresa = 6
obra = '70400'
quadra = '008'
lote = '029'

print("=" * 60)
print(f"TESTE PÓS-CORREÇÃO: Q{quadra} L{lote}")
print("=" * 60)

# Executar a mesma query que get_dados_quitacao agora usaria
query = f"""
SELECT 
    U.C1_unid as quadra,
    U.C2_unid as lote,
    COALESCE(VendasAtivas.Num_Ven, VendasRec.Num_VRec) as numVenda,
    COALESCE(VendasAtivas.Nome_pes, VendasRec.Nome_pes) as cliente,
    COALESCE(VendasAtivas.cpf_pes, VendasRec.cpf_pes) as cpf,
    COALESCE(VendasAtivas.cod_pes, VendasRec.cod_pes) as codCliente
FROM UnidadePer U WITH(NOLOCK)
-- Tentar via Vendas + ItensVenda
OUTER APPLY (
    SELECT TOP 1 V.Num_Ven, V.ValorTot_Ven, P.Nome_pes, P.cpf_pes, P.dtnasc_pes, P.cod_pes
    FROM ItensVenda IV WITH(NOLOCK)
    INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven
    LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
    WHERE IV.Empresa_itv = U.Empresa_unid 
      AND IV.Produto_Itv = U.Prod_unid 
      AND IV.CodPerson_Itv = U.NumPer_unid
    ORDER BY V.Num_Ven DESC
) VendasAtivas
-- Fallback via VendasRecebidas + ItensRecebidas (CORRIGIDO)
OUTER APPLY (
    SELECT TOP 1 VR.Num_VRec, VR.ValorTot_VRec, P.Nome_pes, P.cpf_pes, P.dtnasc_pes, P.cod_pes
    FROM ItensRecebidas IR WITH(NOLOCK)
    INNER JOIN VendasRecebidas VR WITH(NOLOCK) 
        ON IR.Empresa_Itr = VR.Empresa_VRec 
        AND IR.NumVend_Itr = VR.Num_VRec 
        AND IR.Obra_Itr = VR.Obra_VRec
    LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
    WHERE IR.Empresa_Itr = U.Empresa_unid 
      AND IR.Obra_Itr = U.Obra_unid
      AND IR.Produto_Itr = U.Prod_unid
      AND IR.CodPerson_Itr = U.NumPer_unid
      AND VR.Status_VRec IN (0, 3)
    ORDER BY VR.Num_VRec DESC
) VendasRec
WHERE U.Empresa_unid = {empresa}
  AND U.Obra_unid = '{obra}'
  AND U.Vendido_unid = 4
  AND RTRIM(LTRIM(U.C1_unid)) = '{quadra}'
  AND RTRIM(LTRIM(U.C2_unid)) = '{lote}'
"""

result = execute_query(query)
print("\nResultado da query CORRIGIDA:")
for r in result:
    print(f"  Quadra: {r.get('quadra')}, Lote: {r.get('lote')}")
    print(f"  Venda: {r.get('numVenda')}")
    print(f"  Cliente: {r.get('cliente')}")
    print(f"  CPF/CNPJ: {r.get('cpf')}")
    print(f"  Cod: {r.get('codCliente')}")

# Verificar endereço deste cliente
if result:
    cod_cliente = result[0].get('codCliente')
    if cod_cliente:
        print(f"\nENDEREÇO DO CLIENTE {cod_cliente}:")
        query_end = f"""
        SELECT TOP 1
            Endereco_pend,
            NumEnd_pend,
            Bairro_pend,
            Cidade_pend,
            UF_pend,
            CEP_pend
        FROM PesEndereco WITH(NOLOCK)
        WHERE CodPes_pend = {cod_cliente} AND Tipo_pend = 0
        """
        end = execute_query(query_end)
        for e in end:
            print(f"  {e.get('Endereco_pend')}, {e.get('NumEnd_pend')}")
            print(f"  {e.get('Bairro_pend')}, {e.get('Cidade_pend')}-{e.get('UF_pend')}")
            print(f"  CEP: {e.get('CEP_pend')}")

print("\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)
