"""
Verificar estrutura de VendasRecebidas para cancelamentos
"""
import sys
sys.path.insert(0, '.')
from database import execute_query

print("="*60)
r = execute_query("SELECT TOP 1 * FROM VendasRecebidas WHERE Status_VRec = 1")
if r:
    print("Colunas de VendasRecebidas:")
    for k, v in r[0].items():
        print(f"  {k}: {v}")
else:
    print("Sem dados")

# Ver cancelamentos por data
print("\n" + "="*60)
r2 = execute_query("""
SELECT CONVERT(VARCHAR(10), Data_VRec, 103) as data, COUNT(*) as cancelamentos
FROM VendasRecebidas WITH(NOLOCK) 
WHERE Empresa_VRec = 28 AND Obra_VRec = '70100' AND Status_VRec = 1
GROUP BY CONVERT(VARCHAR(10), Data_VRec, 103)
ORDER BY CONVERT(VARCHAR(10), Data_VRec, 103) DESC
""")
print("Cancelamentos por data (VendasRecebidas):")
for r in r2:
    print(f"  {r.get('data')}: {r.get('cancelamentos')}")
print("="*60)
