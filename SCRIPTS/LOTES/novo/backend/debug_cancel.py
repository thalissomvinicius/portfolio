"""
Investigar cancelamentos em todas as tabelas
"""
import sys
sys.path.insert(0, '.')
from database import execute_query

empresa = 28
obra = '70100'

print("="*60)
print("INVESTIGAÇÃO COMPLETA DE CANCELAMENTOS")
print("="*60)

# 1. Vendas com Status_Ven = 1
q1 = f"SELECT COUNT(*) as total FROM Vendas WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}' AND Status_Ven = 1"
r1 = execute_query(q1)
print(f"\n1. Vendas com Status_Ven=1: {r1[0]['total']}")

# 2. Todos os status de vendas
q2 = f"SELECT Status_Ven, COUNT(*) as qtd FROM Vendas WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}' GROUP BY Status_Ven"
r2 = execute_query(q2)
print(f"\n2. Distribuição de Status_Ven:")
for r in r2:
    print(f"   Status {r['Status_Ven']}: {r['qtd']} vendas")

# 3. VendasRecebidas com Status = 1
q3 = f"SELECT COUNT(*) as total FROM VendasRecebidas WHERE Empresa_VRec = {empresa} AND Obra_VRec = '{obra}' AND Status_VRec = 1"
r3 = execute_query(q3)
print(f"\n3. VendasRecebidas com Status_VRec=1: {r3[0]['total']}")

# 4. Total geral de vendas
q4 = f"SELECT COUNT(*) as total FROM Vendas WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}'"
r4 = execute_query(q4)
print(f"\n4. Total de vendas na tabela: {r4[0]['total']}")

# 5. Verificar outra empresa
q5 = "SELECT Empresa_Ven, Obra_Ven, Status_Ven, COUNT(*) as qtd FROM Vendas WHERE Status_Ven = 1 GROUP BY Empresa_Ven, Obra_Ven, Status_Ven ORDER BY qtd DESC"
r5 = execute_query(q5)
print(f"\n5. Cancelamentos em OUTRAS obras:")
for r in r5[:5]:
    print(f"   Empresa {r['Empresa_Ven']}, Obra {r['Obra_Ven']}: {r['qtd']} cancelamentos")

print("="*60)
