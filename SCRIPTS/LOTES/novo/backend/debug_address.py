"""Debug para encontrar de onde vem o endereço DUQUE DE CAXIAS"""
from database import execute_query

# Buscar o endereço específico que está aparecendo
print("=" * 60)
print("BUSCANDO: AVENIDA DUQUE DE CAXIAS, 1696")
print("=" * 60)

query = """
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
WHERE PE.CEP_pend LIKE '%68741360%'
OR (PE.Endereco_pend LIKE '%DUQUE%CAXIAS%' AND PE.Bairro_pend LIKE '%SAUDADE%')
"""
result = execute_query(query)
print(f"Encontrado {len(result)} registros:")
for r in result:
    print(f"  CodPes: {r.get('CodPes_pend')}, Nome: {r.get('Nome_pes')}")
    print(f"    Tipo: {r.get('Tipo_pend')} | {r.get('Endereco_pend')}, {r.get('NumEnd_pend')}")
    print(f"    Bairro: {r.get('Bairro_pend')} | Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')}")
    print(f"    CEP: {r.get('CEP_pend')}")
    print()

# Verificar se tem algum vínculo com DN Construtora
print("=" * 60)
print("VERIFICANDO SE DN CONSTRUTORA TEM VINCULO COM ESSE ENDEREÇO")
print("=" * 60)

# Verificar se alguem tem CodEmp_pend para esse pessoa
if result:
    cod_pes_errado = result[0].get('CodPes_pend')
    query2 = f"""
    SELECT 
        PE.CodPes_pend,
        P.Nome_pes,
        PE.CodEmp_pend
    FROM PesEndereco PE WITH(NOLOCK)
    LEFT JOIN Pessoas P WITH(NOLOCK) ON PE.CodPes_pend = P.cod_pes
    WHERE PE.CodEmp_pend = {cod_pes_errado}
    """
    result2 = execute_query(query2)
    print(f"Pessoas que tem CodEmp_pend = {cod_pes_errado}:")
    for r in result2:
        print(f"  CodPes: {r.get('CodPes_pend')}, Nome: {r.get('Nome_pes')}")

# Verificar endereços da DN Construtora incluindo CodEmp_pend
print("\n" + "=" * 60)
print("TODOS OS ENDEREÇOS DA DN CONSTRUTORA (73309) COM CodEmp_pend")
print("=" * 60)
query3 = """
SELECT 
    PE.Tipo_pend,
    PE.Endereco_pend,
    PE.NumEnd_pend,
    PE.Bairro_pend,
    PE.Cidade_pend,
    PE.UF_pend,
    PE.CEP_pend,
    PE.CodEmp_pend,
    PEmp.Nome_pes as EmpresaVinculada
FROM PesEndereco PE WITH(NOLOCK)
LEFT JOIN Pessoas PEmp WITH(NOLOCK) ON PE.CodEmp_pend = PEmp.cod_pes
WHERE PE.CodPes_pend = 73309
"""
result3 = execute_query(query3)
for r in result3:
    print(f"  Tipo: {r.get('Tipo_pend')}")
    print(f"    Endereco: {r.get('Endereco_pend')}, {r.get('NumEnd_pend')}")
    print(f"    Bairro: {r.get('Bairro_pend')}")
    print(f"    Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')}, CEP: {r.get('CEP_pend')}")
    print(f"    CodEmp_pend: {r.get('CodEmp_pend')} -> {r.get('EmpresaVinculada')}")
    print()

print("=" * 60)
print("FIM")
print("=" * 60)
