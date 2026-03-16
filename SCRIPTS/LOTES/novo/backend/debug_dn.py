"""Debug script para verificar de onde vem DN CONSTRUTORA"""
from database import execute_query

# 1. Buscar DN Construtora por nome em Pessoas
print("=" * 60)
print("BUSCANDO 'DN CONSTRUTORA' na tabela Pessoas")
print("=" * 60)
query_dn_pes = """
SELECT TOP 5
    cod_pes,
    Nome_pes,
    cpf_pes,
    Tipo_Pes
FROM Pessoas WITH(NOLOCK)
WHERE Nome_pes LIKE '%DN%CONSTRUTORA%' OR Nome_pes LIKE '%DN CONSTRUTORA%'
"""
result = execute_query(query_dn_pes)
print(f"Encontrado {len(result)} pessoas:")
for r in result:
    print(f"  Cod: {r.get('cod_pes')}, Nome: {r.get('Nome_pes')}, CPF/CNPJ: {r.get('cpf_pes')}, Tipo: {r.get('Tipo_Pes')}")

# 2. Buscar por CNPJ específico 51.358.491/0001-88
print("\n" + "=" * 60)
print("BUSCANDO POR CNPJ 51.358.491/0001-88")
print("=" * 60)
query_cnpj = """
SELECT TOP 5
    cod_pes,
    Nome_pes,
    cpf_pes,
    Tipo_Pes
FROM Pessoas WITH(NOLOCK)
WHERE cpf_pes LIKE '%51358491%'
"""
result_cnpj = execute_query(query_cnpj)
print(f"Encontrado {len(result_cnpj)} pessoas:")
for r in result_cnpj:
    print(f"  Cod: {r.get('cod_pes')}, Nome: {r.get('Nome_pes')}, CPF/CNPJ: {r.get('cpf_pes')}")

# 3. Se encontrou, buscar no PesEndereco
if result_cnpj:
    cod_pes = result_cnpj[0].get('cod_pes')
    print(f"\n" + "=" * 60)
    print(f"ENDEREÇOS DA PESSOA COD: {cod_pes}")
    print("=" * 60)
    query_end = f"""
    SELECT 
        Tipo_pend,
        Endereco_pend,
        NumEnd_pend,
        Bairro_pend,
        Cidade_pend,
        UF_pend,
        CEP_pend,
        CodEmp_pend
    FROM PesEndereco WITH(NOLOCK)
    WHERE CodPes_pend = {cod_pes}
    ORDER BY Tipo_pend
    """
    result_end = execute_query(query_end)
    print(f"Encontrado {len(result_end)} endereços:")
    for r in result_end:
        print(f"  Tipo: {r.get('Tipo_pend')} | {r.get('Endereco_pend')}, {r.get('NumEnd_pend')} | "
              f"Bairro: {r.get('Bairro_pend')} | Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')} | "
              f"CEP: {r.get('CEP_pend')} | CodEmp: {r.get('CodEmp_pend')}")

# 4. Buscar vendas na obra 70400 para identificar o cliente
print("\n" + "=" * 60)
print("VENDAS NA OBRA 70400 (Empresa 6)")
print("=" * 60)
query_vendas = """
SELECT TOP 10
    V.Num_Ven,
    V.Empresa_Ven,
    V.Obra_Ven,
    P.Nome_pes as Cliente,
    P.cpf_pes as CPF,
    P.cod_pes as CodCliente
FROM Vendas V WITH(NOLOCK)
LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
WHERE V.Empresa_Ven = 6 AND V.Obra_Ven = '70400'
ORDER BY V.Num_Ven DESC
"""
result_vendas = execute_query(query_vendas)
print(f"Encontrado {len(result_vendas)} vendas:")
for r in result_vendas:
    print(f"  Venda: {r.get('Num_Ven')}, Cliente: {r.get('Cliente')}, CPF: {r.get('CPF')}")

# 5. Verificar descrição da obra
print("\n" + "=" * 60)
print("OBRA 70400 - Detalhes")
print("=" * 60)
query_obra = """
SELECT TOP 1 *
FROM Obras WITH(NOLOCK)
WHERE Empresa_Obr = 6 AND Cod_Obr = '70400'
"""
result_obra = execute_query(query_obra)
if result_obra:
    for key, value in result_obra[0].items():
        if value:
            print(f"  {key}: {value}")

print("\n" + "=" * 60)
print("FIM DO DEBUG")
print("=" * 60)
