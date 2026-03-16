"""
Script para testar o endpoint de corretores
"""
import sys
sys.path.append('.')
from database import execute_query

# Query igual ao endpoint
empresa = 28
obra = '70100'
data_inicio = '2025-12-01'
data_fim = '2025-12-27'

# Formato ISO
data_inicio_sql = data_inicio.replace('-', '')
data_fim_sql = data_fim.replace('-', '')
date_filter = f"AND (Data_Ven BETWEEN CONVERT(datetime, '{data_inicio_sql}', 112) AND CONVERT(datetime, '{data_fim_sql}', 112))"
emp_obra_param = f"{empresa}|{obra}"

stats_query = f"""
SELECT 
    ISNULL(Pessoas.nome_pes, 'Não informado') AS corretor,
    COUNT(*) AS totalVendas,
    ISNULL(SUM(VendaLiquida), 0) AS valorTotal,
    Vendedor_Ven AS vendedorCod
FROM (
    SELECT Status_Ven, Data_Ven, Num_Ven, Vendedor_Ven, Cliente_Ven, 
           ValorTot_Ven, Desconto_Ven, Acrescimo_Ven,
           Empresa_Ven, Obra_Ven, 
           (ValorTot_Ven - Desconto_Ven + Acrescimo_Ven) AS VendaLiquida
    FROM Vendas WITH(NOLOCK)
    WHERE Status_Ven IN (0, 1, 3)
        {date_filter}
    UNION    
    SELECT Status_VRec, Data_VRec, Num_VRec, Vendedor_VRec, Cliente_VRec,
           ValorTot_VRec, Desconto_VRec, Acrescimo_VRec,
           Empresa_VRec, Obra_VRec,
           (ValorTot_VRec - Desconto_VRec + Acrescimo_VRec) AS VendaLiquida
    FROM VendasRecebidas WITH(NOLOCK)
    WHERE Status_VRec IN (0, 1, 3)
        {date_filter.replace('Data_Ven', 'Data_VRec')}
) AS Vendas
INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Vendedor_Ven = Pessoas.cod_pes
INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON Vendas.Empresa_Ven = Empresa AND Vendas.Obra_Ven = Obra
WHERE Status_Ven = 0
GROUP BY Pessoas.nome_pes, Vendedor_Ven
ORDER BY COUNT(*) DESC
"""

print("Executando query do endpoint...", flush=True)
print("=" * 80, flush=True)

try:
    results = execute_query(stats_query)
    print(f"Total de corretores encontrados: {len(results)}", flush=True)
    print("-" * 80, flush=True)
    for i, r in enumerate(results[:10], 1):
        valor = float(r.get('valorTotal', 0) or 0)
        print(f"{i}. {r['corretor']}: {r['totalVendas']} vendas - R$ {valor:,.2f}", flush=True)
    print("-" * 80, flush=True)
    total_vendas = sum(r.get('totalVendas', 0) or 0 for r in results)
    total_valor = sum(float(r.get('valorTotal', 0) or 0) for r in results)
    print(f"Total de vendas: {total_vendas}", flush=True)
    print(f"Valor total: R$ {total_valor:,.2f}", flush=True)
except Exception as e:
    import traceback
    print(f"ERRO: {e}", flush=True)
    print(traceback.format_exc(), flush=True)
