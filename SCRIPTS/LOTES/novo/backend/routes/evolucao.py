"""
VallePrime Dashboard - Evolução do Empreendimento Routes
"""

from fastapi import APIRouter, Query, HTTPException
from database import execute_query
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/evolucao")
async def get_evolucao(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    data: str = Query(None, description="Data de referência (YYYY-MM-DD), padrão hoje")
):
    """Busca métricas de evolução do empreendimento"""
    
    # Data de referência (usa hoje se não fornecida)
    if data:
        try:
            data_ref = datetime.strptime(data, '%Y-%m-%d')
        except:
            data_ref = datetime.now()
    else:
        data_ref = datetime.now()
    
    data_ref_str = data_ref.strftime('%Y-%m-%d')
    primeiro_dia_mes = data_ref.replace(day=1)
    primeiro_dia_ano = data_ref.replace(month=1, day=1)
    
    # Initialize defaults
    vendas = {}
    recebimentos = {}
    inadimplencia = {}
    estoque = {}
    sinais = {}
    recebimentos_diarios = []
    
    try:
        # ========== VENDAS ==========
        vendas_query = f"""
        SELECT 
            COUNT(*) AS totalVendas,
            ISNULL(SUM(ValorTot_Ven + Acrescimo_Ven - Desconto_Ven), 0) AS valorTotal,
            SUM(CASE WHEN Data_Ven >= '{primeiro_dia_mes.strftime('%Y-%m-%d')}' THEN 1 ELSE 0 END) AS vendasMes,
            ISNULL(SUM(CASE WHEN Data_Ven >= '{primeiro_dia_mes.strftime('%Y-%m-%d')}' THEN ValorTot_Ven + Acrescimo_Ven - Desconto_Ven ELSE 0 END), 0) AS valorMes,
            SUM(CASE WHEN Data_Ven >= '{primeiro_dia_ano.strftime('%Y-%m-%d')}' THEN 1 ELSE 0 END) AS vendasAno,
            ISNULL(SUM(CASE WHEN Data_Ven >= '{primeiro_dia_ano.strftime('%Y-%m-%d')}' THEN ValorTot_Ven + Acrescimo_Ven - Desconto_Ven ELSE 0 END), 0) AS valorAno,
            SUM(CASE WHEN CONVERT(date, Data_Ven) = '{data_ref_str}' THEN 1 ELSE 0 END) AS vendasHoje,
            ISNULL(SUM(CASE WHEN CONVERT(date, Data_Ven) = '{data_ref_str}' THEN ValorTot_Ven + Acrescimo_Ven - Desconto_Ven ELSE 0 END), 0) AS valorHoje
        FROM Vendas WITH(NOLOCK)
        WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}'
        """
        vendas_result = execute_query(vendas_query)
        vendas = vendas_result[0] if vendas_result else {}
    except Exception as e:
        print(f"Erro vendas: {e}")
    
    try:
        # ========== RECEBIMENTOS (usando data de conciliação) ==========
        recebimentos_query = f"""
        SELECT 
            ISNULL(SUM(CASE WHEN CONVERT(date, Extrato.Data_Doc) = '{data_ref_str}' THEN 
                RecebePgtoDiv.PercentValor_Rpd
            ELSE 0 END), 0) AS recebidoHoje,
            ISNULL(SUM(CASE WHEN CONVERT(date, Extrato.Data_Doc) >= '{primeiro_dia_mes.strftime('%Y-%m-%d')}' THEN 
                RecebePgtoDiv.PercentValor_Rpd
            ELSE 0 END), 0) AS recebidoMes,
            ISNULL(SUM(CASE WHEN CONVERT(date, Extrato.Data_Doc) >= '{primeiro_dia_ano.strftime('%Y-%m-%d')}' THEN 
                RecebePgtoDiv.PercentValor_Rpd
            ELSE 0 END), 0) AS recebidoAno,
            ISNULL(SUM(RecebePgtoDiv.PercentValor_Rpd), 0) AS recebidoTotal
        FROM Recebidas WITH(NOLOCK)
        INNER JOIN RecebePgtoDiv WITH(NOLOCK)
            ON Recebidas.Empresa_Rec = RecebePgtoDiv.Empresa_Rpd
            AND Recebidas.Obra_Rec = RecebePgtoDiv.Obra_Rpd
            AND Recebidas.NumVend_Rec = RecebePgtoDiv.NumVend_Rpd
            AND Recebidas.NumParc_Rec = RecebePgtoDiv.NumParc_Rpd
            AND Recebidas.ParcType_Rec = RecebePgtoDiv.ParcType_Rpd
            AND Recebidas.Tipo_Rec = RecebePgtoDiv.Tipo_Rpd
            AND Recebidas.NumParcGer_Rec = RecebePgtoDiv.NumParcGer_Rpd
        INNER JOIN RecebePgto WITH(NOLOCK)
            ON RecebePgtoDiv.Empresa_Rpd = RecebePgto.Empresa_Rpg
            AND RecebePgtoDiv.NumReceb_Rpd = RecebePgto.NumReceb_Rpg
            AND RecebePgtoDiv.TipoRpg_Rpd = RecebePgto.Tipo_Rpg
            AND RecebePgtoDiv.NumCont_Rpd = RecebePgto.NumCont_Rpg
            AND RecebePgto.Status_Rpg <> 2
        INNER JOIN Depositos WITH(NOLOCK)
            ON RecebePgto.Empresa_Rpg = Depositos.Empresa_Dep
            AND RecebePgto.NumDep_Rpg = Depositos.Numero_Dep
            AND RecebePgto.BancoDep_Rpg = Depositos.Banco_Dep
            AND RecebePgto.ContaDep_Rpg = Depositos.Conta_Dep
        INNER JOIN Extrato WITH(NOLOCK)
            ON Depositos.Empresa_Dep = Extrato.Empresa_Doc
            AND Depositos.Banco_Dep = Extrato.Banco_Doc
            AND Depositos.Conta_Dep = Extrato.Conta_Doc
            AND Depositos.Numero_Dep = Extrato.Numero_Doc
            AND Extrato.Tipo_Doc = 1
        WHERE Recebidas.Empresa_Rec = {empresa} 
          AND Recebidas.Obra_Rec = '{obra}' 
          AND Recebidas.Status_Rec = 1
        """
        recebimentos_result = execute_query(recebimentos_query)
        recebimentos = recebimentos_result[0] if recebimentos_result else {}
    except Exception as e:
        print(f"Erro recebimentos: {e}")
        
    try:
        # ========== INADIMPLÊNCIA ==========
        inadimplencia_query = f"""
        SELECT 
            COUNT(*) AS parcelasAtrasadas,
            ISNULL(SUM(Valor_Prc), 0) AS valorAtrasado
        FROM ContasReceber WITH(NOLOCK)
        WHERE Empresa_prc = {empresa} 
          AND Obra_Prc = '{obra}'
          AND Status_Prc = 0
          AND Data_Prc < CAST(GETDATE() AS DATE)
          AND Tipo_Prc != '1'
        """
        inadimplencia_result = execute_query(inadimplencia_query)
        inadimplencia = inadimplencia_result[0] if inadimplencia_result else {}
    except Exception as e:
        print(f"Erro inadimplencia: {e}")
        
    try:
        # ========== ESTOQUE ==========
        # Usando Vendido_unid (campo correto com valores numéricos)
        estoque_query = f"""
        SELECT 
            SUM(CASE WHEN Vendido_unid = 0 THEN 1 ELSE 0 END) AS disponivel,
            SUM(CASE WHEN Vendido_unid = 2 THEN 1 ELSE 0 END) AS reservado,
            SUM(CASE WHEN Vendido_unid = 1 THEN 1 ELSE 0 END) AS vendido,
            SUM(CASE WHEN Vendido_unid = 4 THEN 1 ELSE 0 END) AS quitado,
            SUM(CASE WHEN Vendido_unid = 7 THEN 1 ELSE 0 END) AS suspenso,
            SUM(CASE WHEN Vendido_unid = 8 THEN 1 ELSE 0 END) AS foraVenda,
            COUNT(*) AS total
        FROM UnidadePer WITH(NOLOCK)
        WHERE Empresa_unid = {empresa} AND Obra_unid = '{obra}'
        """
        estoque_result = execute_query(estoque_query)
        estoque = estoque_result[0] if estoque_result else {}
    except Exception as e:
        print(f"Erro estoque: {e}")
    
    try:
        # ========== RECEBIMENTOS DIÁRIOS (últimos 30 dias - data conciliação) ==========
        recebimentos_diarios_query = f"""
        SELECT 
            FORMAT(Extrato.Data_Doc, 'yyyy-MM-dd') AS data,
            FORMAT(Extrato.Data_Doc, 'dd/MM') AS dataFormatada,
            ISNULL(SUM(RecebePgtoDiv.PercentValor_Rpd), 0) AS valor
        FROM Recebidas WITH(NOLOCK)
        INNER JOIN RecebePgtoDiv WITH(NOLOCK)
            ON Recebidas.Empresa_Rec = RecebePgtoDiv.Empresa_Rpd
            AND Recebidas.Obra_Rec = RecebePgtoDiv.Obra_Rpd
            AND Recebidas.NumVend_Rec = RecebePgtoDiv.NumVend_Rpd
            AND Recebidas.NumParc_Rec = RecebePgtoDiv.NumParc_Rpd
            AND Recebidas.ParcType_Rec = RecebePgtoDiv.ParcType_Rpd
            AND Recebidas.Tipo_Rec = RecebePgtoDiv.Tipo_Rpd
            AND Recebidas.NumParcGer_Rec = RecebePgtoDiv.NumParcGer_Rpd
        INNER JOIN RecebePgto WITH(NOLOCK)
            ON RecebePgtoDiv.Empresa_Rpd = RecebePgto.Empresa_Rpg
            AND RecebePgtoDiv.NumReceb_Rpd = RecebePgto.NumReceb_Rpg
            AND RecebePgtoDiv.TipoRpg_Rpd = RecebePgto.Tipo_Rpg
            AND RecebePgtoDiv.NumCont_Rpd = RecebePgto.NumCont_Rpg
            AND RecebePgto.Status_Rpg <> 2
        INNER JOIN Depositos WITH(NOLOCK)
            ON RecebePgto.Empresa_Rpg = Depositos.Empresa_Dep
            AND RecebePgto.NumDep_Rpg = Depositos.Numero_Dep
            AND RecebePgto.BancoDep_Rpg = Depositos.Banco_Dep
            AND RecebePgto.ContaDep_Rpg = Depositos.Conta_Dep
        INNER JOIN Extrato WITH(NOLOCK)
            ON Depositos.Empresa_Dep = Extrato.Empresa_Doc
            AND Depositos.Banco_Dep = Extrato.Banco_Doc
            AND Depositos.Conta_Dep = Extrato.Conta_Doc
            AND Depositos.Numero_Dep = Extrato.Numero_Doc
            AND Extrato.Tipo_Doc = 1
        WHERE Recebidas.Empresa_Rec = {empresa} 
          AND Recebidas.Obra_Rec = '{obra}' 
          AND Recebidas.Status_Rec = 1
          AND Extrato.Data_Doc >= DATEADD(DAY, -30, GETDATE())
        GROUP BY FORMAT(Extrato.Data_Doc, 'yyyy-MM-dd'), FORMAT(Extrato.Data_Doc, 'dd/MM')
        ORDER BY FORMAT(Extrato.Data_Doc, 'yyyy-MM-dd')
        """
        recebimentos_db = execute_query(recebimentos_diarios_query) or []
        
        # Create a dict from database results
        recebimentos_dict = {r['data']: r for r in recebimentos_db}
        
        # Generate all 30 days and fill missing with 0
        recebimentos_diarios = []
        for i in range(30, -1, -1):  # 30 days ago to today
            dia = datetime.now() - timedelta(days=i)
            data_str = dia.strftime('%Y-%m-%d')
            data_formatada = dia.strftime('%d/%m')
            
            if data_str in recebimentos_dict:
                recebimentos_diarios.append({
                    'data': data_str,
                    'dataFormatada': data_formatada,
                    'valor': float(recebimentos_dict[data_str]['valor'] or 0)
                })
            else:
                recebimentos_diarios.append({
                    'data': data_str,
                    'dataFormatada': data_formatada,
                    'valor': 0.0
                })
    except Exception as e:
        print(f"Erro recebimentos diarios: {e}")
    
    try:
        # ========== SINAIS PAGOS ==========
        sinais_query = f"""
        SELECT 
            COUNT(*) AS sinaisPagos,
            ISNULL(SUM(Valor_Rec + ISNULL(ValorConf_Rec,0)), 0) AS valorSinaisPagos
        FROM Recebidas WITH(NOLOCK)
        WHERE Empresa_Rec = {empresa} 
          AND Obra_Rec = '{obra}' 
          AND Status_Rec = 1
          AND Tipo_Rec = 'S'
        """
        sinais_result = execute_query(sinais_query)
        sinais = sinais_result[0] if sinais_result else {}
    except Exception as e:
        print(f"Erro sinais: {e}")
    
    return {
        "vendas": {
            "total": vendas.get('totalVendas', 0) or 0,
            "valorTotal": float(vendas.get('valorTotal', 0) or 0),
            "mes": vendas.get('vendasMes', 0) or 0,
            "valorMes": float(vendas.get('valorMes', 0) or 0),
            "ano": vendas.get('vendasAno', 0) or 0,
            "valorAno": float(vendas.get('valorAno', 0) or 0),
            "hoje": vendas.get('vendasHoje', 0) or 0,
            "valorHoje": float(vendas.get('valorHoje', 0) or 0)
        },
        "recebimentos": {
            "hoje": float(recebimentos.get('recebidoHoje', 0) or 0),
            "mes": float(recebimentos.get('recebidoMes', 0) or 0),
            "ano": float(recebimentos.get('recebidoAno', 0) or 0),
            "total": float(recebimentos.get('recebidoTotal', 0) or 0)
        },
        "inadimplencia": {
            "parcelas": inadimplencia.get('parcelasAtrasadas', 0) or 0,
            "valor": float(inadimplencia.get('valorAtrasado', 0) or 0)
        },
        "estoque": {
            "disponivel": estoque.get('disponivel', 0) or 0,
            "reservado": estoque.get('reservado', 0) or 0,
            "vendido": estoque.get('vendido', 0) or 0,
            "quitado": estoque.get('quitado', 0) or 0,
            "suspenso": estoque.get('suspenso', 0) or 0,
            "foraVenda": estoque.get('foraVenda', 0) or 0,
            "total": estoque.get('total', 0) or 0
        },
        "sinais": {
            "pagos": sinais.get('sinaisPagos', 0) or 0,
            "valorPago": float(sinais.get('valorSinaisPagos', 0) or 0)
        },
        "recebimentosDiarios": recebimentos_diarios,
        "dataAtualizacao": datetime.now().strftime('%d/%m/%Y %H:%M')
    }

