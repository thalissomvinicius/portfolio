"""
Verificar colunas disponíveis para lotes
"""
import sys
sys.path.insert(0, '.')
from database import execute_query

print("="*60)
# Colunas de UnidadePer
r = execute_query("SELECT TOP 1 * FROM UnidadePer WHERE Empresa_unid = 28 AND Obra_unid = '70100'")
if r:
    print("Colunas de UnidadePer:")
    for k, v in r[0].items():
        if k.lower() in ['c1_unid', 'c2_unid', 'c3_unid', 'c4_unid', 'c5_unid', 'c6_unid', 'c7_unid', 'c8_unid', 'qtde_unid', 'valpreco_unid', 'vendido_unid']:
            print(f"  {k}: {v}")

# UnidadeDetalhe
r2 = execute_query("SELECT TOP 1 * FROM UnidadeDetalhe WHERE Empresa_Udt = 28")
if r2:
    print("\nColunas de UnidadeDetalhe (selecionadas):")
    for k, v in r2[0].items():
        print(f"  {k}: {v}")

print("="*60)
