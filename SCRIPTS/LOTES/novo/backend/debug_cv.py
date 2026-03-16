"""
Verificar valores dos cancelamentos
"""
import sys
sys.path.insert(0, '.')
from database import execute_query

print("="*60)
# Cancelamentos com valor agrupados por data
r = execute_query("""
SELECT CONVERT(VARCHAR(10), DataCancel_Vrec, 103) as data, 
       COUNT(*) as qtd, 
       SUM(ValorTot_VRec) as valor
FROM VendasRecebidas WITH(NOLOCK) 
WHERE Empresa_VRec = 28 AND Obra_VRec = '70100' AND Status_VRec = 1
  AND DataCancel_Vrec >= CONVERT(datetime, '20251201', 112) 
  AND DataCancel_Vrec <= CONVERT(datetime, '20251231', 112)
GROUP BY CONVERT(VARCHAR(10), DataCancel_Vrec, 103), DataCancel_Vrec
ORDER BY DataCancel_Vrec DESC
""")
print("Cancelamentos por data com valor:")
total_qtd = 0
total_valor = 0
for x in r:
    print(f"  {x.get('data')}: {x.get('qtd')} cancelamentos, R$ {float(x.get('valor') or 0):,.2f}")
    total_qtd += x.get('qtd', 0)
    total_valor += float(x.get('valor') or 0)

print(f"\nTOTAL: {total_qtd} cancelamentos, R$ {total_valor:,.2f}")
print("="*60)
