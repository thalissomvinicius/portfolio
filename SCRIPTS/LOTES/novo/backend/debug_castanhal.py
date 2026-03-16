"""Debug para verificar endereço errado - Castanhal"""
from database import execute_query

# 1. Buscar qualquer endereço em Castanhal na tabela PesEndereco
print("=" * 60)
print("BUSCANDO ENDEREÇOS COM 'CASTANHAL' na tabela PesEndereco")
print("=" * 60)
query = """
SELECT TOP 10
    PE.CodPes_pend,
    P.Nome_pes,
    PE.Tipo_pend,
    PE.Endereco_pend,
    PE.NumEnd_pend,
    PE.Bairro_pend,
    PE.Cidade_pend,
    PE.UF_pend,
    PE.CodEmp_pend
FROM PesEndereco PE WITH(NOLOCK)
LEFT JOIN Pessoas P WITH(NOLOCK) ON PE.CodPes_pend = P.cod_pes
WHERE PE.Cidade_pend LIKE '%CASTANHAL%'
ORDER BY PE.CodPes_pend DESC
"""
result = execute_query(query)
print(f"Encontrado {len(result)} endereços:")
for r in result:
    print(f"  CodPes: {r.get('CodPes_pend')}, Nome: {r.get('Nome_pes')[:40] if r.get('Nome_pes') else 'N/A'}")
    print(f"    Tipo: {r.get('Tipo_pend')} | {r.get('Endereco_pend')}, {r.get('NumEnd_pend')}")
    print(f"    Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')} | CodEmp: {r.get('CodEmp_pend')}")
    print()

# 2. Buscar endereço específico 'DUQUE DE CAXIAS, 1696'
print("\n" + "=" * 60)
print("BUSCANDO ENDEREÇO 'DUQUE DE CAXIAS' + '1696'")
print("=" * 60)
query2 = """
SELECT 
    PE.CodPes_pend,
    P.Nome_pes,
    PE.Tipo_pend,
    PE.Endereco_pend,
    PE.NumEnd_pend,
    PE.Bairro_pend,
    PE.Cidade_pend,
    PE.UF_pend,
    PE.CodEmp_pend
FROM PesEndereco PE WITH(NOLOCK)
LEFT JOIN Pessoas P WITH(NOLOCK) ON PE.CodPes_pend = P.cod_pes
WHERE PE.Endereco_pend LIKE '%DUQUE%CAXIAS%' AND PE.NumEnd_pend LIKE '%1696%'
"""
result2 = execute_query(query2)
print(f"Encontrado {len(result2)} endereços:")
for r in result2:
    print(f"  CodPes: {r.get('CodPes_pend')}, Nome: {r.get('Nome_pes')}")
    print(f"    Tipo: {r.get('Tipo_pend')} | {r.get('Endereco_pend')}, {r.get('NumEnd_pend')}")
    print(f"    Bairro: {r.get('Bairro_pend')} | Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')}")
    print(f"    CodEmp: {r.get('CodEmp_pend')}")
    print()

# 3. Se encontrou, verificar se alguma PJ tem esse CodPes_pend como CodEmp_pend
if result2:
    cod_pes_errado = result2[0].get('CodPes_pend')
    print(f"\n" + "=" * 60)
    print(f"VERIFICANDO QUEM TEM CodEmp_pend = {cod_pes_errado}")
    print("=" * 60)
    query3 = f"""
    SELECT 
        PE.CodPes_pend,
        P.Nome_pes,
        PE.Tipo_pend,
        PE.CodEmp_pend
    FROM PesEndereco PE WITH(NOLOCK)
    LEFT JOIN Pessoas P WITH(NOLOCK) ON PE.CodPes_pend = P.cod_pes
    WHERE PE.CodEmp_pend = {cod_pes_errado}
    """
    result3 = execute_query(query3)
    print(f"Encontrado {len(result3)} pessoas com CodEmp_pend = {cod_pes_errado}:")
    for r in result3:
        print(f"  CodPes: {r.get('CodPes_pend')}, Nome: {r.get('Nome_pes')}, Tipo: {r.get('Tipo_pend')}")

# 4. Verificar cliente específico da obra 70400 que aparece como DN Construtora
print("\n" + "=" * 60)
print("DN CONSTRUTORA (73309) - Verificar CodEmp_pend nos seus endereços")
print("=" * 60)
query4 = """
SELECT 
    PE.CodPes_pend,
    PE.Tipo_pend,
    PE.Endereco_pend,
    PE.NumEnd_pend,
    PE.Bairro_pend,
    PE.Cidade_pend,
    PE.UF_pend,
    PE.CodEmp_pend,
    PEmp.Nome_pes as NomeEmpresaVinculada
FROM PesEndereco PE WITH(NOLOCK)
LEFT JOIN Pessoas PEmp WITH(NOLOCK) ON PE.CodEmp_pend = PEmp.cod_pes
WHERE PE.CodPes_pend = 73309
"""
result4 = execute_query(query4)
print(f"Endereços da DN Construtora (cod 73309):")
for r in result4:
    print(f"  Tipo: {r.get('Tipo_pend')} | {r.get('Endereco_pend')}, {r.get('NumEnd_pend')}")
    print(f"    Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')}")
    print(f"    CodEmp_pend: {r.get('CodEmp_pend')} -> Empresa: {r.get('NomeEmpresaVinculada')}")
    print()

# 5. Testar a query exata do sistema
print("\n" + "=" * 60)
print("TESTANDO QUERY EXATA DO SISTEMA PARA DN CONSTRUTORA (cod 73309)")
print("=" * 60)
query5 = """
SELECT TOP 1 
    P.Nome_pes as nome, P.cpf_pes as cpf, P.dtnasc_pes as dataNascimento, P.ci_pes as rg,
    ISNULL(PE.Endereco_pend, PEComercial.Endereco_pend) as endereco, 
    ISNULL(PE.NumEnd_pend, PEComercial.NumEnd_pend) as numero, 
    ISNULL(PE.Bairro_pend, PEComercial.Bairro_pend) as bairro,
    ISNULL(PE.Cidade_pend, PEComercial.Cidade_pend) as cidade, 
    ISNULL(PE.UF_pend, PEComercial.UF_pend) as uf, 
    ISNULL(PE.CEP_pend, PEComercial.CEP_pend) as cep,
    PE.CodEmp_pend as CodEmpOriginal,
    PEComercial.CodPes_pend as CodPesComercial
FROM Pessoas P WITH(NOLOCK)
LEFT JOIN PesEndereco PE WITH(NOLOCK) 
    ON P.cod_pes = PE.CodPes_pend AND PE.Tipo_pend = 0
LEFT JOIN Pessoas PEmp WITH(NOLOCK) 
    ON PE.CodEmp_pend = PEmp.cod_pes
LEFT JOIN PesEndereco PEComercial WITH(NOLOCK) 
    ON PEComercial.CodPes_pend = PEmp.cod_pes AND PEComercial.Tipo_pend = 0
WHERE P.cod_pes = 73309
"""
result5 = execute_query(query5)
print("Resultado da query do sistema:")
for r in result5:
    for key, val in r.items():
        print(f"  {key}: {val}")

print("\n" + "=" * 60)
print("FIM DO DEBUG")
print("=" * 60)
