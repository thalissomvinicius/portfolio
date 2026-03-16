"""Teste exato da query do Termo de Quitação para cod 73309"""
from database import execute_query

cliente_cod_hist = 73309

print("=" * 60)
print(f"TESTANDO QUERY DO TERMO DE QUITAÇÃO PARA CLIENTE {cliente_cod_hist}")
print("=" * 60)

# Query exata do código (sem ci_pes, EstadoCivil_Pes, OrgEmissor_Pes que não existem)
query = f"""
SELECT TOP 1 
    P.Nome_pes as nome, 
    P.cpf_pes as cpf, 
    P.dtnasc_pes as dataNascimento,
    PE.Endereco_pend as endereco_PE,
    PE.NumEnd_pend as numero_PE,
    PE.Bairro_pend as bairro_PE,
    PE.Cidade_pend as cidade_PE,
    PE.UF_pend as uf_PE,
    PE.CEP_pend as cep_PE,
    PE.CodEmp_pend as CodEmpPend,
    PEmpresa.cod_pes as codEmpresa,
    PEmpresa.Nome_pes as nomeEmpresa,
    PEComercial.Endereco_pend as endereco_PEComercial,
    PEComercial.Cidade_pend as cidade_PEComercial,
    ISNULL(PE.Endereco_pend, PEComercial.Endereco_pend) as endereco_final,
    ISNULL(PE.NumEnd_pend, PEComercial.NumEnd_pend) as numero_final,
    ISNULL(PE.Bairro_pend, PEComercial.Bairro_pend) as bairro_final,
    ISNULL(PE.Cidade_pend, PEComercial.Cidade_pend) as cidade_final,
    ISNULL(PE.UF_pend, PEComercial.UF_pend) as uf_final,
    ISNULL(PE.CEP_pend, PEComercial.CEP_pend) as cep_final
FROM Pessoas P WITH(NOLOCK)
LEFT JOIN PesEndereco PE WITH(NOLOCK) 
    ON PE.CodPes_pend = P.cod_pes AND PE.Tipo_pend = 0
LEFT JOIN Pessoas PEmpresa WITH(NOLOCK) 
    ON PEmpresa.cod_pes = PE.CodEmp_pend
LEFT JOIN PesEndereco PEComercial WITH(NOLOCK) 
    ON PEComercial.CodPes_pend = PEmpresa.cod_pes AND PEComercial.Tipo_pend = 0
WHERE P.cod_pes = {cliente_cod_hist}
"""

result = execute_query(query)
print("\nResultado:")
for r in result:
    print(f"  Nome: {r.get('nome')}")
    print(f"  CPF: {r.get('cpf')}")
    print(f"\n  ENDEREÇO PE (direto do cliente):")
    print(f"    {r.get('endereco_PE')}, {r.get('numero_PE')}")
    print(f"    {r.get('bairro_PE')}, {r.get('cidade_PE')}-{r.get('uf_PE')}")
    print(f"    CEP: {r.get('cep_PE')}")
    print(f"    CodEmp_pend: {r.get('CodEmpPend')}")
    print(f"\n  EMPRESA VINCULADA:")
    print(f"    Cod: {r.get('codEmpresa')}, Nome: {r.get('nomeEmpresa')}")
    print(f"\n  ENDEREÇO PEComercial (da empresa):")
    print(f"    {r.get('endereco_PEComercial')}, {r.get('cidade_PEComercial')}")
    print(f"\n  ENDEREÇO FINAL (com ISNULL):")
    print(f"    {r.get('endereco_final')}, {r.get('numero_final')}")
    print(f"    {r.get('bairro_final')}, {r.get('cidade_final')}-{r.get('uf_final')}")
    print(f"    CEP: {r.get('cep_final')}")

# Verificar qual cliente está sendo pego pelo histórico
print("\n" + "=" * 60)
print("VERIFICANDO HISTÓRICO DE TRANSFERÊNCIAS PARA Q008 L029")
print("=" * 60)

empresa = 6
obra = '70400'
quadra = '008'
lote = '029'

# Query de calcular_valor_quitacao resumida
query_hist = f"""
WITH VendaAtual AS (
    SELECT DISTINCT V.Num_Ven as NumVenda, V.Empresa_Ven, V.Obra_Ven, V.Data_Ven, 
           P.Nome_pes as Cliente, P.cpf_pes as CPF, P.cod_pes as CodCliente, 'Vendas' as Origem
    FROM ItensVenda IV WITH(NOLOCK)
    INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_Itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven AND IV.Obra_Itv = V.Obra_Ven
    INNER JOIN UnidadePer U WITH(NOLOCK) ON IV.Empresa_Itv = U.Empresa_unid AND IV.Obra_Itv = U.Obra_unid 
        AND IV.Produto_Itv = U.Prod_unid AND IV.CodPerson_Itv = U.NumPer_unid
    LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
    WHERE U.Empresa_unid = {empresa} AND U.Obra_unid = '{obra}' 
      AND RTRIM(LTRIM(U.C1_unid)) = '{quadra}' AND RTRIM(LTRIM(U.C2_unid)) = '{lote}'
      AND V.Status_Ven IN (0, 3)
      
    UNION
    
    SELECT DISTINCT VR.Num_VRec as NumVenda, VR.Empresa_VRec, VR.Obra_VRec, VR.Data_VRec, 
           P.Nome_pes as Cliente, P.cpf_pes as CPF, P.cod_pes as CodCliente, 'VendasRecebidas' as Origem
    FROM ItensRecebidas IR WITH(NOLOCK)
    INNER JOIN VendasRecebidas VR WITH(NOLOCK) ON IR.Empresa_Itr = VR.Empresa_VRec AND IR.NumVend_Itr = VR.Num_VRec AND IR.Obra_Itr = VR.Obra_VRec
    INNER JOIN UnidadePer U WITH(NOLOCK) ON IR.Empresa_Itr = U.Empresa_unid AND IR.Obra_Itr = U.Obra_unid 
        AND IR.Produto_Itr = U.Prod_unid AND IR.CodPerson_Itr = U.NumPer_unid
    LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
    WHERE U.Empresa_unid = {empresa} AND U.Obra_unid = '{obra}' 
      AND RTRIM(LTRIM(U.C1_unid)) = '{quadra}' AND RTRIM(LTRIM(U.C2_unid)) = '{lote}'
      AND VR.Status_VRec IN (0, 3)
)
SELECT * FROM VendaAtual ORDER BY Data_Ven
"""

result_hist = execute_query(query_hist)
print(f"Histórico de transferências ({len(result_hist)} vendas):")
for i, r in enumerate(result_hist):
    print(f"  {i+1}. Venda {r.get('NumVenda')}: {r.get('Cliente')} (cod: {r.get('CodCliente')}) - {r.get('Origem')}")

if result_hist:
    ultimo = result_hist[-1]
    print(f"\n  ÚLTIMO (cliente atual): {ultimo.get('Cliente')} (cod: {ultimo.get('CodCliente')})")

print("\n" + "=" * 60)
print("FIM")
print("=" * 60)
