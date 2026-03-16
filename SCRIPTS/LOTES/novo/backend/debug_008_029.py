"""Debug específico para quadra 008 lote 029 - DN Construtora"""
from database import execute_query

empresa = 6
obra = '70400'
quadra = '008'
lote = '029'

print("=" * 60)
print(f"DEBUG: Quadra {quadra}, Lote {lote}, Obra {obra}, Empresa {empresa}")
print("=" * 60)

# 1. Verificar qual cliente está na venda deste lote
print("\n1. VENDAS DESTE LOTE:")
query_vendas = f"""
SELECT 
    V.Num_Ven,
    V.Status_Ven,
    V.Cliente_Ven,
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
    print(f"  Venda {r.get('Num_Ven')}, Status: {r.get('Status_Ven')}, Cliente: {r.get('Cliente')}")
    print(f"    CPF/CNPJ: {r.get('CPF_CNPJ')}, CodCliente: {r.get('Cliente_Ven')}")

# 2. Verificar TODOS os endereços da DN Construtora (cod 73309)
print("\n2. TODOS OS ENDEREÇOS DA DN CONSTRUTORA (cod 73309):")
query_end = """
SELECT 
    PE.Tipo_pend,
    PE.Endereco_pend,
    PE.NumEnd_pend,
    PE.Bairro_pend,
    PE.Cidade_pend,
    PE.UF_pend,
    PE.CEP_pend,
    PE.CodEmp_pend
FROM PesEndereco PE WITH(NOLOCK)
WHERE PE.CodPes_pend = 73309
ORDER BY PE.Tipo_pend
"""
result_end = execute_query(query_end)
for r in result_end:
    print(f"  Tipo: {r.get('Tipo_pend')} | {r.get('Endereco_pend')}, {r.get('NumEnd_pend')}")
    print(f"    Bairro: {r.get('Bairro_pend')} | Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')}")
    print(f"    CEP: {r.get('CEP_pend')} | CodEmp: {r.get('CodEmp_pend')}")
    print()

# 3. Buscar endereço ALAMEDA LEOPOLDINA (que aparece no documento)
print("\n3. BUSCANDO ENDEREÇO 'ALAMEDA LEOPOLDINA' NO BANCO:")
query_leopoldina = """
SELECT 
    PE.CodPes_pend,
    P.Nome_pes,
    PE.Tipo_pend,
    PE.Endereco_pend,
    PE.NumEnd_pend,
    PE.Bairro_pend,
    PE.Cidade_pend,
    PE.UF_pend,
    PE.CEP_pend
FROM PesEndereco PE WITH(NOLOCK)
LEFT JOIN Pessoas P WITH(NOLOCK) ON PE.CodPes_pend = P.cod_pes
WHERE PE.Endereco_pend LIKE '%LEOPOLDINA%'
"""
result_leo = execute_query(query_leopoldina)
print(f"Encontrado {len(result_leo)} endereços com LEOPOLDINA:")
for r in result_leo:
    print(f"  CodPes: {r.get('CodPes_pend')}, Nome: {r.get('Nome_pes')}")
    print(f"    {r.get('Endereco_pend')}, {r.get('NumEnd_pend')}, {r.get('Bairro_pend')}")
    print(f"    Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')}, CEP: {r.get('CEP_pend')}")
    print()

# 4. Verificar histórico de transferências do lote
print("\n4. HISTÓRICO DE TRANSFERÊNCIAS (VendaHist):")
# Primeiro pegar a venda atual
if result:
    venda_atual = result[0].get('Num_Ven')
    query_hist = f"""
    SELECT 
        VH.NumVend_vhist as VendaAnterior,
        VH.NumNovaVend_vhist as VendaNova,
        VH.TipoMnt_vhist as TipoManutencao,
        VH.DataAssinaturaCessao_vhist as DataCessao,
        P.Nome_pes as ClienteAnterior,
        P.cod_pes as CodClienteAnterior
    FROM VendaHist VH WITH(NOLOCK)
    LEFT JOIN Vendas V ON VH.Empresa_vhist = V.Empresa_Ven AND VH.Obra_vhist = V.Obra_Ven AND VH.NumVend_vhist = V.Num_Ven
    LEFT JOIN Pessoas P ON V.Cliente_Ven = P.cod_pes
    WHERE VH.Empresa_vhist = {empresa} AND VH.Obra_vhist = '{obra}'
    AND VH.NumNovaVend_vhist = {venda_atual}
    """
    try:
        result_hist = execute_query(query_hist)
        for r in result_hist:
            print(f"  Venda {r.get('VendaAnterior')} -> {r.get('VendaNova')}, Tipo: {r.get('TipoManutencao')}")
            print(f"    Cliente Anterior: {r.get('ClienteAnterior')} (cod: {r.get('CodClienteAnterior')})")
    except Exception as e:
        print(f"  Erro: {e}")

# 5. Verificar se a query do sistema está pegando o cliente certo
print("\n5. SIMULANDO QUERY DO SISTEMA PARA TERMO DE QUITAÇÃO:")
# A query busca o ÚLTIMO cliente no histórico de transferências
query_ultimo = f"""
WITH VendaAtual AS (
    SELECT DISTINCT V.Num_Ven as NumVenda, V.Empresa_Ven, V.Obra_Ven, V.Data_Ven, 
           P.Nome_pes as Cliente, P.cpf_pes as CPF, P.cod_pes as CodCliente
    FROM ItensVenda IV WITH(NOLOCK)
    INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_Itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven AND IV.Obra_Itv = V.Obra_Ven
    INNER JOIN UnidadePer U WITH(NOLOCK) ON IV.Empresa_Itv = U.Empresa_unid AND IV.Obra_Itv = U.Obra_unid 
        AND IV.Produto_Itv = U.Prod_unid AND IV.CodPerson_Itv = U.NumPer_unid
    LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
    WHERE U.Empresa_unid = {empresa} AND U.Obra_unid = '{obra}' 
      AND RTRIM(LTRIM(U.C1_unid)) = '{quadra}' AND RTRIM(LTRIM(U.C2_unid)) = '{lote}'
      AND V.Status_Ven IN (0, 3)
)
SELECT * FROM VendaAtual
"""
result_atual = execute_query(query_ultimo)
print("Cliente atual (última venda):")
for r in result_atual:
    print(f"  Venda: {r.get('NumVenda')}, Cliente: {r.get('Cliente')}")
    print(f"  CPF/CNPJ: {r.get('CPF')}, CodCliente: {r.get('CodCliente')}")
    
    # Buscar endereço para este cliente
    cod_cliente = r.get('CodCliente')
    if cod_cliente:
        print(f"\n6. ENDEREÇO RETORNADO PARA CLIENTE {cod_cliente}:")
        query_end_cliente = f"""
        SELECT TOP 1
            PE.Tipo_pend,
            PE.Endereco_pend,
            PE.NumEnd_pend,
            PE.Bairro_pend,
            PE.Cidade_pend,
            PE.UF_pend,
            PE.CEP_pend
        FROM PesEndereco PE WITH(NOLOCK)
        WHERE PE.CodPes_pend = {cod_cliente}
        AND PE.Tipo_pend = 0
        """
        result_end_cliente = execute_query(query_end_cliente)
        for e in result_end_cliente:
            print(f"  Tipo: {e.get('Tipo_pend')}")
            print(f"  Endereço: {e.get('Endereco_pend')}, {e.get('NumEnd_pend')}")
            print(f"  Bairro: {e.get('Bairro_pend')}")
            print(f"  Cidade: {e.get('Cidade_pend')}-{e.get('UF_pend')}")
            print(f"  CEP: {e.get('CEP_pend')}")

print("\n" + "=" * 60)
print("FIM DO DEBUG")
print("=" * 60)
