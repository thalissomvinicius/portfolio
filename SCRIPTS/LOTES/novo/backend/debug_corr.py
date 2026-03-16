"""
Debug corretores e vendas do período DEZ/2025
"""
import sys
sys.path.insert(0, '.')
from database import execute_query

empresa = 28
obra = '70100'
data_inicio_str = '20251201'
data_fim_str = '20251231'

print("="*60)
print("DEBUG PERÍODO DEZ/2025")
print("="*60)

# Corretores
query = f"""
SELECT TOP 5 P.Nome_Pes as corretor, COUNT(*) as vendas, SUM(V.ValorTot_Ven) as valor 
FROM Vendas V WITH(NOLOCK) 
INNER JOIN Pessoas P WITH(NOLOCK) ON V.Vendedor_Ven = P.Cod_Pes 
WHERE V.Empresa_Ven = {empresa} AND V.Obra_Ven = '{obra}' AND V.Status_Ven = 0 
AND V.Data_Ven >= CONVERT(datetime, '{data_inicio_str}', 112) 
AND V.Data_Ven <= CONVERT(datetime, '{data_fim_str}', 112) 
GROUP BY P.Nome_Pes 
ORDER BY vendas DESC
"""
result = execute_query(query)
print(f"\nCORRETORES (Top 5): {len(result)} resultados")
for r in result:
    print(f"  {r.get('corretor')}: {r.get('vendas')} vendas")

# Vendas diárias
query2 = f"""
SELECT TOP 10 CONVERT(VARCHAR(10), Data_Ven, 103) as data, COUNT(*) as vendas
FROM Vendas WITH(NOLOCK) 
WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}' AND Status_Ven = 0
  AND Data_Ven >= CONVERT(datetime, '{data_inicio_str}', 112) AND Data_Ven <= CONVERT(datetime, '{data_fim_str}', 112)
GROUP BY CONVERT(VARCHAR(10), Data_Ven, 103), Data_Ven
ORDER BY Data_Ven DESC
"""
r2 = execute_query(query2)
print(f"\nVENDAS DIÁRIAS: {len(r2)} dias")
for r in r2[:6]:
    print(f"  {r.get('data')}: {r.get('vendas')} vendas")

# Total vendas no período
query3 = f"""
SELECT COUNT(*) as total FROM Vendas WITH(NOLOCK) 
WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}' AND Status_Ven = 0
AND Data_Ven >= CONVERT(datetime, '{data_inicio_str}', 112) 
AND Data_Ven <= CONVERT(datetime, '{data_fim_str}', 112)
"""
r3 = execute_query(query3)
print(f"\nTOTAL VENDAS NO PERÍODO: {r3[0].get('total')}")

print("="*60)
