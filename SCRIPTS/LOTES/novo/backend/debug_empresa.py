"""Debug script para verificar dados da empresa 6"""
from database import execute_query

# 1. Verificar dados da tabela Empresas para empresa 6
print("=" * 60)
print("DADOS DA TABELA EMPRESAS - Empresa 6")
print("=" * 60)
query_empresa = """
SELECT 
    Codigo_emp,
    Desc_emp,
    CGC_emp,
    Endereco_emp,
    NumEnd_emp,
    Setor_emp,
    Cidade_emp,
    UF_emp,
    CEP_emp
FROM Empresas WITH(NOLOCK)
WHERE Codigo_emp = 6
"""
result = execute_query(query_empresa)
for r in result:
    print(f"Codigo: {r.get('Codigo_emp')}")
    print(f"Razão Social: {r.get('Desc_emp')}")
    print(f"CNPJ: {r.get('CGC_emp')}")
    print(f"Endereço: {r.get('Endereco_emp')}")
    print(f"Número: {r.get('NumEnd_emp')}")
    print(f"Bairro/Setor: {r.get('Setor_emp')}")
    print(f"Cidade: {r.get('Cidade_emp')}")
    print(f"UF: {r.get('UF_emp')}")
    print(f"CEP: {r.get('CEP_emp')}")

# 2. Verificar se existe relação com obra 70400
print("\n" + "=" * 60)
print("DADOS DA OBRA 70400 - Empresa 6")
print("=" * 60)
query_obra = """
SELECT 
    O.Empresa_Obr,
    O.Cod_Obr,
    O.Descr_Obr,
    O.cid_obr,
    O.uf_obr
FROM Obras O WITH(NOLOCK)
WHERE O.Empresa_Obr = 6 AND O.Cod_Obr = '70400'
"""
result_obra = execute_query(query_obra)
for r in result_obra:
    print(f"Empresa: {r.get('Empresa_Obr')}")
    print(f"Código Obra: {r.get('Cod_Obr')}")
    print(f"Descrição: {r.get('Descr_Obr')}")
    print(f"Cidade da Obra: {r.get('cid_obr')}")
    print(f"UF da Obra: {r.get('uf_obr')}")

# 3. Verificar se existe tabela de endereços por obra ou pendências
print("\n" + "=" * 60)
print("ENDEREÇOS PENDENTES (Pendencias) - Empresa 6")
print("=" * 60)
query_pend = """
SELECT TOP 5 *
FROM Pendencias WITH(NOLOCK)
WHERE CodEmp_pend = 6
"""
try:
    result_pend = execute_query(query_pend)
    for r in result_pend:
        print(r)
except Exception as e:
    print(f"Erro ou tabela não existe: {e}")

# 4. Verificar DN Construtora no banco
print("\n" + "=" * 60)
print("BUSCANDO 'DN CONSTRUTORA' em todas as empresas")
print("=" * 60)
query_dn = """
SELECT 
    Codigo_emp,
    Desc_emp,
    CGC_emp,
    Endereco_emp,
    NumEnd_emp,
    Setor_emp,
    Cidade_emp,
    UF_emp,
    CEP_emp
FROM Empresas WITH(NOLOCK)
WHERE Desc_emp LIKE '%DN%' OR CGC_emp LIKE '%51358491%'
"""
result_dn = execute_query(query_dn)
print(f"Encontrado {len(result_dn)} empresa(s):")
for r in result_dn:
    print(f"\nCodigo: {r.get('Codigo_emp')}")
    print(f"Razão Social: {r.get('Desc_emp')}")
    print(f"CNPJ: {r.get('CGC_emp')}")
    print(f"Endereço: {r.get('Endereco_emp')}")
    print(f"Cidade: {r.get('Cidade_emp')}")
    print(f"UF: {r.get('UF_emp')}")

print("\n" + "=" * 60)
print("FIM DO DEBUG")
print("=" * 60)
