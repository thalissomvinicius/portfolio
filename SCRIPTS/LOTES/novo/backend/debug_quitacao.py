"""
Debug: Verificar campo Contrato na VendasRecebidas e UnidadePer
"""

from database import execute_query

print("=" * 70)
print("VERIFICANDO CAMPOS CONTRATO")
print("=" * 70)

# Verificar campos CONTRATO
query1 = """
SELECT TOP 10 
    VR.Num_VRec, VR.Contrato_VRec, VR.Cliente_VRec, P.Nome_pes
FROM VendasRecebidas VR
LEFT JOIN Pessoas P ON VR.Cliente_VRec = P.cod_pes
WHERE VR.Empresa_VRec = 28 AND VR.Obra_VRec = '70100'
ORDER BY VR.Num_VRec
"""
try:
    r = execute_query(query1)
    print(f"\nVendasRecebidas com Contrato ({len(r)}):")
    for x in r:
        print(f"  Venda: {x['Num_VRec']} | Contrato: {x.get('Contrato_VRec')} | {x.get('Nome_pes', '')[:25]}")
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "-" * 70)
print("VERIFICANDO UnidadePer CAMPOS")
print("-" * 70)

query2 = """
SELECT TOP 10
    U.C1_unid as quadra, U.C2_unid as lote,
    U.NumPer_unid, U.Prod_unid,
    U.Contrato_unid
FROM UnidadePer U
WHERE U.Empresa_unid = 28 AND U.Obra_unid = '70100' AND U.Vendido_unid = 4
ORDER BY U.C1_unid, U.C2_unid
"""
try:
    r = execute_query(query2)
    print(f"\nUnidadePer ({len(r)}):")
    for x in r:
        print(f"  Q{x['quadra']} L{x['lote']} | NumPer: {x['NumPer_unid']} Prod: {x['Prod_unid']} Contrato: {x.get('Contrato_unid')}")
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "-" * 70)
print("VERIFICANDO TABELA CONTRATOS OU ALGUM LINK")
print("-" * 70)

# Verificar se existe tabela de contratos
query3 = """
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE '%Contrat%'
"""
try:
    r = execute_query(query3)
    print(f"\nTabelas Contrat ({len(r)}):")
    for x in r:
        print(f"  {x['TABLE_NAME']}")
except Exception as e:
    print(f"Erro: {e}")

# Verificar ItensVendasReceb ou similar
query4 = """
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE '%ItensVend%Rec%' OR TABLE_NAME LIKE '%IVR%'
"""
try:
    r = execute_query(query4)
    print(f"\nTabelas ItensVendRec ({len(r)}):")
    for x in r:
        print(f"  {x['TABLE_NAME']}")
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "=" * 70)
print("FIM")
print("=" * 70)
