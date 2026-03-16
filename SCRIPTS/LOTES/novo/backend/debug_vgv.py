"""
Verificar valor após aplicar ROUND(,2)
"""
import sys
sys.path.insert(0, '.')
from database import execute_query

empresa = 28
obra = '70100'
target = 103168404.30

# Query com ROUND (igual ao loteamento.py atualizado)
q = f"""
SELECT SUM(ValPrecoPerc) as vgv FROM (
    SELECT ROUND(CASE WHEN ud.TipoContrato_Udt IN (1, 2, 4) THEN UnidadePer.ValPreco_Unid
    ELSE ISNULL((SELECT TOP 1 cpp.Valor_Cpp FROM CategoriasPrecoProd cpp WITH(NOLOCK) WHERE cpp.NumProd_Cpp = UnidadePer.Prod_Unid 
    AND cpp.Codigo_Cpp = UnidadePer.Codigo_Unid AND cpp.Empresa_Cpp = UnidadePer.Empresa_Unid AND cpp.Data_Cpp <= GETDATE()
    ORDER BY cpp.Data_Cpp DESC), UnidadePer.ValPreco_Unid) END * (ISNULL(UnidadePer.PorcentPr_Unid, 100) / 100.0) * ISNULL(UnidadePer.Qtde_Unid, 1), 2) as ValPrecoPerc
    FROM UnidadePer WITH(NOLOCK) LEFT JOIN UnidadeDetalhe ud WITH(NOLOCK) ON UnidadePer.Empresa_Unid = ud.Empresa_Udt AND UnidadePer.Prod_Unid = ud.Prod_Udt AND UnidadePer.NumPer_Unid = ud.NumPer_Udt
    WHERE UnidadePer.Empresa_Unid = {empresa} AND UnidadePer.Obra_Unid = '{obra}'
) X
"""

result = execute_query(q)
vgv = float(result[0].get('vgv', 0) or 0)
diff = vgv - target

print("="*60)
print("RESULTADO COM ROUND(,2)")
print("="*60)
print(f"VGV Calculado: R$ {vgv:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
print(f"VGV Target:    R$ {target:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
print(f"Diferenca:     R$ {diff:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
print("="*60)
