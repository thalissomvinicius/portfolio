"""
VallePrime Dashboard - Recebimentos Routes
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from datetime import date, datetime
from database import execute_query
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus.flowables import HRFlowable
import traceback

router = APIRouter()

# Contas bancarias por empresa
CONTAS_POR_EMPRESA = {
    28: ("'13005587-5'", "'529-5'", "'529-0'", "'27083-6'"),
    29: ("'13005588-2'", "'549-0'", "'31714-8'"),
}

@router.get("/recebimentos")
async def get_recebimentos(
    empresa: int = Query(..., description="Codigo da empresa"),
    obra: str = Query(..., description="Codigo da obra"),
    data_inicio: str = Query("", description="Data inicio"),
    data_fim: str = Query("", description="Data fim"),
    corretor: str = Query("", description="Filtrar por corretor")
):
    """Retorna recebimentos/depositos conciliados no periodo"""
    
    contas = CONTAS_POR_EMPRESA.get(empresa, CONTAS_POR_EMPRESA[28])
    contas_filter = f"({','.join(contas)})"
    
    def format_date(d):
        if not d:
            return ""
        if '-' in d:
            parts = d.split('-')
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        return d
    
    data_inicio_fmt = format_date(data_inicio)
    data_fim_fmt = format_date(data_fim)
    
    if data_inicio_fmt and data_fim_fmt:
        date_filter = f"AND Extrato.Data_Doc BETWEEN '{data_inicio_fmt}' AND '{data_fim_fmt}'"
    elif data_inicio_fmt:
        date_filter = f"AND Extrato.Data_Doc >= '{data_inicio_fmt}'"
    elif data_fim_fmt:
        date_filter = f"AND Extrato.Data_Doc <= '{data_fim_fmt}'"
    else:
        date_filter = ""
    
    # Filtro de corretor
    corretor_filter = f"AND UPPER(PessoasVendedor.nome_pes) = '{corretor}'" if corretor else ""
    
    query = f"""
    SELECT
        VendasRecebidas.Num_VRec as venda,
        VendasRecebidas.Cliente_VRec as codCliente,
        UPPER(Pessoas.Nome_Pes) as nomeCliente,
        UPPER(UnidVenda.Identificador_Unid) as identificador,
        ISNULL(UnidVenda.C1_unid, '') as quadra,
        ISNULL(UnidVenda.C2_unid, '') as lote,
        CONCAT(Recebidas.NumParc_Rec, '/', Recebidas.TotParc_Rec) as parcela,
        Recebidas.Tipo_Rec + ' - ' + UPPER(Parcelas.Descricao_Par) as tipoParcela,
        FORMAT(Recebidas.DataVenci_Rec, 'dd/MM/yyyy') as dataVencimento,
        FORMAT(Depositos.Data_Dep, 'dd/MM/yyyy') as dataDeposito,
        FORMAT(Extrato.Data_Doc, 'dd/MM/yyyy') as dataConciliacao,
        FORMAT(Recebidas.Data_Rec, 'dd/MM/yyyy') as dataRecebimento,
        RecebePgtoDiv.PercentValor_Rpd * (CAST((ItensRecebidas.Qtde_Itr * ItensRecebidas.PrecoProc_Itr - ItensRecebidas.ValComissaoDir_Itr) AS NUMERIC(18, 6)) / NULLIF(VendasRecebidas.ValorTot_VRec, 0)) as valorPago,
        Recebidas.ValorPrincipalPrice_rec as valorPrincipal,
        Recebidas.VlCorrecao_Rec + Recebidas.VlCorrecaoConf_Rec as correcao,
        Recebidas.VlMulta_Rec + Recebidas.VlMultaConf_Rec as multa,
        Recebidas.VlJurosParc_Rec + Recebidas.VlJurosParcConf_Rec + Recebidas.VlJuros_Rec + Recebidas.VlJurosConf_Rec as juros,
        CASE
            WHEN DATEDIFF(MONTH, Recebidas.DataVenci_Rec, Recebidas.Data_Rec) < 0 THEN 'ADIANTADA'
            WHEN DATEDIFF(MONTH, Recebidas.DataVenci_Rec, Recebidas.Data_Rec) = 0 THEN 'NORMAL'
            WHEN DATEDIFF(MONTH, Recebidas.DataVenci_Rec, Recebidas.Data_Rec) > 0 THEN 'ATRASADA'
        END as status,
        CAST(Extrato.Banco_Doc AS VARCHAR) + ' - ' + UPPER(Bancos.Nome_Banco) as banco,
        Extrato.Conta_Doc as conta,
        Extrato.Conta_Doc + ' - ' + UPPER(CCorrente.Descri_Banco) as descricaoConta,
        UPPER(ISNULL(COALESCE(PessoasVendedor.nome_pes, PessoasVendedorVRec.nome_pes), 'NAO INFORMADO')) as corretor
    FROM
    (
        SELECT *
        FROM Extrato WITH(NOLOCK)
        WHERE Tipo_Doc = 1
            {date_filter}
            AND Empresa_doc = {empresa}
            AND Conta_doc IN {contas_filter}
    ) [Extrato]
    INNER JOIN Depositos WITH(NOLOCK)
        ON Extrato.Empresa_Doc = Depositos.Empresa_Dep
        AND Extrato.Banco_Doc = Depositos.Banco_Dep
        AND Extrato.Conta_Doc = Depositos.Conta_Dep
        AND Extrato.Numero_Doc = Depositos.Numero_Dep
    INNER JOIN (
        SELECT * FROM RecebePgto WITH(NOLOCK) WHERE Status_Rpg <> 2
    ) [RecebePgto]
        ON Depositos.Empresa_Dep = RecebePgto.Empresa_Rpg
        AND Depositos.Numero_Dep = RecebePgto.NumDep_Rpg
        AND Depositos.Banco_Dep = RecebePgto.BancoDep_Rpg
        AND Depositos.Conta_Dep = RecebePgto.ContaDep_Rpg
    INNER JOIN RecebePgtoDiv WITH(NOLOCK)
        ON RecebePgto.Empresa_Rpg = RecebePgtoDiv.Empresa_Rpd
        AND RecebePgto.NumReceb_Rpg = RecebePgtoDiv.NumReceb_Rpd
        AND RecebePgto.Tipo_Rpg = RecebePgtoDiv.TipoRpg_Rpd
        AND RecebePgto.NumCont_Rpg = RecebePgtoDiv.NumCont_Rpd
    INNER JOIN Recebidas WITH(NOLOCK)
        ON RecebePgtoDiv.Empresa_Rpd = Recebidas.Empresa_Rec
        AND RecebePgtoDiv.Obra_Rpd = Recebidas.Obra_Rec
        AND RecebePgtoDiv.NumVend_Rpd = Recebidas.NumVend_Rec
        AND RecebePgtoDiv.NumParc_Rpd = Recebidas.NumParc_Rec
        AND RecebePgtoDiv.ParcType_Rpd = Recebidas.ParcType_Rec
        AND RecebePgtoDiv.Tipo_Rpd = Recebidas.Tipo_Rec
        AND RecebePgtoDiv.NumParcGer_Rpd = Recebidas.NumParcGer_Rec
    INNER JOIN VendasRecebidas WITH(NOLOCK)
        ON Recebidas.Empresa_Rec = VendasRecebidas.Empresa_VRec
        AND Recebidas.Obra_Rec = VendasRecebidas.Obra_VRec
        AND Recebidas.NumVend_Rec = VendasRecebidas.Num_VRec
    INNER JOIN ItensRecebidas WITH(NOLOCK)
        ON VendasRecebidas.Empresa_VRec = ItensRecebidas.Empresa_Itr
        AND VendasRecebidas.Obra_VRec = ItensRecebidas.Obra_Itr
        AND VendasRecebidas.Num_VRec = ItensRecebidas.NumVend_Itr
    LEFT JOIN UnidadePer WITH(NOLOCK)
        ON ItensRecebidas.Empresa_Itr = UnidadePer.Empresa_Unid
        AND ItensRecebidas.Produto_Itr = UnidadePer.Prod_Unid
        AND ItensRecebidas.CodPerson_Itr = UnidadePer.NumPer_Unid
    LEFT JOIN ItensVenda WITH(NOLOCK) 
        ON VendasRecebidas.Empresa_VRec = ItensVenda.Empresa_itv 
        AND VendasRecebidas.Obra_VRec = ItensVenda.Obra_Itv 
        AND VendasRecebidas.Num_VRec = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer UnidVenda WITH(NOLOCK) 
        ON ItensVenda.Empresa_itv = UnidVenda.Empresa_unid 
        AND ItensVenda.Produto_Itv = UnidVenda.Prod_unid 
        AND ItensVenda.CodPerson_Itv = UnidVenda.NumPer_unid
    INNER JOIN Empresas WITH(NOLOCK)
        ON Recebidas.Empresa_Rec = Empresas.Codigo_Emp
    INNER JOIN Obras WITH(NOLOCK)
        ON Recebidas.Empresa_Rec = Obras.Empresa_Obr
        AND Recebidas.Obra_Rec = Obras.Cod_Obr
    LEFT JOIN CCorrente WITH(NOLOCK)
        ON Extrato.Banco_Doc = CCorrente.Numero_Banco
        AND Extrato.Conta_Doc = CCorrente.Conta_Banco
        AND Extrato.Empresa_Doc = CCorrente.Empresa_Banco
    LEFT JOIN Bancos WITH(NOLOCK)
        ON Extrato.Banco_Doc = Bancos.Numero_Banco
    INNER JOIN Pessoas WITH(NOLOCK)
        ON VendasRecebidas.Cliente_VRec = Pessoas.Cod_Pes
    INNER JOIN PrdSrv WITH(NOLOCK)
        ON ItensRecebidas.Produto_Itr = PrdSrv.NumProd_Psc
    INNER JOIN Parcelas WITH(NOLOCK)
        ON Recebidas.Tipo_Rec = Parcelas.Tipo_Par
    LEFT JOIN Vendas WITH(NOLOCK)
        ON Recebidas.Empresa_Rec = Vendas.Empresa_Ven
        AND Recebidas.Obra_Rec = Vendas.Obra_Ven
        AND Recebidas.NumVend_Rec = Vendas.Num_Ven
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK)
        ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    LEFT JOIN Pessoas AS PessoasVendedorVRec WITH(NOLOCK)
        ON VendasRecebidas.Vendedor_VRec = PessoasVendedorVRec.cod_pes
    WHERE 1=1
        {corretor_filter}
    ORDER BY VendasRecebidas.Num_VRec, Recebidas.NumParc_Rec
    """
    
    try:
        results = execute_query(query)
        total_recebido = sum(float(r.get('valorPago', 0) or 0) for r in results)
        total_principal = sum(float(r.get('valorPrincipal', 0) or 0) for r in results)
        qtd_parcelas = len(results)
        adiantadas = sum(1 for r in results if r.get('status') == 'ADIANTADA')
        normais = sum(1 for r in results if r.get('status') == 'NORMAL')
        atrasadas = sum(1 for r in results if r.get('status') == 'ATRASADA')
        
        # Breakdown por tipo de parcela
        tipo_breakdown = {}
        for r in results:
            tipo = r.get('tipoParcela', 'OUTRO')
            valor = float(r.get('valorPago', 0) or 0)
            if tipo not in tipo_breakdown:
                tipo_breakdown[tipo] = {'qtd': 0, 'valor': 0}
            tipo_breakdown[tipo]['qtd'] += 1
            tipo_breakdown[tipo]['valor'] += valor
        
        # Ordenar por valor total desc
        tipo_sorted = sorted(tipo_breakdown.items(), key=lambda x: x[1]['valor'], reverse=True)
        tipo_list = [{'tipo': k, 'qtd': v['qtd'], 'valor': v['valor']} for k, v in tipo_sorted]
        
        return {
            "data": results,
            "totais": {
                "totalRecebido": total_recebido,
                "totalPrincipal": total_principal,
                "qtdParcelas": qtd_parcelas,
                "adiantadas": adiantadas,
                "normais": normais,
                "atrasadas": atrasadas,
                "porTipo": tipo_list
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/a-receber")
async def get_a_receber(
    empresa: int = Query(..., description="Codigo da empresa"),
    obra: str = Query(..., description="Codigo da obra"),
    tipo: str = Query("sinais", description="Tipo: 'sinais' ou 'completo'")
):
    """Retorna resumo de valores a receber (em aberto)"""
    
    tipo_filter = "AND ContasReceber.Tipo_Prc = 'S'" if tipo == "sinais" else ""
    
    resumo_query = f"""
    SELECT
        ContasReceber.Tipo_Prc as tipoCodigo,
        Parcelas.Descricao_Par as tipoDescricao,
        COUNT(*) as qtdParcelas,
        SUM(ContasReceber.Valor_Prc) as totalValor,
        SUM(CASE WHEN ContasReceber.Data_Prc < CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as vencidos,
        SUM(CASE WHEN ContasReceber.Data_Prc < CAST(GETDATE() AS DATE) THEN ContasReceber.Valor_Prc ELSE 0 END) as valorVencido,
        SUM(CASE WHEN ContasReceber.Data_Prc >= CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as aVencer,
        SUM(CASE WHEN ContasReceber.Data_Prc >= CAST(GETDATE() AS DATE) THEN ContasReceber.Valor_Prc ELSE 0 END) as valorAVencer
    FROM ContasReceber WITH(NOLOCK)
    INNER JOIN Parcelas WITH(NOLOCK) ON ContasReceber.Tipo_Prc = Parcelas.Tipo_Par
    WHERE ContasReceber.Empresa_prc = {empresa}
        AND ContasReceber.Obra_Prc = '{obra}'
        AND ContasReceber.Status_Prc = 0
        {tipo_filter}
    GROUP BY ContasReceber.Tipo_Prc, Parcelas.Descricao_Par
    ORDER BY SUM(ContasReceber.Valor_Prc) DESC
    """
    
    totais_query = f"""
    SELECT
        COUNT(*) as qtdParcelas,
        SUM(ContasReceber.Valor_Prc) as totalValor,
        SUM(CASE WHEN ContasReceber.Data_Prc < CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as vencidos,
        SUM(CASE WHEN ContasReceber.Data_Prc < CAST(GETDATE() AS DATE) THEN ContasReceber.Valor_Prc ELSE 0 END) as valorVencido,
        SUM(CASE WHEN ContasReceber.Data_Prc = CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as hoje,
        SUM(CASE WHEN ContasReceber.Data_Prc > CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as aVencer
    FROM ContasReceber WITH(NOLOCK)
    WHERE ContasReceber.Empresa_prc = {empresa}
        AND ContasReceber.Obra_Prc = '{obra}'
        AND ContasReceber.Status_Prc = 0
        {tipo_filter}
    """
    
    try:
        resumo = execute_query(resumo_query)
        totais_result = execute_query(totais_query)
        
        totais = totais_result[0] if totais_result else {
            'qtdParcelas': 0, 'totalValor': 0, 'vencidos': 0, 
            'valorVencido': 0, 'hoje': 0, 'aVencer': 0
        }
        
        return {
            "data": resumo,
            "totais": {
                "totalValor": float(totais.get('totalValor', 0) or 0),
                "qtdParcelas": int(totais.get('qtdParcelas', 0) or 0),
                "vencidos": int(totais.get('vencidos', 0) or 0),
                "valorVencido": float(totais.get('valorVencido', 0) or 0),
                "hoje": int(totais.get('hoje', 0) or 0),
                "aVencer": int(totais.get('aVencer', 0) or 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/relatorio-pdf")
async def get_relatorio_pdf(
    empresa: int = Query(..., description="Codigo da empresa"),
    obra: str = Query(..., description="Codigo da obra"),
    data_inicio: str = Query(..., description="Data inicio (yyyy-mm-dd)"),
    data_fim: str = Query(..., description="Data fim (yyyy-mm-dd)"),
    tipo_a_receber: str = Query("sinais", description="Tipo a receber")
):
    """Gera relatorio PDF com recebimentos diarios e valores a receber"""
    
    contas = CONTAS_POR_EMPRESA.get(empresa, CONTAS_POR_EMPRESA[28])
    contas_filter = f"({','.join(contas)})"
    
    def format_date(d):
        if '-' in d:
            parts = d.split('-')
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        return d
    
    data_inicio_fmt = format_date(data_inicio)
    data_fim_fmt = format_date(data_fim)
    
    # Buscar nome da obra
    obra_query = f"SELECT Descr_Obr FROM Obras WITH(NOLOCK) WHERE Empresa_Obr = {empresa} AND Cod_Obr = '{obra}'"
    obra_result = execute_query(obra_query)
    nome_obra = obra_result[0].get('Descr_Obr', '') if obra_result else obra
    
    # Query: Recebimentos diarios
    recebimentos_query = f"""
    SELECT
        FORMAT(Extrato.Data_Doc, 'dd/MM/yyyy') as data,
        COUNT(*) as qtdParcelas,
        SUM(RecebePgtoDiv.PercentValor_Rpd * (CAST((ItensRecebidas.Qtde_Itr * ItensRecebidas.PrecoProc_Itr - ItensRecebidas.ValComissaoDir_Itr) AS NUMERIC(18, 6)) / NULLIF(VendasRecebidas.ValorTot_VRec, 0))) as totalRecebido
    FROM Extrato WITH(NOLOCK)
    INNER JOIN Depositos WITH(NOLOCK)
        ON Extrato.Empresa_Doc = Depositos.Empresa_Dep
        AND Extrato.Banco_Doc = Depositos.Banco_Dep
        AND Extrato.Conta_Doc = Depositos.Conta_Dep
        AND Extrato.Numero_Doc = Depositos.Numero_Dep
    INNER JOIN RecebePgto WITH(NOLOCK)
        ON Depositos.Empresa_Dep = RecebePgto.Empresa_Rpg
        AND Depositos.Numero_Dep = RecebePgto.NumDep_Rpg
        AND Depositos.Banco_Dep = RecebePgto.BancoDep_Rpg
        AND Depositos.Conta_Dep = RecebePgto.ContaDep_Rpg
        AND RecebePgto.Status_Rpg <> 2
    INNER JOIN RecebePgtoDiv WITH(NOLOCK)
        ON RecebePgto.Empresa_Rpg = RecebePgtoDiv.Empresa_Rpd
        AND RecebePgto.NumReceb_Rpg = RecebePgtoDiv.NumReceb_Rpd
        AND RecebePgto.Tipo_Rpg = RecebePgtoDiv.TipoRpg_Rpd
        AND RecebePgto.NumCont_Rpg = RecebePgtoDiv.NumCont_Rpd
    INNER JOIN Recebidas WITH(NOLOCK)
        ON RecebePgtoDiv.Empresa_Rpd = Recebidas.Empresa_Rec
        AND RecebePgtoDiv.Obra_Rpd = Recebidas.Obra_Rec
        AND RecebePgtoDiv.NumVend_Rpd = Recebidas.NumVend_Rec
        AND RecebePgtoDiv.NumParc_Rpd = Recebidas.NumParc_Rec
        AND RecebePgtoDiv.ParcType_Rpd = Recebidas.ParcType_Rec
        AND RecebePgtoDiv.Tipo_Rpd = Recebidas.Tipo_Rec
        AND RecebePgtoDiv.NumParcGer_Rpd = Recebidas.NumParcGer_Rec
    INNER JOIN VendasRecebidas WITH(NOLOCK)
        ON Recebidas.Empresa_Rec = VendasRecebidas.Empresa_VRec
        AND Recebidas.Obra_Rec = VendasRecebidas.Obra_VRec
        AND Recebidas.NumVend_Rec = VendasRecebidas.Num_VRec
    INNER JOIN ItensRecebidas WITH(NOLOCK)
        ON VendasRecebidas.Empresa_VRec = ItensRecebidas.Empresa_Itr
        AND VendasRecebidas.Obra_VRec = ItensRecebidas.Obra_Itr
        AND VendasRecebidas.Num_VRec = ItensRecebidas.NumVend_Itr
    WHERE Extrato.Tipo_Doc = 1
        AND Extrato.Data_Doc BETWEEN '{data_inicio_fmt}' AND '{data_fim_fmt}'
        AND Extrato.Empresa_doc = {empresa}
        AND Extrato.Conta_doc IN {contas_filter}
    GROUP BY Extrato.Data_Doc
    ORDER BY Extrato.Data_Doc
    """
    
    # Query: Sinais totais
    sinais_totais_query = f"""
    SELECT
        COUNT(*) as qtdSinais,
        SUM(ContasReceber.Valor_Prc) as valorTotal,
        SUM(CASE WHEN ContasReceber.Data_Prc < CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as vencidos,
        SUM(CASE WHEN ContasReceber.Data_Prc < CAST(GETDATE() AS DATE) THEN ContasReceber.Valor_Prc ELSE 0 END) as valorVencido
    FROM ContasReceber WITH(NOLOCK)
    WHERE ContasReceber.Empresa_prc = {empresa}
        AND ContasReceber.Obra_Prc = '{obra}'
        AND ContasReceber.Status_Prc = 0
        AND ContasReceber.Tipo_Prc = 'S'
    """
    
    # Query 1: Sinais em aberto por corretor (QTD, TOTAL GERADO, EM ABERTO, VENCIDOS)
    sinais_aberto_query = f"""
    SELECT
        ISNULL(PessoasVendedor.nome_pes, 'Nao informado') AS corretor,
        COUNT(*) as qtdSinais,
        SUM(ContasReceber.Valor_Prc) as valorTotal,
        SUM(CASE WHEN ContasReceber.Data_Prc < CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as vencidos,
        SUM(CASE WHEN ContasReceber.Data_Prc < CAST(GETDATE() AS DATE) THEN ContasReceber.Valor_Prc ELSE 0 END) as valorVencido
    FROM ContasReceber WITH(NOLOCK)
    INNER JOIN Vendas WITH(NOLOCK) 
        ON ContasReceber.Empresa_prc = Vendas.Empresa_Ven
        AND ContasReceber.Obra_Prc = Vendas.Obra_Ven
        AND ContasReceber.NumVend_prc = Vendas.Num_Ven
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) 
        ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    WHERE ContasReceber.Empresa_prc = {empresa}
        AND ContasReceber.Obra_Prc = '{obra}'
        AND ContasReceber.Status_Prc = 0
        AND ContasReceber.Tipo_Prc = 'S'
    GROUP BY PessoasVendedor.nome_pes
    """

    # Query 2: Recebidos por corretor - usando ESTRUTURA IDÊNTICA ao get_recebimentos
    # Inclui as mesmas subqueries de Extrato e RecebePgto para garantir match exato
    recebidos_corretor_query = f"""
    SELECT
        UPPER(ISNULL(COALESCE(PessoasVendedor.nome_pes, PessoasVendedorVRec.nome_pes), 'NAO INFORMADO')) AS corretor,
        SUM(RecebePgtoDiv.PercentValor_Rpd * (CAST((ItensRecebidas.Qtde_Itr * ItensRecebidas.PrecoProc_Itr - ItensRecebidas.ValComissaoDir_Itr) AS NUMERIC(18, 6)) / NULLIF(VendasRecebidas.ValorTot_VRec, 0))) as valorRecebido
    FROM
    (
        SELECT *
        FROM Extrato WITH(NOLOCK)
        WHERE Tipo_Doc = 1
            AND Data_Doc BETWEEN '{data_inicio_fmt}' AND '{data_fim_fmt}'
            AND Empresa_doc = {empresa}
            AND Conta_doc IN {contas_filter}
    ) [Extrato]
    INNER JOIN Depositos WITH(NOLOCK)
        ON Extrato.Empresa_Doc = Depositos.Empresa_Dep
        AND Extrato.Banco_Doc = Depositos.Banco_Dep
        AND Extrato.Conta_Doc = Depositos.Conta_Dep
        AND Extrato.Numero_Doc = Depositos.Numero_Dep
    INNER JOIN (
        SELECT * FROM RecebePgto WITH(NOLOCK) WHERE Status_Rpg <> 2
    ) [RecebePgto]
        ON Depositos.Empresa_Dep = RecebePgto.Empresa_Rpg
        AND Depositos.Numero_Dep = RecebePgto.NumDep_Rpg
        AND Depositos.Banco_Dep = RecebePgto.BancoDep_Rpg
        AND Depositos.Conta_Dep = RecebePgto.ContaDep_Rpg
    INNER JOIN RecebePgtoDiv WITH(NOLOCK)
        ON RecebePgto.Empresa_Rpg = RecebePgtoDiv.Empresa_Rpd
        AND RecebePgto.NumReceb_Rpg = RecebePgtoDiv.NumReceb_Rpd
        AND RecebePgto.Tipo_Rpg = RecebePgtoDiv.TipoRpg_Rpd
        AND RecebePgto.NumCont_Rpg = RecebePgtoDiv.NumCont_Rpd
    INNER JOIN Recebidas WITH(NOLOCK)
        ON RecebePgtoDiv.Empresa_Rpd = Recebidas.Empresa_Rec
        AND RecebePgtoDiv.Obra_Rpd = Recebidas.Obra_Rec
        AND RecebePgtoDiv.NumVend_Rpd = Recebidas.NumVend_Rec
        AND RecebePgtoDiv.NumParc_Rpd = Recebidas.NumParc_Rec
        AND RecebePgtoDiv.ParcType_Rpd = Recebidas.ParcType_Rec
        AND RecebePgtoDiv.Tipo_Rpd = Recebidas.Tipo_Rec
        AND RecebePgtoDiv.NumParcGer_Rpd = Recebidas.NumParcGer_Rec
    INNER JOIN VendasRecebidas WITH(NOLOCK)
        ON Recebidas.Empresa_Rec = VendasRecebidas.Empresa_VRec
        AND Recebidas.Obra_Rec = VendasRecebidas.Obra_VRec
        AND Recebidas.NumVend_Rec = VendasRecebidas.Num_VRec
    INNER JOIN ItensRecebidas WITH(NOLOCK)
        ON VendasRecebidas.Empresa_VRec = ItensRecebidas.Empresa_Itr
        AND VendasRecebidas.Obra_VRec = ItensRecebidas.Obra_Itr
        AND VendasRecebidas.Num_VRec = ItensRecebidas.NumVend_Itr
    LEFT JOIN Vendas WITH(NOLOCK)
        ON Recebidas.Empresa_Rec = Vendas.Empresa_Ven
        AND Recebidas.Obra_Rec = Vendas.Obra_Ven
        AND Recebidas.NumVend_Rec = Vendas.Num_Ven
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK)
        ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    LEFT JOIN Pessoas AS PessoasVendedorVRec WITH(NOLOCK)
        ON VendasRecebidas.Vendedor_VRec = PessoasVendedorVRec.cod_pes
    WHERE Recebidas.Tipo_Rec = 'S'
    GROUP BY COALESCE(PessoasVendedor.nome_pes, PessoasVendedorVRec.nome_pes)
    """
    
    try:
        recebimentos = execute_query(recebimentos_query)
        sinais_totais_result = execute_query(sinais_totais_query)
        sinais_aberto = execute_query(sinais_aberto_query)
        recebidos_corretor = execute_query(recebidos_corretor_query)
        
        sinais_totais = sinais_totais_result[0] if sinais_totais_result else {
            'qtdSinais': 0, 'valorTotal': 0, 'vencidos': 0, 'valorVencido': 0
        }
        
        # Combinar sinais em aberto com recebidos em Python
        corretor_map = {}
        for s in sinais_aberto:
            nome = s.get('corretor', 'Nao informado') or 'Nao informado'
            corretor_map[nome.upper()] = {
                'corretor': nome,
                'qtdSinais': int(s.get('qtdSinais', 0) or 0),
                'valorTotal': float(s.get('valorTotal', 0) or 0),
                'valorRecebido': 0,  # será preenchido abaixo
                'vencidos': int(s.get('vencidos', 0) or 0),
                'valorVencido': float(s.get('valorVencido', 0) or 0)
            }
        
        # Adicionar valorRecebido de cada corretor
        for r in recebidos_corretor:
            nome = r.get('corretor', 'NAO INFORMADO') or 'NAO INFORMADO'
            valor = float(r.get('valorRecebido', 0) or 0)
            if nome.upper() in corretor_map:
                corretor_map[nome.upper()]['valorRecebido'] = valor
            else:
                # Corretor só tem recebido, sem sinais em aberto
                corretor_map[nome.upper()] = {
                    'corretor': nome,
                    'qtdSinais': 0,
                    'valorTotal': 0,
                    'valorRecebido': valor,
                    'vencidos': 0,
                    'valorVencido': 0
                }
        
        # Converter para lista ordenada por valorTotal
        sinais_corretor = sorted(corretor_map.values(), key=lambda x: x['valorTotal'], reverse=True)
        
        # PDF Generation with professional design
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            topMargin=15*mm, 
            bottomMargin=15*mm,
            leftMargin=12*mm,
            rightMargin=12*mm
        )
        elements = []
        styles = getSampleStyleSheet()
        
        # Color Palette - Valle Prime
        BLUE_DARK = colors.HexColor('#00528F')
        BLUE_LIGHT = colors.HexColor('#0089D6')
        GREEN = colors.HexColor('#8CC63E')
        RED = colors.HexColor('#DC2626')
        GRAY_DARK = colors.HexColor('#1F2A33')
        GRAY_LIGHT = colors.HexColor('#F8FAFC')
        GRAY_MEDIUM = colors.HexColor('#6B7280')
        WHITE = colors.white
        
        # Helper for currency format
        def fmt_brl(valor):
            return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        # ============== HEADER ==============
        header_data = [[
            Paragraph("<b>VALLE PRIME</b>", ParagraphStyle('H', fontSize=18, textColor=WHITE)),
            Paragraph(f"<b>RELATÓRIO DE RECEBIMENTOS</b><br/><font size=9>{nome_obra}</font>", 
                     ParagraphStyle('H', fontSize=12, textColor=WHITE, alignment=TA_RIGHT))
        ]]
        header_table = Table(header_data, colWidths=[60*mm, 126*mm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BLUE_DARK),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(header_table)
        
        # Period info
        period_style = ParagraphStyle('Period', fontSize=10, textColor=GRAY_DARK, alignment=TA_CENTER, spaceBefore=8, spaceAfter=8)
        elements.append(Paragraph(f"Período: {data_inicio_fmt} a {data_fim_fmt} | Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", period_style))
        
        elements.append(HRFlowable(width="100%", thickness=1, color=GRAY_LIGHT, spaceBefore=3, spaceAfter=10))
        
        # ============== SECTION 1: RECEBIMENTOS DIARIOS ==============
        section_style = ParagraphStyle('Section', fontSize=12, textColor=BLUE_DARK, fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=6)
        elements.append(Paragraph("RECEBIMENTOS DIARIOS", section_style))
        
        if recebimentos:
            table_data = [['DATA', 'QTD PARCELAS', 'TOTAL RECEBIDO']]
            total_geral = 0
            for i, r in enumerate(recebimentos):
                valor = float(r.get('totalRecebido', 0) or 0)
                total_geral += valor
                table_data.append([
                    r.get('data', '-'),
                    str(r.get('qtdParcelas', 0)),
                    fmt_brl(valor)
                ])
            table_data.append(['TOTAL', str(len(recebimentos)) + ' dias', fmt_brl(total_geral)])
            
            table = Table(table_data, colWidths=[50*mm, 50*mm, 86*mm])
            
            # Build style with zebra striping
            style_commands = [
                ('BACKGROUND', (0, 0), (-1, 0), BLUE_DARK),
                ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, -1), (-1, -1), GRAY_DARK),
                ('TEXTCOLOR', (0, -1), (-1, -1), WHITE),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('BOX', (0, 0), (-1, -1), 1, BLUE_DARK),
            ]
            # Zebra striping
            for i in range(1, len(table_data) - 1):
                if i % 2 == 0:
                    style_commands.append(('BACKGROUND', (0, i), (-1, i), GRAY_LIGHT))
            
            table.setStyle(TableStyle(style_commands))
            elements.append(table)
        else:
            elements.append(Paragraph("Nenhum recebimento no periodo.", styles['Normal']))
        
        elements.append(Spacer(1, 12*mm))
        
        # ============== SECTION 2: SINAIS TOTAIS ==============
        elements.append(Paragraph("SINAIS DE CORRETAGEM - RESUMO", section_style))
        
        qtd_sinais = int(sinais_totais.get('qtdSinais', 0) or 0)
        valor_total_sinais = float(sinais_totais.get('valorTotal', 0) or 0)
        vencidos_sinais = int(sinais_totais.get('vencidos', 0) or 0)
        valor_vencido_sinais = float(sinais_totais.get('valorVencido', 0) or 0)
        
        # Summary cards as table
        cards_data = [[
            Paragraph(f"<b>{qtd_sinais}</b><br/><font size=8 color='#6B7280'>Total Sinais</font>", 
                     ParagraphStyle('Card', fontSize=16, alignment=TA_CENTER, textColor=BLUE_DARK)),
            Paragraph(f"<b>{fmt_brl(valor_total_sinais)}</b><br/><font size=8 color='#6B7280'>Valor Total</font>", 
                     ParagraphStyle('Card', fontSize=14, alignment=TA_CENTER, textColor=BLUE_DARK)),
            Paragraph(f"<b>{vencidos_sinais}</b><br/><font size=8 color='#6B7280'>Vencidos</font>", 
                     ParagraphStyle('Card', fontSize=16, alignment=TA_CENTER, textColor=RED)),
            Paragraph(f"<b>{fmt_brl(valor_vencido_sinais)}</b><br/><font size=8 color='#6B7280'>Valor Vencido</font>", 
                     ParagraphStyle('Card', fontSize=14, alignment=TA_CENTER, textColor=RED)),
        ]]
        cards_table = Table(cards_data, colWidths=[46*mm, 46*mm, 46*mm, 46*mm])
        cards_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), GRAY_LIGHT),
            ('BOX', (0, 0), (0, 0), 1, BLUE_LIGHT),
            ('BOX', (1, 0), (1, 0), 1, BLUE_LIGHT),
            ('BOX', (2, 0), (2, 0), 1, RED),
            ('BOX', (3, 0), (3, 0), 1, RED),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(cards_table)
        
        elements.append(Spacer(1, 12*mm))
        
        # ============== SECTION 3: SINAIS POR CORRETOR ==============
        elements.append(Paragraph("SINAIS POR CORRETOR - DETALHADO", section_style))
        
        if sinais_corretor:
            table_data = [['CORRETOR', 'QTD', 'TOTAL GERADO', 'EM ABERTO', 'RECEBIDO', 'VENC.']]
            
            t_qtd = t_gerado = t_aberto = t_recebido = t_venc = 0
            
            for c in sinais_corretor:
                nome = (c.get('corretor') or '-')[:28]
                qtd = int(c.get('qtdSinais', 0) or 0)
                aberto = float(c.get('valorTotal', 0) or 0)
                recebido = float(c.get('valorRecebido', 0) or 0)
                gerado = aberto + recebido
                venc = int(c.get('vencidos', 0) or 0)
                
                t_qtd += qtd
                t_gerado += gerado
                t_aberto += aberto
                t_recebido += recebido
                t_venc += venc
                
                table_data.append([nome, str(qtd), fmt_brl(gerado), fmt_brl(aberto), fmt_brl(recebido), str(venc)])
            
            table_data.append(['TOTAL GERAL', str(t_qtd), fmt_brl(t_gerado), fmt_brl(t_aberto), fmt_brl(t_recebido), str(t_venc)])
            
            table = Table(table_data, colWidths=[55*mm, 12*mm, 35*mm, 32*mm, 32*mm, 12*mm])
            
            style_commands = [
                ('BACKGROUND', (0, 0), (-1, 0), GREEN),
                ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, -1), (-1, -1), GRAY_DARK),
                ('TEXTCOLOR', (0, -1), (-1, -1), WHITE),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#D1D5DB')),
                ('BOX', (0, 0), (-1, -1), 1, GREEN),
            ]
            # Zebra striping
            for i in range(1, len(table_data) - 1):
                if i % 2 == 0:
                    style_commands.append(('BACKGROUND', (0, i), (-1, i), GRAY_LIGHT))
            
            table.setStyle(TableStyle(style_commands))
            elements.append(table)
        else:
            elements.append(Paragraph("Nenhum registro.", styles['Normal']))
        
        # ============== FOOTER ==============
        elements.append(Spacer(1, 15*mm))
        elements.append(HRFlowable(width="100%", thickness=1, color=GRAY_LIGHT, spaceBefore=5, spaceAfter=5))
        
        # Importar callback de rodapé
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from pdf_styles import make_footer_callback
        data_geracao_footer = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # Build PDF com rodapé paginado
        doc.build(elements, onFirstPage=make_footer_callback(data_geracao_footer), onLaterPages=make_footer_callback(data_geracao_footer))
        buffer.seek(0)
        
        filename = f"relatorio_recebimentos_{data_inicio}_{data_fim}.pdf"
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}\n\n{error_details}")


@router.get("/relatorio-corretor-pdf")
async def get_relatorio_corretor_pdf(
    empresa: int = Query(..., description="Codigo da empresa"),
    obra: str = Query(..., description="Codigo da obra"),
    corretor: str = Query("", description="Nome do corretor (vazio = todos)"),
    data_inicio: str = Query("", description="Data inicio (yyyy-mm-dd)"),
    data_fim: str = Query("", description="Data fim (yyyy-mm-dd)")
):
    """Gera relatorio PDF profissional por corretor para controle de vendas e cobrança"""
    
    corretor_filter = f"AND UPPER(PessoasVendedor.nome_pes) = UPPER('{corretor}')" if corretor else ""
    
    # Filtro de data - usar Data_Ven (data da venda) com formato YYYYMMDD
    date_filter = ""
    date_filter_v = ""  # Para usar com alias 'v.'
    if data_inicio and data_fim:
        data_inicio_sql = data_inicio.replace('-', '')
        data_fim_sql = data_fim.replace('-', '')
        date_filter = f"AND (Vendas.Data_Ven BETWEEN CONVERT(datetime, '{data_inicio_sql}', 112) AND CONVERT(datetime, '{data_fim_sql}', 112))"
        date_filter_v = f"AND (v.Data_Ven BETWEEN CONVERT(datetime, '{data_inicio_sql}', 112) AND CONVERT(datetime, '{data_fim_sql}', 112))"
    elif data_inicio:
        data_inicio_sql = data_inicio.replace('-', '')
        date_filter = f"AND Vendas.Data_Ven >= CONVERT(datetime, '{data_inicio_sql}', 112)"
        date_filter_v = f"AND v.Data_Ven >= CONVERT(datetime, '{data_inicio_sql}', 112)"
    elif data_fim:
        data_fim_sql = data_fim.replace('-', '')
        date_filter = f"AND Vendas.Data_Ven <= CONVERT(datetime, '{data_fim_sql}', 112)"
        date_filter_v = f"AND v.Data_Ven <= CONVERT(datetime, '{data_fim_sql}', 112)"
    
    # Parâmetro para fn_ListEmpObr
    emp_obra_param = f"{empresa}|{obra}"
    
    # Texto do período para mostrar no PDF
    periodo_texto = ""
    if data_inicio and data_fim:
        di = f"{data_inicio[8:10]}/{data_inicio[5:7]}/{data_inicio[0:4]}"
        df = f"{data_fim[8:10]}/{data_fim[5:7]}/{data_fim[0:4]}"
        periodo_texto = f"Período: {di} a {df}"
    elif data_inicio:
        di = f"{data_inicio[8:10]}/{data_inicio[5:7]}/{data_inicio[0:4]}"
        periodo_texto = f"A partir de: {di}"
    elif data_fim:
        df = f"{data_fim[8:10]}/{data_fim[5:7]}/{data_fim[0:4]}"
        periodo_texto = f"Até: {df}"
    
    # Query 1: Resumo Geral do Corretor - usando UNION igual ao stats com subqueries para sinais
    resumo_query = f"""
    SELECT
        UPPER(ISNULL(Pessoas.nome_pes, 'NAO INFORMADO')) AS corretor,
        COUNT(*) AS qtdVendas,
        ISNULL(SUM(VendaLiquida), 0) AS valorTotalVendas,
        -- Subquery calcular totais de sinais apenas para este corretor
        0 AS sinaisGerados,
        0 AS sinaisPagos,
        0.0 AS valorSinaisPagos,
        0 AS sinaisAbertos,
        0.0 AS valorSinaisAbertos,
        0 AS sinaisVencidos,
        0.0 AS valorSinaisVencidos
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
            {date_filter.replace('Vendas.Data_Ven', 'VendasRecebidas.Data_VRec')}
    ) AS Vendas
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Vendedor_Ven = Pessoas.cod_pes
    INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON Vendas.Empresa_Ven = Empresa AND Vendas.Obra_Ven = Obra
    WHERE Status_Ven = 0
    {corretor_filter.replace('PessoasVendedor', 'Pessoas')}
    GROUP BY Pessoas.nome_pes
    """
    
    # Query para buscar dados de sinais separadamente (mesmo padrão do stats)
    corretor_filter_sinais = f"AND UPPER(Pessoas.nome_pes) = UPPER('{corretor}')" if corretor else ""
    
    sinais_resumo_query = f"""
    SELECT
        -- Sinais Pagos
        (SELECT COUNT(*) FROM Recebidas r WITH(NOLOCK)
         INNER JOIN (
            SELECT Num_Ven, Vendedor_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK) WHERE Status_Ven = 0 {date_filter}
            UNION
            SELECT Num_VRec, Vendedor_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK) WHERE Status_VRec = 0 {date_filter.replace('Vendas.Data_Ven', 'VendasRecebidas.Data_VRec')}
         ) v ON r.NumVend_Rec = v.Num_Ven AND r.Empresa_Rec = v.Empresa_Ven AND r.Obra_Rec = v.Obra_Ven
         INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
         INNER JOIN Pessoas WITH(NOLOCK) ON v.Vendedor_Ven = Pessoas.cod_pes
         WHERE r.Tipo_Rec = 'S'
         {corretor_filter_sinais}) AS sinaisPagos,
        (SELECT ISNULL(SUM(r.Valor_Rec + r.ValorConf_Rec + r.VlCorrecao_Rec + r.VlCorrecaoConf_Rec + 
               r.VlMulta_Rec + r.VlMultaConf_Rec + r.VlJuros_Rec + r.VlJurosConf_Rec), 0) 
         FROM Recebidas r WITH(NOLOCK)
         INNER JOIN (
            SELECT Num_Ven, Vendedor_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK) WHERE Status_Ven = 0 {date_filter}
            UNION
            SELECT Num_VRec, Vendedor_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK) WHERE Status_VRec = 0 {date_filter.replace('Vendas.Data_Ven', 'VendasRecebidas.Data_VRec')}
         ) v ON r.NumVend_Rec = v.Num_Ven AND r.Empresa_Rec = v.Empresa_Ven AND r.Obra_Rec = v.Obra_Ven
         INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
         INNER JOIN Pessoas WITH(NOLOCK) ON v.Vendedor_Ven = Pessoas.cod_pes
         WHERE r.Tipo_Rec = 'S'
         {corretor_filter_sinais}) AS valorSinaisPagos,
        -- Sinais em Aberto
        (SELECT COUNT(*) FROM ContasReceber cr WITH(NOLOCK)
         INNER JOIN (
            SELECT Num_Ven, Vendedor_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK) WHERE Status_Ven = 0 {date_filter}
            UNION
            SELECT Num_VRec, Vendedor_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK) WHERE Status_VRec = 0 {date_filter.replace('Vendas.Data_Ven', 'VendasRecebidas.Data_VRec')}
         ) v ON cr.NumVend_prc = v.Num_Ven AND cr.Empresa_prc = v.Empresa_Ven AND cr.Obra_Prc = v.Obra_Ven
         INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
         INNER JOIN Pessoas WITH(NOLOCK) ON v.Vendedor_Ven = Pessoas.cod_pes
         WHERE cr.Tipo_Prc = 'S' AND cr.Status_Prc = 0
         {corretor_filter_sinais}) AS sinaisAbertos,
        (SELECT ISNULL(SUM(cr.Valor_Prc), 0) FROM ContasReceber cr WITH(NOLOCK)
         INNER JOIN (
            SELECT Num_Ven, Vendedor_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK) WHERE Status_Ven = 0 {date_filter}
            UNION
            SELECT Num_VRec, Vendedor_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK) WHERE Status_VRec = 0 {date_filter.replace('Vendas.Data_Ven', 'VendasRecebidas.Data_VRec')}
         ) v ON cr.NumVend_prc = v.Num_Ven AND cr.Empresa_prc = v.Empresa_Ven AND cr.Obra_Prc = v.Obra_Ven
         INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
         INNER JOIN Pessoas WITH(NOLOCK) ON v.Vendedor_Ven = Pessoas.cod_pes
         WHERE cr.Tipo_Prc = 'S' AND cr.Status_Prc = 0
         {corretor_filter_sinais}) AS valorSinaisAbertos,
        -- Sinais Vencidos
        (SELECT COUNT(*) FROM ContasReceber cr WITH(NOLOCK)
         INNER JOIN (
            SELECT Num_Ven, Vendedor_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK) WHERE Status_Ven = 0 {date_filter}
            UNION
            SELECT Num_VRec, Vendedor_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK) WHERE Status_VRec = 0 {date_filter.replace('Vendas.Data_Ven', 'VendasRecebidas.Data_VRec')}
         ) v ON cr.NumVend_prc = v.Num_Ven AND cr.Empresa_prc = v.Empresa_Ven AND cr.Obra_Prc = v.Obra_Ven
         INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
         INNER JOIN Pessoas WITH(NOLOCK) ON v.Vendedor_Ven = Pessoas.cod_pes
         WHERE cr.Tipo_Prc = 'S' AND cr.Status_Prc = 0 AND cr.Data_Prc < CAST(GETDATE() AS DATE)
         {corretor_filter_sinais}) AS sinaisVencidos,
        (SELECT ISNULL(SUM(cr.Valor_Prc), 0) FROM ContasReceber cr WITH(NOLOCK)
         INNER JOIN (
            SELECT Num_Ven, Vendedor_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK) WHERE Status_Ven = 0 {date_filter}
            UNION
            SELECT Num_VRec, Vendedor_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK) WHERE Status_VRec = 0 {date_filter.replace('Vendas.Data_Ven', 'VendasRecebidas.Data_VRec')}
         ) v ON cr.NumVend_prc = v.Num_Ven AND cr.Empresa_prc = v.Empresa_Ven AND cr.Obra_Prc = v.Obra_Ven
         INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
         INNER JOIN Pessoas WITH(NOLOCK) ON v.Vendedor_Ven = Pessoas.cod_pes
         WHERE cr.Tipo_Prc = 'S' AND cr.Status_Prc = 0 AND cr.Data_Prc < CAST(GETDATE() AS DATE)
         {corretor_filter_sinais}) AS valorSinaisVencidos
    """
    
    # Query 2: Clientes que Pagaram (sinais pagos)
    pagos_query = f"""
    SELECT
        UPPER(Pessoas.Nome_Pes) as cliente,
        ISNULL(UnidVenda.C1_unid, '-') as quadra,
        ISNULL(UnidVenda.C2_unid, '-') as lote,
        Vendas.ValorTot_Ven as valorVenda,
        Recebidas.Valor_Rec + Recebidas.ValorConf_Rec as valorSinalPago,
        CONCAT(Recebidas.NumParc_Rec, '/', Recebidas.TotParc_Rec) as parcela,
        FORMAT(Recebidas.DataVenci_Rec, 'dd/MM/yyyy') as dataVencimento,
        FORMAT(Recebidas.Data_Rec, 'dd/MM/yyyy') as dataPagamento,
        UPPER(ISNULL(PessoasVendedor.nome_pes, 'NAO INFORMADO')) AS corretor
    FROM Recebidas WITH(NOLOCK)
    INNER JOIN Vendas WITH(NOLOCK) 
        ON Recebidas.Empresa_Rec = Vendas.Empresa_Ven 
        AND Recebidas.Obra_Rec = Vendas.Obra_Ven 
        AND Recebidas.NumVend_Rec = Vendas.Num_Ven
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.Cod_Pes
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_itv AND Vendas.Obra_Ven = ItensVenda.Obra_Itv AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer UnidVenda WITH(NOLOCK) ON ItensVenda.Empresa_itv = UnidVenda.Empresa_unid AND ItensVenda.Produto_Itv = UnidVenda.Prod_unid AND ItensVenda.CodPerson_Itv = UnidVenda.NumPer_unid
    WHERE Recebidas.Empresa_Rec = {empresa} AND Recebidas.Obra_Rec = '{obra}' AND Recebidas.Tipo_Rec = 'S'
    {corretor_filter}
    ORDER BY dataPagamento DESC
    """
    
    # Query 3: Clientes em Atraso (sinais vencidos) - com telefone, status boleto e prorrogação
    atraso_query = f"""
    SELECT
        UPPER(Pessoas.Nome_Pes) as cliente,
        ISNULL(PesTel.FoneCel, '-') as telefone,
        ISNULL(UnidVenda.C1_unid, '-') as quadra,
        ISNULL(UnidVenda.C2_unid, '-') as lote,
        ContasReceber.Valor_Prc as valorSinal,
        FORMAT(ContasReceber.Data_Prc, 'dd/MM/yyyy') as vencimento,
        CASE 
            WHEN ContasReceber.DataPror_Prc IS NOT NULL AND ContasReceber.DataPror_Prc > ContasReceber.Data_Prc 
            THEN FORMAT(ContasReceber.DataPror_Prc, 'dd/MM/yyyy')
            ELSE NULL 
        END as prorrogacao,
        DATEDIFF(DAY, ISNULL(ContasReceber.DataPror_Prc, ContasReceber.Data_Prc), GETDATE()) as diasAtraso,
        Vendas.Num_Ven as venda,
        -- Verificar se tem boleto gerado
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM RecebAutoConfirmado rac WITH(NOLOCK)
                INNER JOIN BoletoConfirmado bc WITH(NOLOCK) 
                    ON rac.SeuNum_Rea = bc.SeuNum_Bol AND rac.Banco_Rea = bc.Banco_Bol
                WHERE rac.Empresa_rea = ContasReceber.Empresa_prc 
                    AND rac.ObraPrc_Rea = ContasReceber.Obra_Prc
                    AND rac.NumVendPrc_Rea = ContasReceber.NumVend_prc
                    AND rac.NumParcPrc_Rea = ContasReceber.NumParc_Prc
                    AND rac.TipoPrc_Rea = ContasReceber.Tipo_Prc
            ) THEN 'BOLETO'
            ELSE 'SEM BOLETO'
        END as statusBoleto,
        -- Verificar total de sinais e sinais pagos para determinar se está quitado
        (SELECT COUNT(*) FROM ContasReceber cr2 WITH(NOLOCK) 
         WHERE cr2.Empresa_prc = Vendas.Empresa_Ven AND cr2.Obra_Prc = Vendas.Obra_Ven 
         AND cr2.NumVend_prc = Vendas.Num_Ven AND cr2.Tipo_Prc = 'S') as totalSinais,
        (SELECT COUNT(*) FROM Recebidas r2 WITH(NOLOCK) 
         WHERE r2.Empresa_Rec = Vendas.Empresa_Ven AND r2.Obra_Rec = Vendas.Obra_Ven 
         AND r2.NumVend_Rec = Vendas.Num_Ven AND r2.Tipo_Rec = 'S') as sinaisPagos,
        UPPER(ISNULL(PessoasVendedor.nome_pes, 'NAO INFORMADO')) AS corretor
    FROM ContasReceber WITH(NOLOCK)
    INNER JOIN Vendas WITH(NOLOCK) 
        ON ContasReceber.Empresa_prc = Vendas.Empresa_Ven 
        AND ContasReceber.Obra_Prc = Vendas.Obra_Ven 
        AND ContasReceber.NumVend_prc = Vendas.Num_Ven
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.Cod_Pes
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_itv AND Vendas.Obra_Ven = ItensVenda.Obra_Itv AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer UnidVenda WITH(NOLOCK) ON ItensVenda.Empresa_itv = UnidVenda.Empresa_unid AND ItensVenda.Produto_Itv = UnidVenda.Prod_unid AND ItensVenda.CodPerson_Itv = UnidVenda.NumPer_unid
    -- Telefone do cliente via PesTel
    LEFT OUTER JOIN (
        SELECT Pes_tel,
            COALESCE(MAX(FoneCel), '') AS FoneCel
        FROM (
            SELECT Pes_tel,
                CASE WHEN Tipo_tel = 2 THEN DDD_tel + ' ' + Fone_tel END AS FoneCel
            FROM PesTel WITH(NOLOCK) WHERE Tipo_tel = 2
        ) AS Tel
        GROUP BY Pes_tel
    ) AS PesTel ON Pessoas.Cod_pes = PesTel.Pes_tel
    WHERE ContasReceber.Empresa_prc = {empresa} AND ContasReceber.Obra_Prc = '{obra}' 
    AND ContasReceber.Tipo_Prc = 'S' AND ContasReceber.Status_Prc = 0
    AND ISNULL(ContasReceber.DataPror_Prc, ContasReceber.Data_Prc) < CAST(GETDATE() AS DATE)
    {corretor_filter}
    ORDER BY diasAtraso DESC
    """
    
    # Query 4: Sinais A VENCER (ainda não vencidos)
    a_vencer_query = f"""
    SELECT
        UPPER(Pessoas.Nome_Pes) as cliente,
        ISNULL(PesTel.FoneCel, '-') as telefone,
        ISNULL(UnidVenda.C1_unid, '-') as quadra,
        ISNULL(UnidVenda.C2_unid, '-') as lote,
        ContasReceber.Valor_Prc as valorSinal,
        FORMAT(ContasReceber.Data_Prc, 'dd/MM/yyyy') as vencimento,
        DATEDIFF(DAY, GETDATE(), ISNULL(ContasReceber.DataPror_Prc, ContasReceber.Data_Prc)) as diasParaVencer,
        Vendas.Num_Ven as venda,
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM RecebAutoConfirmado rac WITH(NOLOCK)
                INNER JOIN BoletoConfirmado bc WITH(NOLOCK) 
                    ON rac.SeuNum_Rea = bc.SeuNum_Bol AND rac.Banco_Rea = bc.Banco_Bol
                WHERE rac.Empresa_rea = ContasReceber.Empresa_prc 
                    AND rac.ObraPrc_Rea = ContasReceber.Obra_Prc
                    AND rac.NumVendPrc_Rea = ContasReceber.NumVend_prc
                    AND rac.NumParcPrc_Rea = ContasReceber.NumParc_Prc
                    AND rac.TipoPrc_Rea = ContasReceber.Tipo_Prc
            ) THEN 'BOLETO'
            ELSE 'SEM BOLETO'
        END as statusBoleto,
        UPPER(ISNULL(PessoasVendedor.nome_pes, 'NAO INFORMADO')) AS corretor
    FROM ContasReceber WITH(NOLOCK)
    INNER JOIN Vendas WITH(NOLOCK) 
        ON ContasReceber.Empresa_prc = Vendas.Empresa_Ven 
        AND ContasReceber.Obra_Prc = Vendas.Obra_Ven 
        AND ContasReceber.NumVend_prc = Vendas.Num_Ven
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.Cod_Pes
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_itv AND Vendas.Obra_Ven = ItensVenda.Obra_Itv AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer UnidVenda WITH(NOLOCK) ON ItensVenda.Empresa_itv = UnidVenda.Empresa_unid AND ItensVenda.Produto_Itv = UnidVenda.Prod_unid AND ItensVenda.CodPerson_Itv = UnidVenda.NumPer_unid
    LEFT OUTER JOIN (
        SELECT Pes_tel, COALESCE(MAX(FoneCel), '') AS FoneCel
        FROM (SELECT Pes_tel, CASE WHEN Tipo_tel = 2 THEN DDD_tel + ' ' + Fone_tel END AS FoneCel FROM PesTel WITH(NOLOCK) WHERE Tipo_tel = 2) AS Tel
        GROUP BY Pes_tel
    ) AS PesTel ON Pessoas.Cod_pes = PesTel.Pes_tel
    WHERE ContasReceber.Empresa_prc = {empresa} AND ContasReceber.Obra_Prc = '{obra}' 
    AND ContasReceber.Tipo_Prc = 'S' AND ContasReceber.Status_Prc = 0
    AND ISNULL(ContasReceber.DataPror_Prc, ContasReceber.Data_Prc) >= CAST(GETDATE() AS DATE)
    {corretor_filter}
    ORDER BY diasParaVencer ASC
    """
    
    try:
        resumo = execute_query(resumo_query)
        pagos = execute_query(pagos_query)
        atrasos = execute_query(atraso_query)
        a_vencer = execute_query(a_vencer_query)
        sinais_dados = execute_query(sinais_resumo_query)
        
        # Query para sinais pagos usando Depósitos Conciliados (mesma metodologia da tela Recebimentos)
        contas = CONTAS_POR_EMPRESA.get(empresa, CONTAS_POR_EMPRESA[28])
        contas_filter = f"({','.join(contas)})"
        corretor_filter_pagos = f"AND UPPER(COALESCE(PessoasVendedor.nome_pes, PessoasVendedorVRec.nome_pes)) = UPPER('{corretor}')" if corretor else ""
        
        sinais_pagos_conciliados_query = f"""
        SELECT
            COUNT(*) AS sinaisPagos,
            ISNULL(SUM(RecebePgtoDiv.PercentValor_Rpd * (CAST((ItensRecebidas.Qtde_Itr * ItensRecebidas.PrecoProc_Itr - ItensRecebidas.ValComissaoDir_Itr) AS NUMERIC(18, 6)) / NULLIF(VendasRecebidas.ValorTot_VRec, 0))), 0) AS valorSinaisPagos
        FROM Extrato WITH(NOLOCK)
        INNER JOIN Depositos WITH(NOLOCK)
            ON Extrato.Empresa_Doc = Depositos.Empresa_Dep
            AND Extrato.Banco_Doc = Depositos.Banco_Dep
            AND Extrato.Conta_Doc = Depositos.Conta_Dep
            AND Extrato.Numero_Doc = Depositos.Numero_Dep
        INNER JOIN RecebePgto WITH(NOLOCK)
            ON Depositos.Empresa_Dep = RecebePgto.Empresa_Rpg
            AND Depositos.Numero_Dep = RecebePgto.NumDep_Rpg
            AND Depositos.Banco_Dep = RecebePgto.BancoDep_Rpg
            AND Depositos.Conta_Dep = RecebePgto.ContaDep_Rpg
            AND RecebePgto.Status_Rpg <> 2
        INNER JOIN RecebePgtoDiv WITH(NOLOCK)
            ON RecebePgto.Empresa_Rpg = RecebePgtoDiv.Empresa_Rpd
            AND RecebePgto.NumReceb_Rpg = RecebePgtoDiv.NumReceb_Rpd
            AND RecebePgto.Tipo_Rpg = RecebePgtoDiv.TipoRpg_Rpd
            AND RecebePgto.NumCont_Rpg = RecebePgtoDiv.NumCont_Rpd
        INNER JOIN Recebidas WITH(NOLOCK)
            ON RecebePgtoDiv.Empresa_Rpd = Recebidas.Empresa_Rec
            AND RecebePgtoDiv.Obra_Rpd = Recebidas.Obra_Rec
            AND RecebePgtoDiv.NumVend_Rpd = Recebidas.NumVend_Rec
            AND RecebePgtoDiv.NumParc_Rpd = Recebidas.NumParc_Rec
            AND RecebePgtoDiv.ParcType_Rpd = Recebidas.ParcType_Rec
            AND RecebePgtoDiv.Tipo_Rpd = Recebidas.Tipo_Rec
            AND RecebePgtoDiv.NumParcGer_Rpd = Recebidas.NumParcGer_Rec
        INNER JOIN VendasRecebidas WITH(NOLOCK)
            ON Recebidas.Empresa_Rec = VendasRecebidas.Empresa_VRec
            AND Recebidas.Obra_Rec = VendasRecebidas.Obra_VRec
            AND Recebidas.NumVend_Rec = VendasRecebidas.Num_VRec
        INNER JOIN ItensRecebidas WITH(NOLOCK)
            ON VendasRecebidas.Empresa_VRec = ItensRecebidas.Empresa_Itr
            AND VendasRecebidas.Obra_VRec = ItensRecebidas.Obra_Itr
            AND VendasRecebidas.Num_VRec = ItensRecebidas.NumVend_Itr
        LEFT JOIN Vendas WITH(NOLOCK)
            ON Recebidas.Empresa_Rec = Vendas.Empresa_Ven
            AND Recebidas.Obra_Rec = Vendas.Obra_Ven
            AND Recebidas.NumVend_Rec = Vendas.Num_Ven
        LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK)
            ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
        LEFT JOIN Pessoas AS PessoasVendedorVRec WITH(NOLOCK)
            ON VendasRecebidas.Vendedor_VRec = PessoasVendedorVRec.cod_pes
        WHERE Extrato.Tipo_Doc = 1
            AND Extrato.Empresa_doc = {empresa}
            AND Extrato.Conta_doc IN {contas_filter}
            AND Recebidas.Tipo_Rec = 'S'
            AND VendasRecebidas.Obra_VRec = '{obra}'
            {corretor_filter_pagos}
        """
        sinais_pagos_result = execute_query(sinais_pagos_conciliados_query)
        
        # Sobrescrever valores de sinais pagos com dados conciliados
        if sinais_dados and sinais_pagos_result:
            sinais_dados[0]['sinaisPagos'] = sinais_pagos_result[0].get('sinaisPagos', 0)
            sinais_dados[0]['valorSinaisPagos'] = sinais_pagos_result[0].get('valorSinaisPagos', 0)
        
        # Buscar nome do empreendimento
        obra_name_query = f"SELECT Descr_Obr FROM Obras WITH(NOLOCK) WHERE Empresa_Obr = {empresa} AND Cod_Obr = '{obra}'"
        obra_result = execute_query(obra_name_query)
        nome_empreendimento = obra_result[0].get('Descr_Obr', obra) if obra_result else obra
        
        if not resumo or (len(resumo) == 1 and resumo[0].get('qtdVendas', 0) == 0):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = [Paragraph("Nenhuma venda encontrada para os filtros selecionados", styles['Heading1'])]
            doc.build(story)
            buffer.seek(0)
            return StreamingResponse(buffer, media_type='application/pdf',
                headers={'Content-Disposition': 'inline; filename="relatorio_corretor_vazio.pdf"'})
        
        # PDF Generation
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=12*mm, bottomMargin=12*mm, leftMargin=10*mm, rightMargin=10*mm)
        elements = []
        styles = getSampleStyleSheet()
        
        # Colors
        BLUE_DARK = colors.HexColor('#1E3A8A')
        BLUE_LIGHT = colors.HexColor('#3B82F6')
        GREEN = colors.HexColor('#059669')
        RED = colors.HexColor('#DC2626')
        ORANGE = colors.HexColor('#F59E0B')
        GRAY_DARK = colors.HexColor('#374151')
        GRAY_LIGHT = colors.HexColor('#F3F4F6')
        WHITE = colors.white
        
        def fmt_brl(valor):
            try:
                return f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            except:
                return "R$ 0,00"
        
        # ============ HEADER ============
        r = resumo[0]
        nome_corretor = r.get('corretor', 'TODOS')
        
        header_data = [[
            Paragraph(f"<b>VALLEPRIME</b><br/><font size=8>{nome_empreendimento}</font>", ParagraphStyle('H', fontSize=14, textColor=WHITE)),
            Paragraph(f"<b>RELATÓRIO DO CORRETOR</b><br/><font size=10>{nome_corretor}</font>", 
                     ParagraphStyle('H', fontSize=12, textColor=WHITE, alignment=TA_CENTER)),
            Paragraph(f"<font size=9>Empresa: {empresa}<br/>Obra: {obra}</font>", 
                     ParagraphStyle('H', fontSize=9, textColor=WHITE, alignment=TA_RIGHT))
        ]]
        header_table = Table(header_data, colWidths=[50*mm, 90*mm, 50*mm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BLUE_DARK),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 3*mm))
        
        # Data geração e período
        data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
        info_texto = f"Gerado em: {data_geracao}"
        if periodo_texto:
            info_texto = f"{periodo_texto} | {info_texto}"
        elements.append(Paragraph(f"<font size=8 color='#6B7280'>{info_texto}</font>", 
                                  ParagraphStyle('dt', alignment=TA_RIGHT)))
        elements.append(Spacer(1, 4*mm))
        
        # ============ RESUMO GERAL ============
        elements.append(Paragraph("<b>RESUMO GERAL</b>", ParagraphStyle('title', fontSize=11, textColor=BLUE_DARK, spaceBefore=5)))
        elements.append(HRFlowable(width="100%", thickness=1, color=BLUE_LIGHT, spaceAfter=5))
        
        # Dados de vendas vem do resumo principal
        qtd_vendas = r.get('qtdVendas', 0) or 0
        valor_vendas = float(r.get('valorTotalVendas', 0) or 0)
        
        # Dados de sinais vem da query separada sinais_dados
        s = sinais_dados[0] if sinais_dados else {}
        sinais_pagos = int(s.get('sinaisPagos', 0) or 0)
        valor_pagos = float(s.get('valorSinaisPagos', 0) or 0)
        sinais_abertos = int(s.get('sinaisAbertos', 0) or 0)
        valor_abertos = float(s.get('valorSinaisAbertos', 0) or 0)
        sinais_vencidos = int(s.get('sinaisVencidos', 0) or 0)
        valor_vencidos = float(s.get('valorSinaisVencidos', 0) or 0)
        sinais_gerados = sinais_pagos + sinais_abertos
        
        # Cards de resumo
        card_style = ParagraphStyle('card', fontSize=8, alignment=TA_CENTER, textColor=GRAY_DARK)
        card_value = ParagraphStyle('cardval', fontSize=11, alignment=TA_CENTER, fontName='Helvetica-Bold')
        
        resumo_data = [[
            Paragraph(f"<b>VENDAS</b><br/><font size=14 color='#2563EB'>{qtd_vendas}</font><br/><font size=7>{fmt_brl(valor_vendas)}</font>", card_style),
            Paragraph(f"<b>SINAIS GERADOS</b><br/><font size=14 color='#7C3AED'>{sinais_gerados}</font>", card_style),
            Paragraph(f"<b>SINAIS PAGOS</b><br/><font size=14 color='#059669'>{sinais_pagos}</font><br/><font size=7 color='#059669'>{fmt_brl(valor_pagos)}</font>", card_style),
            Paragraph(f"<b>EM ABERTO</b><br/><font size=14 color='#F59E0B'>{sinais_abertos}</font><br/><font size=7 color='#F59E0B'>{fmt_brl(valor_abertos)}</font>", card_style),
            Paragraph(f"<b>VENCIDOS</b><br/><font size=14 color='#DC2626'>{sinais_vencidos}</font><br/><font size=7 color='#DC2626'>{fmt_brl(valor_vencidos)}</font>", card_style),
        ]]
        resumo_table = Table(resumo_data, colWidths=[38*mm, 38*mm, 38*mm, 38*mm, 38*mm])
        resumo_table.setStyle(TableStyle([
            ('BOX', (0, 0), (0, 0), 1, BLUE_LIGHT),
            ('BOX', (1, 0), (1, 0), 1, colors.HexColor('#7C3AED')),
            ('BOX', (2, 0), (2, 0), 1, GREEN),
            ('BOX', (3, 0), (3, 0), 1, ORANGE),
            ('BOX', (4, 0), (4, 0), 1, RED),
            ('BACKGROUND', (0, 0), (-1, -1), WHITE),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(resumo_table)
        elements.append(Spacer(1, 6*mm))
        
        # ============ CLIENTES QUE PAGARAM ============
        elements.append(Paragraph("<b>✅ CLIENTES QUE PAGARAM</b>", ParagraphStyle('title', fontSize=10, textColor=GREEN, spaceBefore=5)))
        elements.append(HRFlowable(width="100%", thickness=1, color=GREEN, spaceAfter=3))
        
        if pagos:
            pagos_header = [['Cliente', 'Quadra', 'Lote', 'Parcela', 'Valor Venda', 'Sinal Pago', 'Vencim.', 'Data Pgto']]
            pagos_rows = []
            for p in pagos:  # Mostrar TODOS os registros
                pagos_rows.append([
                    (p.get('cliente', '-') or '-')[:42],
                    p.get('quadra', '-'),
                    p.get('lote', '-'),
                    p.get('parcela', '-'),
                    fmt_brl(p.get('valorVenda', 0)),
                    fmt_brl(p.get('valorSinalPago', 0)),
                    p.get('dataVencimento', '-'),
                    p.get('dataPagamento', '-')
                ])
            
            pagos_table = Table(pagos_header + pagos_rows, colWidths=[62*mm, 14*mm, 14*mm, 12*mm, 24*mm, 24*mm, 18*mm, 18*mm])
            pagos_style = [
                ('BACKGROUND', (0, 0), (-1, 0), GREEN),
                ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (1, 0), (3, -1), 'CENTER'),  # Quadra, Lote, Parcela centered
                ('ALIGN', (4, 0), (5, -1), 'RIGHT'),   # Valores right
                ('ALIGN', (6, 0), (-1, -1), 'CENTER'), # Datas centered
                ('GRID', (0, 0), (-1, -1), 0.5, GRAY_LIGHT),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]
            for i in range(1, len(pagos_rows) + 1):
                if i % 2 == 0:
                    pagos_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ECFDF5')))
            pagos_table.setStyle(TableStyle(pagos_style))
            elements.append(pagos_table)
        else:
            elements.append(Paragraph("<font size=9 color='#6B7280'>Nenhum cliente pagou sinal até o momento.</font>", styles['Normal']))
        
        elements.append(Spacer(1, 6*mm))
        
        # ============ SINAIS A VENCER ============
        elements.append(Paragraph("<b>📅 SINAIS A VENCER</b>", ParagraphStyle('title', fontSize=10, textColor=ORANGE, spaceBefore=5)))
        elements.append(HRFlowable(width="100%", thickness=1, color=ORANGE, spaceAfter=3))
        
        if a_vencer:
            avencer_header = [['Cliente', 'Telefone', 'Q', 'L', 'Valor', 'Vencimento', 'Dias p/ Vencer', 'Boleto']]
            avencer_rows = []
            total_a_vencer = 0
            for v in a_vencer:
                dias = int(v.get('diasParaVencer', 0) or 0)
                status_boleto = v.get('statusBoleto', 'SEM BOLETO')
                status_display = 'BOL' if status_boleto == 'BOLETO' else 'S/B'
                telefone_raw = str(v.get('telefone', '-') or '-')
                telefone = telefone_raw[:13] if telefone_raw != '-' else '-'
                cliente_nome = str(v.get('cliente', '-') or '-')[:35]
                valor = float(v.get('valorSinal', 0) or 0)
                total_a_vencer += valor
                
                # Cor baseada em quantos dias faltam
                if dias <= 3:
                    dias_display = f"{dias}d ⚡"  # Urgente
                elif dias <= 7:
                    dias_display = f"{dias}d"  # Breve
                else:
                    dias_display = f"{dias}d"  # Normal
                
                avencer_rows.append([
                    cliente_nome,
                    telefone,
                    str(v.get('quadra', '-')),
                    str(v.get('lote', '-')),
                    fmt_brl(valor),
                    v.get('vencimento', '-'),
                    dias_display,
                    status_display
                ])
            
            # Adicionar linha de total
            avencer_rows.append(['TOTAL A VENCER', '', '', '', fmt_brl(total_a_vencer), f'{len(a_vencer)} sinais', '', ''])
            
            avencer_table = Table(avencer_header + avencer_rows, colWidths=[52*mm, 22*mm, 8*mm, 8*mm, 24*mm, 22*mm, 24*mm, 14*mm])
            avencer_style = [
                ('BACKGROUND', (0, 0), (-1, 0), ORANGE),
                ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (3, -1), 'CENTER'),
                ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
                ('ALIGN', (5, 0), (7, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, GRAY_LIGHT),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                # Linha de total
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FEF3C7')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]
            # Zebra striping exceto última linha (total)
            for i in range(1, len(avencer_rows)):
                if i % 2 == 0 and i < len(avencer_rows):
                    avencer_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFFBEB')))
            avencer_table.setStyle(TableStyle(avencer_style))
            elements.append(avencer_table)
        else:
            elements.append(Paragraph("<font size=9 color='#059669'>Nenhum sinal a vencer no momento!</font>", styles['Normal']))
        
        elements.append(Spacer(1, 6*mm))
        
        # ============ CLIENTES EM ATRASO ============
        elements.append(Paragraph("<b>⚠️ CLIENTES EM ATRASO - PARA COBRANÇA</b>", ParagraphStyle('title', fontSize=10, textColor=RED, spaceBefore=5)))
        elements.append(HRFlowable(width="100%", thickness=1, color=RED, spaceAfter=3))
        
        if atrasos:
            # Cabeçalho ajustado com novas colunas + Anotações
            atraso_header = [['Cliente', 'Telefone', 'Q', 'L', 'Valor', 'Venc.', 'Prorrog.', 'Bol', 'Dias', 'Anotacoes']]
            atraso_rows = []
            for a in atrasos:
                dias = int(a.get('diasAtraso', 0) or 0)
                prorrogacao = a.get('prorrogacao') or '-'
                
                # Determinar status do boleto
                status_boleto = a.get('statusBoleto', 'SEM BOLETO')
                
                # Apenas BOL ou S/B (sem "quitando" pois só mostra em aberto)
                if status_boleto == 'BOLETO':
                    status_display = 'BOL'
                else:
                    status_display = 'S/B'
                
                # Formatar telefone (apenas últimos 13 caracteres)
                telefone_raw = str(a.get('telefone', '-') or '-')
                telefone = telefone_raw[:13] if telefone_raw != '-' else '-'
                
                # Truncar nome do cliente (mais espaço agora)
                cliente_nome = str(a.get('cliente', '-') or '-')[:32]
                
                atraso_rows.append([
                    cliente_nome,
                    telefone,
                    str(a.get('quadra', '-')),
                    str(a.get('lote', '-')),
                    fmt_brl(a.get('valorSinal', 0)),
                    a.get('vencimento', '-'),
                    prorrogacao,
                    status_display,
                    f"{dias}d",
                    ''  # Coluna vazia para anotações manuais
                ])
            
            # Larguras ajustadas: Cliente maior, Anotações menor
            atraso_table = Table(atraso_header + atraso_rows, colWidths=[48*mm, 20*mm, 7*mm, 7*mm, 20*mm, 16*mm, 16*mm, 10*mm, 10*mm, 36*mm])
            atraso_style = [
                ('BACKGROUND', (0, 0), (-1, 0), RED),
                ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 6),
                ('FONTSIZE', (0, 1), (-1, -1), 6),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # Telefone centered
                ('ALIGN', (2, 0), (3, -1), 'CENTER'),  # Quadra, Lote centered
                ('ALIGN', (4, 0), (4, -1), 'RIGHT'),   # Valor right
                ('ALIGN', (5, 0), (8, -1), 'CENTER'),  # Datas e status centered
                ('ALIGN', (9, 0), (9, 0), 'CENTER'),   # Anotacoes header centered
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, GRAY_LIGHT),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                # Coluna de anotações com fundo amarelo claro para destaque
                ('BACKGROUND', (9, 1), (9, -1), colors.HexColor('#FFFBEB')),
            ]
            for i in range(1, len(atraso_rows) + 1):
                if i % 2 == 0:
                    atraso_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FEF2F2')))
            atraso_table.setStyle(TableStyle(atraso_style))
            elements.append(atraso_table)
            
            # Legenda
            elements.append(Spacer(1, 2*mm))
            legenda = "<font size=6 color='#6B7280'>Legenda: BOL = Boleto Gerado | S/B = Sem Boleto | Prorrog. = Data de Prorrogacao</font>"
            elements.append(Paragraph(legenda, ParagraphStyle('leg', fontSize=6, alignment=TA_LEFT)))
        else:
            elements.append(Paragraph("<font size=9 color='#059669'>Nenhum cliente em atraso!</font>", styles['Normal']))
        
        elements.append(Spacer(1, 8*mm))
        
        # ============ FOOTER ============
        elements.append(HRFlowable(width="100%", thickness=1, color=GRAY_LIGHT, spaceBefore=5, spaceAfter=5))
        elements.append(Paragraph(f"<font size=8 color='#9CA3AF'>Sistema VallePrime | {nome_empreendimento}</font>", 
                                  ParagraphStyle('footer', alignment=TA_CENTER)))
        elements.append(Paragraph("<font size=8 color='#6366F1'><b>Desenvolvido por Vinicius Dev</b></font>", 
                                  ParagraphStyle('footer', alignment=TA_CENTER)))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        filename = f"relatorio_{nome_corretor.replace(' ', '_')}.pdf"
        return StreamingResponse(buffer, media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"})
        
    except HTTPException:
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}\n\n{error_details}")

