"""Test script to debug address lookup for client 73309 (DN CONSTRUTORA)"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import execute_query

# First, let's see what the PesEndereco table has for client 73309
print("=" * 80)
print("1. ALL ADDRESSES FOR CLIENT 73309:")
print("=" * 80)

query1 = """
SELECT 
    CodPes_pend, 
    Tipo_pend,
    Endereco_pend,
    Bairro_pend,
    Cidade_pend,
    UF_pend,
    CEP_pend,
    NumEnd_pend,
    CodEmp_pend
FROM PesEndereco WITH(NOLOCK)
WHERE CodPes_pend = 73309
"""
result1 = execute_query(query1)
for r in result1:
    print(f"Tipo: {r.get('Tipo_pend')}")
    print(f"  Endereco: {r.get('Endereco_pend')}")
    print(f"  Bairro: {r.get('Bairro_pend')}")
    print(f"  Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')}")
    print(f"  CEP: {r.get('CEP_pend')}")
    print(f"  CodEmp_pend (empresa vinculada): {r.get('CodEmp_pend')}")
    print("-" * 40)

# Now let's test the EXACT query being used in quitacao.py
print("\n" + "=" * 80)
print("2. RESULT OF THE CURRENT QUERY:")
print("=" * 80)

query2 = """
SELECT TOP 1 
    P.Nome_pes as nome, 
    P.cpf_pes as cpf, 
    ISNULL(PE.Endereco_pend, PEComercial.Endereco_pend) as endereco,
    ISNULL(PE.NumEnd_pend, PEComercial.NumEnd_pend) as numero,
    ISNULL(PE.Bairro_pend, PEComercial.Bairro_pend) as bairro,
    ISNULL(PE.Cidade_pend, PEComercial.Cidade_pend) as cidade,
    ISNULL(PE.UF_pend, PEComercial.UF_pend) as uf,
    ISNULL(PE.CEP_pend, PEComercial.CEP_pend) as cep,
    PE.Endereco_pend as endereco_direto,
    PEComercial.Endereco_pend as endereco_empresa
FROM Pessoas P WITH(NOLOCK)
LEFT JOIN PesEndereco PE WITH(NOLOCK) 
    ON PE.CodPes_pend = P.cod_pes AND PE.Tipo_pend = 0
LEFT JOIN Pessoas PEmpresa WITH(NOLOCK) 
    ON PEmpresa.cod_pes = PE.CodEmp_pend
LEFT JOIN PesEndereco PEComercial WITH(NOLOCK) 
    ON PEComercial.CodPes_pend = PEmpresa.cod_pes AND PEComercial.Tipo_pend = 0
WHERE P.cod_pes = 73309
"""
result2 = execute_query(query2)
for r in result2:
    print(f"Nome: {r.get('nome')}")
    print(f"CPF/CNPJ: {r.get('cpf')}")
    print(f"Endereco (ISNULL result): {r.get('endereco')}")
    print(f"Endereco direto (PE): {r.get('endereco_direto')}")
    print(f"Endereco empresa (PEComercial): {r.get('endereco_empresa')}")
    print(f"Bairro: {r.get('bairro')}")
    print(f"Cidade: {r.get('cidade')}-{r.get('uf')}")
    print(f"CEP: {r.get('cep')}")

# Now let's test the query from the user
print("\n" + "=" * 80)
print("3. USER'S ORIGINAL SQL QUERY:")
print("=" * 80)

query3 = """
Select 
    PesEndereco.CodPes_pend, 
    PesEndereco.Tipo_pend,
    ISNULL(PesEndereco.Endereco_pend, PesEnderecoComercial.Endereco_pend) As Endereco_pend,
    ISNULL(PesEndereco.Bairro_pend, PesEnderecoComercial.Bairro_pend) As Bairro_pend,
    ISNULL(PesEndereco.Cidade_pend, PesEnderecoComercial.Cidade_pend) As Cidade_pend,
    ISNULL(PesEndereco.UF_pend, PesEnderecoComercial.UF_pend) As UF_pend,
    ISNULL(PesEndereco.CEP_pend, PesEnderecoComercial.CEP_pend) As CEP_pend,
    ISNULL(PesEndereco.NumEnd_pend, PesEnderecoComercial.NumEnd_pend) As NumEnd_pend,
    PesEndereco.Endereco_pend as EnderecoDireto,
    PesEnderecoComercial.Endereco_pend as EnderecoEmpresa
FROM PesEndereco 
LEFT JOIN Pessoas 
    On cod_pes = PesEndereco.CodEmp_pend
LEFT JOIN PesEndereco As PesEnderecoComercial
    On PesEnderecoComercial.CodPes_pend = Pessoas.cod_pes
    And PesEnderecoComercial.Tipo_pend = 0
WHERE PesEndereco.CodPes_pend = 73309
"""
result3 = execute_query(query3)
for r in result3:
    print(f"Tipo: {r.get('Tipo_pend')}")
    print(f"Endereco (ISNULL result): {r.get('Endereco_pend')}")
    print(f"Endereco direto: {r.get('EnderecoDireto')}")
    print(f"Endereco empresa: {r.get('EnderecoEmpresa')}")
    print(f"Bairro: {r.get('Bairro_pend')}")
    print(f"Cidade: {r.get('Cidade_pend')}-{r.get('UF_pend')}")
    print(f"CEP: {r.get('CEP_pend')}")
    print("-" * 40)
