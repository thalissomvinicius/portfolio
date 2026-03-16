"""
Verificar todas as colunas C de UnidadePer
"""
import sys
sys.path.insert(0, '.')
from database import execute_query

print("="*60)
# Todas as colunas C
r = execute_query("""
SELECT 
    Identificador_Unid,
    C1_unid, C2_unid, C3_unid, C4_unid, C5_unid, C6_unid, C7_unid, C8_unid, C9_unid, C10_unid, C11_unid, C12_unid
FROM UnidadePer 
WHERE Empresa_unid = 28 AND Obra_unid = '70100' AND Vendido_unid = 0
  AND C1_unid = '003' AND C2_unid = '036'
""")
if r:
    print("Lote 003-036:")
    for k, v in r[0].items():
        print(f"  {k}: {v}")

print("="*60)
