"""
VallePrime Dashboard - Loteamento Routes
Dashboard executivo com dados do loteamento
"""

from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime, timedelta
from database import execute_query
import traceback

router = APIRouter()

# Mapeamento de status
STATUS_MAP = {
    0: {'label': 'DISPONIVEL', 'color': '#10B981'},
    1: {'label': 'VENDIDO', 'color': '#3B82F6'},
    2: {'label': 'RESERVADO', 'color': '#F59E0B'},
    3: {'label': 'PROPOSTA', 'color': '#8B5CF6'},
    4: {'label': 'QUITADO', 'color': '#059669'},
    5: {'label': 'ESCRITURADO', 'color': '#0891B2'},
    6: {'label': 'EM VENDA', 'color': '#6366F1'},
    7: {'label': 'SUSPENSO', 'color': '#EF4444'},
    8: {'label': 'FORA DE VENDA', 'color': '#6B7280'},
    9: {'label': 'EM ACERTO', 'color': '#EC4899'},
    10: {'label': 'DACAO', 'color': '#14B8A6'},
}


@router.get("/resumo")
async def get_loteamento_resumo(
    empresa: int = Query(..., description="Codigo da empresa"),
    obra: str = Query(..., description="Codigo da obra")
):
    """Retorna resumo geral do loteamento com status das unidades"""
    
    try:
        # Query completa baseada no Power BI - busca valor de CategoriasPrecoProd
        valor_query = f"""
        SELECT 
            Vendido_Unid as status,
            COUNT(*) as quantidade,
            ISNULL(SUM(ValPrecoPerc), 0) as valor
        FROM (
            SELECT 
                UnidadePer.Vendido_Unid,
                ROUND(CASE 
                    WHEN ud.TipoContrato_Udt IN (1, 2, 4) THEN UnidadePer.ValPreco_Unid
                    ELSE ISNULL(
                        (SELECT TOP 1 cpp.Valor_Cpp 
                         FROM CategoriasPrecoProd cpp WITH(NOLOCK)
                         WHERE cpp.NumProd_Cpp = UnidadePer.Prod_Unid 
                           AND cpp.Codigo_Cpp = UnidadePer.Codigo_Unid
                           AND cpp.Empresa_Cpp = UnidadePer.Empresa_Unid
                           AND cpp.Data_Cpp <= GETDATE()
                         ORDER BY cpp.Data_Cpp DESC),
                        UnidadePer.ValPreco_Unid
                    )
                END * (ISNULL(UnidadePer.PorcentPr_Unid, 100) / 100.0) * ISNULL(UnidadePer.Qtde_Unid, 1), 2) as ValPrecoPerc
            FROM UnidadePer WITH(NOLOCK)
            LEFT JOIN UnidadeDetalhe ud WITH(NOLOCK)
                ON UnidadePer.Empresa_Unid = ud.Empresa_Udt
                AND UnidadePer.Prod_Unid = ud.Prod_Udt
                AND UnidadePer.NumPer_Unid = ud.NumPer_Udt
            WHERE UnidadePer.Empresa_Unid = {empresa} 
                AND UnidadePer.Obra_Unid = '{obra}'
        ) AS SubQuery
        GROUP BY Vendido_Unid
        ORDER BY Vendido_Unid
        """
        
        status_data = execute_query(valor_query)
        
        # Processar dados
        total_unidades = 0
        total_valor = 0
        status_list = []
        
        for row in status_data:
            status_code = row.get('status', 0) or 0
            qtd = row.get('quantidade', 0) or 0
            valor = float(row.get('valor', 0) or 0)
            
            status_info = STATUS_MAP.get(status_code, {'label': 'OUTROS', 'color': '#6B7280'})
            
            status_list.append({
                'status': status_code,
                'label': status_info['label'],
                'color': status_info['color'],
                'quantidade': qtd,
                'valor': valor
            })
            
            total_unidades += qtd
            total_valor += valor
        
        # Calcular percentuais
        for item in status_list:
            item['percentual'] = round((item['quantidade'] / total_unidades * 100), 2) if total_unidades > 0 else 0
            item['percentualValor'] = round((item['valor'] / total_valor * 100), 2) if total_valor > 0 else 0
        
        # Buscar nome da obra
        obra_query = f"""
        SELECT Descr_Obr FROM Obras WITH(NOLOCK) 
        WHERE Empresa_Obr = {empresa} AND Cod_Obr = '{obra}'
        """
        obra_result = execute_query(obra_query)
        nome_obra = obra_result[0].get('Descr_Obr', '') if obra_result else ''
        
        return {
            "obra": nome_obra,
            "totalUnidades": total_unidades,
            "totalValor": total_valor,
            "statusUnidades": status_list
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}\n\n{error_details}")


@router.get("/vendas-diarias")
async def get_vendas_diarias(
    empresa: int = Query(..., description="Codigo da empresa"),
    obra: str = Query(..., description="Codigo da obra"),
    dias: int = Query(30, description="Numero de dias para buscar")
):
    """Retorna vendas diárias dos últimos N dias"""
    
    try:
        # Query para vendas (por Data_Ven)
        vendas_query = f"""
        SELECT 
            CONVERT(VARCHAR(10), Data_Ven, 103) as data,
            Data_Ven as dataOriginal,
            COUNT(*) as vendas,
            ISNULL(SUM(ValorTot_Ven), 0) as valorTotal,
            ISNULL(AVG(ValorTot_Ven), 0) as valorMedio
        FROM Vendas WITH(NOLOCK)
        WHERE Empresa_Ven = {empresa} 
            AND Obra_Ven = '{obra}'
            AND Data_Ven >= DATEADD(DAY, -{dias}, CAST(GETDATE() AS DATE))
            AND Status_Ven = 0
        GROUP BY Data_Ven, CONVERT(VARCHAR(10), Data_Ven, 103)
        ORDER BY Data_Ven DESC
        """
        
        # Query para cancelamentos (por DataCancel_Ven) com valor
        cancel_query = f"""
        SELECT 
            CONVERT(VARCHAR(10), DataCancel_Ven, 103) as data,
            COUNT(*) as cancelamentos,
            ISNULL(SUM(ValorTot_Ven), 0) as valorCancelamentos
        FROM Vendas WITH(NOLOCK)
        WHERE Empresa_Ven = {empresa} 
            AND Obra_Ven = '{obra}'
            AND DataCancel_Ven IS NOT NULL
            AND DataCancel_Ven >= DATEADD(DAY, -{dias}, CAST(GETDATE() AS DATE))
            AND Status_Ven = 1
        GROUP BY CONVERT(VARCHAR(10), DataCancel_Ven, 103)
        UNION ALL
        SELECT 
            CONVERT(VARCHAR(10), DataCancel_VRec, 103) as data,
            COUNT(*) as cancelamentos,
            ISNULL(SUM(ValorTot_VRec), 0) as valorCancelamentos
        FROM VendasRecebidas WITH(NOLOCK)
        WHERE Empresa_VRec = {empresa} 
            AND Obra_VRec = '{obra}'
            AND DataCancel_VRec IS NOT NULL
            AND DataCancel_VRec >= DATEADD(DAY, -{dias}, CAST(GETDATE() AS DATE))
            AND Status_VRec = 1
        GROUP BY CONVERT(VARCHAR(10), DataCancel_VRec, 103)
        """
        
        vendas_result = execute_query(vendas_query)
        cancel_result = execute_query(cancel_query)
        
        # Criar mapa de cancelamentos por data (qtd e valor)
        cancel_map = {}
        for c in cancel_result:
            data = c.get('data', '')
            if data not in cancel_map:
                cancel_map[data] = {'qtd': 0, 'valor': 0}
            cancel_map[data]['qtd'] += (c.get('cancelamentos', 0) or 0)
            cancel_map[data]['valor'] += float(c.get('valorCancelamentos', 0) or 0)
        
        # Calcular totais
        total_vendas = sum(r.get('vendas', 0) or 0 for r in vendas_result)
        total_valor = sum(float(r.get('valorTotal', 0) or 0) for r in vendas_result)
        
        # Formatar dados com cancelamentos
        vendas_list = []
        for r in vendas_result:
            data = r.get('data', '')
            cancel_info = cancel_map.get(data, {'qtd': 0, 'valor': 0})
            vendas_list.append({
                'data': data,
                'vendas': r.get('vendas', 0) or 0,
                'cancelamentos': cancel_info['qtd'],
                'valorTotal': float(r.get('valorTotal', 0) or 0),
                'valorCancelamentos': cancel_info['valor'],
                'valorMedio': float(r.get('valorMedio', 0) or 0)
            })
        
        return {
            "totalVendas": total_vendas,
            "totalValor": total_valor,
            "valorMedio": total_valor / total_vendas if total_vendas > 0 else 0,
            "vendasDiarias": vendas_list
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}\n\n{error_details}")


@router.get("/cancelamentos")
async def get_cancelamentos(
    empresa: int = Query(..., description="Codigo da empresa"),
    obra: str = Query(..., description="Codigo da obra"),
    dias: int = Query(30, description="Numero de dias para buscar")
):
    """Retorna cancelamentos dos últimos N dias"""
    
    try:
        query = f"""
        SELECT 
            CONVERT(VARCHAR(10), COALESCE(DataCancel_VRec, Data_VRec), 103) as data,
            COUNT(*) as cancelamentos
        FROM VendasRecebidas WITH(NOLOCK)
        WHERE Empresa_VRec = {empresa} 
            AND Obra_VRec = '{obra}'
            AND Status_VRec = 1
            AND COALESCE(DataCancel_VRec, Data_VRec) >= DATEADD(DAY, -{dias}, CAST(GETDATE() AS DATE))
        GROUP BY CONVERT(VARCHAR(10), COALESCE(DataCancel_VRec, Data_VRec), 103)
        ORDER BY data DESC
        """
        
        result = execute_query(query)
        
        total_cancelamentos = sum(r.get('cancelamentos', 0) or 0 for r in result)
        
        return {
            "totalCancelamentos": total_cancelamentos,
            "cancelamentosDiarios": result
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}\n\n{error_details}")


@router.get("/resumo-mensal")
async def get_resumo_mensal(
    empresa: int = Query(..., description="Codigo da empresa"),
    obra: str = Query(..., description="Codigo da obra")
):
    """Retorna resumo mensal de vendas"""
    
    try:
        query = f"""
        SELECT 
            YEAR(Data_Ven) as ano,
            MONTH(Data_Ven) as mes,
            COUNT(*) as vendas,
            ISNULL(SUM(ValorTot_Ven), 0) as valorTotal,
            ISNULL(AVG(ValorTot_Ven), 0) as valorMedio
        FROM Vendas WITH(NOLOCK)
        WHERE Empresa_Ven = {empresa} 
            AND Obra_Ven = '{obra}'
            AND Data_Ven >= DATEADD(MONTH, -12, CAST(GETDATE() AS DATE))
            AND Status_Ven = 1
        GROUP BY YEAR(Data_Ven), MONTH(Data_Ven)
        ORDER BY ano DESC, mes DESC
        """
        
        result = execute_query(query)
        
        meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho', 
                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        resumo = []
        for r in result:
            mes_num = r.get('mes', 1) or 1
            ano = r.get('ano', 2025) or 2025
            resumo.append({
                'mesAno': f"{meses_nomes[mes_num]}/{ano}",
                'mes': mes_num,
                'ano': ano,
                'vendas': r.get('vendas', 0) or 0,
                'valorTotal': float(r.get('valorTotal', 0) or 0),
                'valorMedio': float(r.get('valorMedio', 0) or 0)
            })
        
        return {
            "resumoMensal": resumo
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}\n\n{error_details}")
