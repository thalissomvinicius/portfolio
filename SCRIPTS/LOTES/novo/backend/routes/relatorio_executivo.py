"""
Prime Imóveis Dashboard - Relatório Executivo PDF Compacto
Relatório otimizado para caber em UMA PÁGINA
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from database import execute_query
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from datetime import datetime, timedelta
import os

router = APIRouter()

# Cores Valle Prime
AZUL_ESCURO = colors.HexColor('#00528F')
AZUL_MEDIO = colors.HexColor('#0089D6')
VERDE_PRIME = colors.HexColor('#8CC63E')
CINZA_ESCURO = colors.HexColor('#1F2A33')
BRANCO = colors.white
VERMELHO = colors.HexColor('#DC2626')
AMARELO = colors.HexColor('#F59E0B')

STATUS_LABELS = {0: "Disponível", 1: "Vendido", 2: "Reservado", 3: "Proposta", 4: "Quitado", 5: "Escriturado", 
                 6: "Em Venda", 7: "Suspenso", 8: "Fora de Venda", 9: "Em Acerto", 10: "Dação"}

STATUS_COLORS = {0: colors.HexColor('#10B981'), 1: AZUL_ESCURO, 2: AMARELO, 3: colors.HexColor('#8B5CF6'),
                 4: colors.HexColor('#14B8A6'), 5: colors.HexColor('#0891B2'), 6: colors.HexColor('#6366F1'),
                 7: colors.HexColor('#9CA3AF'), 8: colors.HexColor('#6B7280'), 9: colors.HexColor('#EC4899'), 10: colors.HexColor('#78716C')}

def format_currency_br(value):
    if value is None: return "R$ 0,00"
    try: return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def create_pie_chart(data, chart_colors, size=70):
    d = Drawing(size, size)
    pie = Pie()
    pie.x, pie.y, pie.width, pie.height = 5, 5, size-10, size-10
    pie.data, pie.labels, pie.simpleLabels, pie.sideLabels = data, None, 0, 0
    pie.slices.strokeWidth, pie.slices.strokeColor = 1, BRANCO
    for i in range(len(data)):
        if i < len(chart_colors): pie.slices[i].fillColor = chart_colors[i]
    d.add(pie)
    return d

def get_logo_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logoprime.png')

@router.get("/relatorio-executivo/pdf")
async def gerar_relatorio_executivo_pdf(
    empresa: int = Query(...), obra: str = Query(...),
    data_inicio: str = Query(""), data_fim: str = Query("")
):
    try:
        # Período
        if data_inicio and data_fim:
            dt_inicio, dt_fim = datetime.strptime(data_inicio, '%Y-%m-%d'), datetime.strptime(data_fim, '%Y-%m-%d')
        else:
            dt_fim = datetime.now(); dt_inicio = dt_fim - timedelta(days=30)
        data_inicio_str, data_fim_str = dt_inicio.strftime('%Y%m%d'), dt_fim.strftime('%Y%m%d')
        periodo_label = f"{dt_inicio.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')}"
        dias = (dt_fim - dt_inicio).days + 1
        
        # Queries
        obra_result = execute_query(f"SELECT Descr_Obr FROM Obras WITH(NOLOCK) WHERE Empresa_Obr = {empresa} AND Cod_Obr = '{obra}'")
        nome_obra = obra_result[0].get('Descr_Obr', 'Loteamento') if obra_result else 'Loteamento'
        
        status_query = f"""
        SELECT Vendido_Unid as status, COUNT(*) as quantidade, ISNULL(SUM(ValPrecoPerc), 0) as valor FROM (
            SELECT UnidadePer.Vendido_Unid, ROUND(CASE WHEN ud.TipoContrato_Udt IN (1, 2, 4) THEN UnidadePer.ValPreco_Unid
            ELSE ISNULL((SELECT TOP 1 cpp.Valor_Cpp FROM CategoriasPrecoProd cpp WITH(NOLOCK) WHERE cpp.NumProd_Cpp = UnidadePer.Prod_Unid 
            AND cpp.Codigo_Cpp = UnidadePer.Codigo_Unid AND cpp.Empresa_Cpp = UnidadePer.Empresa_Unid AND cpp.Data_Cpp <= GETDATE()
            ORDER BY cpp.Data_Cpp DESC), UnidadePer.ValPreco_Unid) END * (ISNULL(UnidadePer.PorcentPr_Unid, 100) / 100.0) * ISNULL(UnidadePer.Qtde_Unid, 1), 2) as ValPrecoPerc
            FROM UnidadePer WITH(NOLOCK) LEFT JOIN UnidadeDetalhe ud WITH(NOLOCK) ON UnidadePer.Empresa_Unid = ud.Empresa_Udt AND UnidadePer.Prod_Unid = ud.Prod_Udt AND UnidadePer.NumPer_Unid = ud.NumPer_Udt
            WHERE UnidadePer.Empresa_Unid = {empresa} AND UnidadePer.Obra_Unid = '{obra}'
        ) AS SubQuery GROUP BY Vendido_Unid ORDER BY quantidade DESC"""
        status_result = execute_query(status_query)
        total_unidades = sum(r.get('quantidade', 0) for r in status_result)
        total_vgv = sum(float(r.get('valor', 0) or 0) for r in status_result)
        
        vendas_result = execute_query(f"SELECT COUNT(*) as vendas, SUM(ValorTot_Ven) as valor FROM Vendas WITH(NOLOCK) WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}' AND Status_Ven = 0 AND Data_Ven >= CONVERT(datetime, '{data_inicio_str}', 112) AND Data_Ven <= CONVERT(datetime, '{data_fim_str}', 112)")
        total_vendas = vendas_result[0].get('vendas', 0) if vendas_result else 0
        total_valor_vendas = float(vendas_result[0].get('valor', 0) or 0) if vendas_result else 0
        ticket_medio = total_valor_vendas / total_vendas if total_vendas > 0 else 0
        
        cancel_result = execute_query(f"""SELECT (SELECT COUNT(*) FROM Vendas WITH(NOLOCK) WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}' AND Status_Ven = 1 AND COALESCE(DataCancel_Ven, Data_Ven) >= CONVERT(datetime, '{data_inicio_str}', 112) AND COALESCE(DataCancel_Ven, Data_Ven) <= CONVERT(datetime, '{data_fim_str}', 112)) + (SELECT COUNT(*) FROM VendasRecebidas WITH(NOLOCK) WHERE Empresa_VRec = {empresa} AND Obra_VRec = '{obra}' AND Status_VRec = 1 AND COALESCE(DataCancel_VRec, Data_VRec) >= CONVERT(datetime, '{data_inicio_str}', 112) AND COALESCE(DataCancel_VRec, Data_VRec) <= CONVERT(datetime, '{data_fim_str}', 112)) as total, (SELECT ISNULL(SUM(ValorTot_Ven), 0) FROM Vendas WITH(NOLOCK) WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}' AND Status_Ven = 1 AND COALESCE(DataCancel_Ven, Data_Ven) >= CONVERT(datetime, '{data_inicio_str}', 112) AND COALESCE(DataCancel_Ven, Data_Ven) <= CONVERT(datetime, '{data_fim_str}', 112)) + (SELECT ISNULL(SUM(ValorTot_VRec), 0) FROM VendasRecebidas WITH(NOLOCK) WHERE Empresa_VRec = {empresa} AND Obra_VRec = '{obra}' AND Status_VRec = 1 AND COALESCE(DataCancel_VRec, Data_VRec) >= CONVERT(datetime, '{data_inicio_str}', 112) AND COALESCE(DataCancel_VRec, Data_VRec) <= CONVERT(datetime, '{data_fim_str}', 112)) as valor""")
        total_cancel = cancel_result[0].get('total', 0) if cancel_result else 0
        valor_cancel = float(cancel_result[0].get('valor', 0) or 0) if cancel_result else 0
        
        inad_result = execute_query(f"SELECT COUNT(DISTINCT CR.NumVend_prc) as vendas_inad, COUNT(*) as parcelas, ISNULL(SUM(CR.Valor_Prc), 0) as valor FROM ContasReceber CR WITH(NOLOCK) INNER JOIN Vendas V WITH(NOLOCK) ON CR.Empresa_prc = V.Empresa_Ven AND CR.NumVend_prc = V.Num_Ven WHERE CR.Empresa_prc = {empresa} AND CR.Obra_Prc = '{obra}' AND CR.Status_Prc = 0 AND CR.Data_Prc < GETDATE() AND V.Status_Ven = 0")
        vendas_inad = inad_result[0].get('vendas_inad', 0) if inad_result else 0
        parcelas_inad = inad_result[0].get('parcelas', 0) if inad_result else 0
        valor_inad = float(inad_result[0].get('valor', 0) or 0) if inad_result else 0
        
        # Recebimentos - usando a mesma lógica da tela (data de conciliação do Extrato)
        contas_map = {28: "('13005587-5', '529-5', '529-0', '27083-6')", 29: "('13005588-2', '549-0', '31714-8')"}
        contas_filter = contas_map.get(empresa, contas_map[28])
        data_inicio_fmt = f"{dt_inicio.strftime('%d/%m/%Y')}"
        data_fim_fmt = f"{dt_fim.strftime('%d/%m/%Y')}"
        
        receb_result = execute_query(f"""
            SELECT COUNT(*) as qtd, 
            ISNULL(SUM(RecebePgtoDiv.PercentValor_Rpd * (CAST((ItensRecebidas.Qtde_Itr * ItensRecebidas.PrecoProc_Itr - ItensRecebidas.ValComissaoDir_Itr) AS NUMERIC(18, 6)) / NULLIF(VendasRecebidas.ValorTot_VRec, 0))), 0) as valor
            FROM (SELECT * FROM Extrato WITH(NOLOCK) WHERE Tipo_Doc = 1 AND Empresa_doc = {empresa} AND Conta_doc IN {contas_filter} AND Data_Doc BETWEEN '{data_inicio_fmt}' AND '{data_fim_fmt}') [Extrato]
            INNER JOIN Depositos WITH(NOLOCK) ON Extrato.Empresa_Doc = Depositos.Empresa_Dep AND Extrato.Banco_Doc = Depositos.Banco_Dep AND Extrato.Conta_Doc = Depositos.Conta_Dep AND Extrato.Numero_Doc = Depositos.Numero_Dep
            INNER JOIN (SELECT * FROM RecebePgto WITH(NOLOCK) WHERE Status_Rpg <> 2) [RecebePgto] ON Depositos.Empresa_Dep = RecebePgto.Empresa_Rpg AND Depositos.Numero_Dep = RecebePgto.NumDep_Rpg AND Depositos.Banco_Dep = RecebePgto.BancoDep_Rpg AND Depositos.Conta_Dep = RecebePgto.ContaDep_Rpg
            INNER JOIN RecebePgtoDiv WITH(NOLOCK) ON RecebePgto.Empresa_Rpg = RecebePgtoDiv.Empresa_Rpd AND RecebePgto.NumReceb_Rpg = RecebePgtoDiv.NumReceb_Rpd AND RecebePgto.Tipo_Rpg = RecebePgtoDiv.TipoRpg_Rpd AND RecebePgto.NumCont_Rpg = RecebePgtoDiv.NumCont_Rpd
            INNER JOIN Recebidas WITH(NOLOCK) ON RecebePgtoDiv.Empresa_Rpd = Recebidas.Empresa_Rec AND RecebePgtoDiv.Obra_Rpd = Recebidas.Obra_Rec AND RecebePgtoDiv.NumVend_Rpd = Recebidas.NumVend_Rec AND RecebePgtoDiv.NumParc_Rpd = Recebidas.NumParc_Rec AND RecebePgtoDiv.ParcType_Rpd = Recebidas.ParcType_Rec AND RecebePgtoDiv.Tipo_Rpd = Recebidas.Tipo_Rec AND RecebePgtoDiv.NumParcGer_Rpd = Recebidas.NumParcGer_Rec
            INNER JOIN VendasRecebidas WITH(NOLOCK) ON Recebidas.Empresa_Rec = VendasRecebidas.Empresa_VRec AND Recebidas.Obra_Rec = VendasRecebidas.Obra_VRec AND Recebidas.NumVend_Rec = VendasRecebidas.Num_VRec
            INNER JOIN ItensRecebidas WITH(NOLOCK) ON VendasRecebidas.Empresa_VRec = ItensRecebidas.Empresa_Itr AND VendasRecebidas.Obra_VRec = ItensRecebidas.Obra_Itr AND VendasRecebidas.Num_VRec = ItensRecebidas.NumVend_Itr
            WHERE Recebidas.Obra_Rec = '{obra}'
        """)
        qtd_receb = receb_result[0].get('qtd', 0) if receb_result else 0
        valor_receb = float(receb_result[0].get('valor', 0) or 0) if receb_result else 0
        
        receb_tipo_result = execute_query(f"""
            SELECT Recebidas.Tipo_Rec + ' - ' + UPPER(Parcelas.Descricao_Par) as tipo, COUNT(*) as qtd, 
            ISNULL(SUM(RecebePgtoDiv.PercentValor_Rpd * (CAST((ItensRecebidas.Qtde_Itr * ItensRecebidas.PrecoProc_Itr - ItensRecebidas.ValComissaoDir_Itr) AS NUMERIC(18, 6)) / NULLIF(VendasRecebidas.ValorTot_VRec, 0))), 0) as valor
            FROM (SELECT * FROM Extrato WITH(NOLOCK) WHERE Tipo_Doc = 1 AND Empresa_doc = {empresa} AND Conta_doc IN {contas_filter} AND Data_Doc BETWEEN '{data_inicio_fmt}' AND '{data_fim_fmt}') [Extrato]
            INNER JOIN Depositos WITH(NOLOCK) ON Extrato.Empresa_Doc = Depositos.Empresa_Dep AND Extrato.Banco_Doc = Depositos.Banco_Dep AND Extrato.Conta_Doc = Depositos.Conta_Dep AND Extrato.Numero_Doc = Depositos.Numero_Dep
            INNER JOIN (SELECT * FROM RecebePgto WITH(NOLOCK) WHERE Status_Rpg <> 2) [RecebePgto] ON Depositos.Empresa_Dep = RecebePgto.Empresa_Rpg AND Depositos.Numero_Dep = RecebePgto.NumDep_Rpg AND Depositos.Banco_Dep = RecebePgto.BancoDep_Rpg AND Depositos.Conta_Dep = RecebePgto.ContaDep_Rpg
            INNER JOIN RecebePgtoDiv WITH(NOLOCK) ON RecebePgto.Empresa_Rpg = RecebePgtoDiv.Empresa_Rpd AND RecebePgto.NumReceb_Rpg = RecebePgtoDiv.NumReceb_Rpd AND RecebePgto.Tipo_Rpg = RecebePgtoDiv.TipoRpg_Rpd AND RecebePgto.NumCont_Rpg = RecebePgtoDiv.NumCont_Rpd
            INNER JOIN Recebidas WITH(NOLOCK) ON RecebePgtoDiv.Empresa_Rpd = Recebidas.Empresa_Rec AND RecebePgtoDiv.Obra_Rpd = Recebidas.Obra_Rec AND RecebePgtoDiv.NumVend_Rpd = Recebidas.NumVend_Rec AND RecebePgtoDiv.NumParc_Rpd = Recebidas.NumParc_Rec AND RecebePgtoDiv.ParcType_Rpd = Recebidas.ParcType_Rec AND RecebePgtoDiv.Tipo_Rpd = Recebidas.Tipo_Rec AND RecebePgtoDiv.NumParcGer_Rpd = Recebidas.NumParcGer_Rec
            INNER JOIN VendasRecebidas WITH(NOLOCK) ON Recebidas.Empresa_Rec = VendasRecebidas.Empresa_VRec AND Recebidas.Obra_Rec = VendasRecebidas.Obra_VRec AND Recebidas.NumVend_Rec = VendasRecebidas.Num_VRec
            INNER JOIN ItensRecebidas WITH(NOLOCK) ON VendasRecebidas.Empresa_VRec = ItensRecebidas.Empresa_Itr AND VendasRecebidas.Obra_VRec = ItensRecebidas.Obra_Itr AND VendasRecebidas.Num_VRec = ItensRecebidas.NumVend_Itr
            INNER JOIN Parcelas WITH(NOLOCK) ON Recebidas.Tipo_Rec = Parcelas.Tipo_Par
            WHERE Recebidas.Obra_Rec = '{obra}'
            GROUP BY Recebidas.Tipo_Rec, Parcelas.Descricao_Par
            ORDER BY SUM(RecebePgtoDiv.PercentValor_Rpd * (CAST((ItensRecebidas.Qtde_Itr * ItensRecebidas.PrecoProc_Itr - ItensRecebidas.ValComissaoDir_Itr) AS NUMERIC(18, 6)) / NULLIF(VendasRecebidas.ValorTot_VRec, 0))) DESC
        """)
        
        corretores_result = execute_query(f"SELECT TOP 5 P.Nome_Pes as corretor, COUNT(*) as vendas, SUM(V.ValorTot_Ven) as valor FROM Vendas V WITH(NOLOCK) INNER JOIN Pessoas P WITH(NOLOCK) ON V.Vendedor_Ven = P.Cod_Pes WHERE V.Empresa_Ven = {empresa} AND V.Obra_Ven = '{obra}' AND V.Status_Ven = 0 AND V.Data_Ven >= CONVERT(datetime, '{data_inicio_str}', 112) AND V.Data_Ven <= CONVERT(datetime, '{data_fim_str}', 112) GROUP BY P.Nome_Pes ORDER BY vendas DESC")
        
        # Vendas diárias (todo o período)
        vendas_diarias_result = execute_query(f"""
            SELECT CONVERT(VARCHAR(10), Data_Ven, 103) as data, COUNT(*) as vendas, ISNULL(SUM(ValorTot_Ven), 0) as valor
            FROM Vendas WITH(NOLOCK) 
            WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}' AND Status_Ven = 0
              AND Data_Ven >= CONVERT(datetime, '{data_inicio_str}', 112) AND Data_Ven <= CONVERT(datetime, '{data_fim_str}', 112)
            GROUP BY CONVERT(VARCHAR(10), Data_Ven, 103), Data_Ven
            ORDER BY Data_Ven DESC
        """)
        
        # Cancelamentos diários (da tabela VendasRecebidas) com valores
        cancelamentos_diarios_result = execute_query(f"""
            SELECT CONVERT(VARCHAR(10), DataCancel_Vrec, 103) as data, COUNT(*) as cancelamentos, SUM(ValorTot_VRec) as valor
            FROM VendasRecebidas WITH(NOLOCK) 
            WHERE Empresa_VRec = {empresa} AND Obra_VRec = '{obra}' AND Status_VRec = 1
              AND DataCancel_Vrec >= CONVERT(datetime, '{data_inicio_str}', 112) 
              AND DataCancel_Vrec <= CONVERT(datetime, '{data_fim_str}', 112)
            GROUP BY CONVERT(VARCHAR(10), DataCancel_Vrec, 103), DataCancel_Vrec
            ORDER BY DataCancel_Vrec DESC
        """)
        # Criar dict para lookup fácil
        cancel_por_data = {r.get('data'): r.get('cancelamentos', 0) for r in cancelamentos_diarios_result}
        
        # Recebimentos diários (todo o período)
        receb_diarios_result = execute_query(f"""
            SELECT CONVERT(VARCHAR(10), Extrato.Data_Doc, 103) as data, COUNT(*) as qtd, 
            ISNULL(SUM(RecebePgtoDiv.PercentValor_Rpd * (CAST((ItensRecebidas.Qtde_Itr * ItensRecebidas.PrecoProc_Itr - ItensRecebidas.ValComissaoDir_Itr) AS NUMERIC(18, 6)) / NULLIF(VendasRecebidas.ValorTot_VRec, 0))), 0) as valor
            FROM (SELECT * FROM Extrato WITH(NOLOCK) WHERE Tipo_Doc = 1 AND Empresa_doc = {empresa} AND Conta_doc IN {contas_filter} AND Data_Doc BETWEEN '{data_inicio_fmt}' AND '{data_fim_fmt}') [Extrato]
            INNER JOIN Depositos WITH(NOLOCK) ON Extrato.Empresa_Doc = Depositos.Empresa_Dep AND Extrato.Banco_Doc = Depositos.Banco_Dep AND Extrato.Conta_Doc = Depositos.Conta_Dep AND Extrato.Numero_Doc = Depositos.Numero_Dep
            INNER JOIN (SELECT * FROM RecebePgto WITH(NOLOCK) WHERE Status_Rpg <> 2) [RecebePgto] ON Depositos.Empresa_Dep = RecebePgto.Empresa_Rpg AND Depositos.Numero_Dep = RecebePgto.NumDep_Rpg AND Depositos.Banco_Dep = RecebePgto.BancoDep_Rpg AND Depositos.Conta_Dep = RecebePgto.ContaDep_Rpg
            INNER JOIN RecebePgtoDiv WITH(NOLOCK) ON RecebePgto.Empresa_Rpg = RecebePgtoDiv.Empresa_Rpd AND RecebePgto.NumReceb_Rpg = RecebePgtoDiv.NumReceb_Rpd AND RecebePgto.Tipo_Rpg = RecebePgtoDiv.TipoRpg_Rpd AND RecebePgto.NumCont_Rpg = RecebePgtoDiv.NumCont_Rpd
            INNER JOIN Recebidas WITH(NOLOCK) ON RecebePgtoDiv.Empresa_Rpd = Recebidas.Empresa_Rec AND RecebePgtoDiv.Obra_Rpd = Recebidas.Obra_Rec AND RecebePgtoDiv.NumVend_Rpd = Recebidas.NumVend_Rec AND RecebePgtoDiv.NumParc_Rpd = Recebidas.NumParc_Rec AND RecebePgtoDiv.ParcType_Rpd = Recebidas.ParcType_Rec AND RecebePgtoDiv.Tipo_Rpd = Recebidas.Tipo_Rec AND RecebePgtoDiv.NumParcGer_Rpd = Recebidas.NumParcGer_Rec
            INNER JOIN VendasRecebidas WITH(NOLOCK) ON Recebidas.Empresa_Rec = VendasRecebidas.Empresa_VRec AND Recebidas.Obra_Rec = VendasRecebidas.Obra_VRec AND Recebidas.NumVend_Rec = VendasRecebidas.Num_VRec
            INNER JOIN ItensRecebidas WITH(NOLOCK) ON VendasRecebidas.Empresa_VRec = ItensRecebidas.Empresa_Itr AND VendasRecebidas.Obra_VRec = ItensRecebidas.Obra_Itr AND VendasRecebidas.Num_VRec = ItensRecebidas.NumVend_Itr
            WHERE Recebidas.Obra_Rec = '{obra}'
            GROUP BY CONVERT(VARCHAR(10), Extrato.Data_Doc, 103), Extrato.Data_Doc
            ORDER BY Extrato.Data_Doc DESC
        """)
        
        # PDF COMPACTO - UMA PÁGINA
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=10*mm, rightMargin=10*mm, topMargin=2*mm, bottomMargin=8*mm)
        elements = []
        
        # CABEÇALHO COMPACTO
        logo_path = get_logo_path()
        try:
            from PIL import Image as PILImage
            with PILImage.open(logo_path) as img:
                w, h = img.size
                aspect = w / h
                logo = Image(logo_path, width=20*mm, height=20*mm/aspect)
        except:
            try: logo = Image(logo_path, width=20*mm, height=8*mm)
            except: logo = Paragraph("<b>PRIME</b>", ParagraphStyle('L', fontSize=12, textColor=AZUL_ESCURO))
        
        header_center = Paragraph(f"<b>RELATÓRIO EXECUTIVO</b><br/><font size=8 color='#64748B'>{nome_obra.upper()}</font>", 
                                   ParagraphStyle('T', fontSize=11, textColor=AZUL_ESCURO, alignment=TA_CENTER, leading=12))
        header_right = Paragraph(f"<font size=8 color='#64748B'>Período: {periodo_label}</font><br/><font size=7 color='#9CA3AF'>{datetime.now().strftime('%d/%m/%Y %H:%M')}</font>",
                                  ParagraphStyle('D', alignment=TA_RIGHT, leading=10))
        
        header = Table([[logo, header_center, header_right]], colWidths=[25*mm, 115*mm, 50*mm])
        header.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'CENTER'), ('ALIGN', (2, 0), (2, 0), 'RIGHT'), ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
        elements.append(header)
        
        # Linha divisória
        div = Table([['']], colWidths=[190*mm])
        div.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1.5, AZUL_ESCURO), ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
        elements.append(div)

        
        section_style = ParagraphStyle('S', fontSize=7, textColor=AZUL_ESCURO, fontName='Helvetica-Bold', spaceBefore=0*mm, spaceAfter=0*mm)
        
        # RESUMO COMPACTO
        elements.append(Paragraph("RESUMO DO EMPREENDIMENTO", section_style))
        resumo = Table([['UNIDADES', 'VGV TOTAL', 'VENDAS', 'VALOR VENDAS', 'TICKET MÉDIO'],
                        [str(total_unidades), format_currency_br(total_vgv), str(total_vendas), format_currency_br(total_valor_vendas), format_currency_br(ticket_medio)]],
                       colWidths=[28*mm, 50*mm, 20*mm, 50*mm, 42*mm])
        resumo.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), AZUL_ESCURO), ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO), ('FONTSIZE', (0, 0), (-1, 0), 7),
                                    ('FONTSIZE', (0, 1), (-1, 1), 9), ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2), ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#E0F2FE')), ('BOX', (0, 0), (-1, -1), 1, AZUL_ESCURO)]))
        elements.append(resumo)
        elements.append(Spacer(1, 1*mm))
        
        # INDICADORES
        ind = Table([['CANCELAMENTOS', 'VALOR CANCEL.', 'RECEBIMENTOS', 'VALOR RECEBIDO'],
                     [str(total_cancel), format_currency_br(valor_cancel), str(qtd_receb), format_currency_br(valor_receb)]],
                    colWidths=[40*mm, 55*mm, 40*mm, 55*mm])
        ind.setStyle(TableStyle([('BACKGROUND', (0, 0), (1, 0), VERMELHO), ('BACKGROUND', (2, 0), (3, 0), VERDE_PRIME), ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO),
                                 ('FONTSIZE', (0, 0), (-1, 0), 7), ('FONTSIZE', (0, 1), (-1, 1), 9), ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                 ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                                 ('BACKGROUND', (0, 1), (1, 1), colors.HexColor('#FEE2E2')), ('BACKGROUND', (2, 1), (3, 1), colors.HexColor('#D1FAE5')), ('BOX', (0, 0), (1, -1), 1, VERMELHO), ('BOX', (2, 0), (3, -1), 1, VERDE_PRIME)]))
        elements.append(ind)
        elements.append(Spacer(1, 1*mm))
        
        # STATUS COM PIZZA
        elements.append(Paragraph("DISTRIBUIÇÃO POR STATUS", section_style))
        status_sorted = sorted(status_result, key=lambda x: x.get('quantidade', 0), reverse=True)[:6]
        pie_data = [r.get('quantidade', 0) for r in status_sorted]
        pie_colors = [STATUS_COLORS.get(r.get('status', 0), colors.HexColor('#888')) for r in status_sorted]
        
        if pie_data:
            pie = create_pie_chart(pie_data, pie_colors, 65)
            legend_rows = [['Status', 'Qtd', '%', 'Valor']]
            total_status_qtd = 0
            total_status_valor = 0
            for i, r in enumerate(status_sorted):
                s = r.get('status', 0); q = r.get('quantidade', 0); v = float(r.get('valor', 0) or 0)
                total_status_qtd += q
                total_status_valor += v
                legend_rows.append([STATUS_LABELS.get(s, f'S{s}'), str(q), f'{q/total_unidades*100:.0f}%' if total_unidades else '0%', format_currency_br(v)])
            # Adicionar linha TOTAL
            legend_rows.append(['TOTAL', str(total_status_qtd), '100%', format_currency_br(total_status_valor)])
            legend = Table(legend_rows, colWidths=[28*mm, 12*mm, 10*mm, 42*mm])
            style_cmds = [('BACKGROUND', (0, 0), (-1, 0), CINZA_ESCURO), ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO), ('FONTSIZE', (0, 0), (-1, -1), 7),
                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('ALIGN', (0, 1), (0, -1), 'LEFT'), ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                         ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
                         ('BACKGROUND', (0, -1), (-1, -1), AZUL_ESCURO), ('TEXTCOLOR', (0, -1), (-1, -1), BRANCO), ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')]
            for i in range(len(status_sorted)): style_cmds.extend([('BACKGROUND', (0, i+1), (0, i+1), pie_colors[i]), ('TEXTCOLOR', (0, i+1), (0, i+1), BRANCO)])
            legend.setStyle(TableStyle(style_cmds))
            combo = Table([[pie, legend]], colWidths=[35*mm, 95*mm])
            combo.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
            elements.append(combo)
        elements.append(Spacer(1, 1*mm))
        
        # INADIMPLÊNCIA + RECEBIMENTOS LADO A LADO
        elements.append(Paragraph("INADIMPLÊNCIA E RECEBIMENTOS POR TIPO", section_style))
        
        # Inadimplência mini
        inad_table = Table([['V. Atraso', 'Parcelas', 'Valor', '% VGV'], [str(vendas_inad), str(parcelas_inad), format_currency_br(valor_inad), f'{valor_inad/total_vgv*100:.2f}%' if total_vgv else '0%']],
                           colWidths=[18*mm, 18*mm, 30*mm, 18*mm])
        inad_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#991B1B')), ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO), ('FONTSIZE', (0, 0), (-1, -1), 6),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                                        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FEF2F2')), ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#991B1B'))]))
        
        # Recebimentos por tipo mini
        tipo_rows = [['Tipo', 'Qtd', 'Valor']]
        total_tipo_qtd = 0
        total_tipo_valor = 0
        for r in receb_tipo_result[:4]:
            t = r.get('tipo', '-'); t = t[:18] + '..' if len(t) > 20 else t
            qtd = r.get('qtd', 0)
            valor = float(r.get('valor', 0) or 0)
            total_tipo_qtd += qtd
            total_tipo_valor += valor
            tipo_rows.append([t, str(qtd), format_currency_br(valor)])
        # Adicionar linha TOTAL
        tipo_rows.append(['TOTAL', str(total_tipo_qtd), format_currency_br(total_tipo_valor)])
        tipo_table = Table(tipo_rows, colWidths=[35*mm, 12*mm, 35*mm])
        tipo_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), VERDE_PRIME), ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO), ('FONTSIZE', (0, 0), (-1, -1), 6),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('ALIGN', (0, 1), (0, -1), 'LEFT'), ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                                        ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#A7F3D0')),
                                        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#166534')), ('TEXTCOLOR', (0, -1), (-1, -1), BRANCO), ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')]))
        
        side = Table([[inad_table, '', tipo_table]], colWidths=[88*mm, 5*mm, 85*mm])
        side.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        elements.append(side)
        elements.append(Spacer(1, 1*mm))
        
        # TOP 5 CORRETORES E RESUMO DIÁRIO lado a lado
        elements.append(Paragraph("TOP 5 CORRETORES E RESUMO DIÁRIO", section_style))
        
        # Título para Corretores
        corr_title = Paragraph("<b>RANKING CORRETORES</b>", ParagraphStyle('CT', fontSize=7, textColor=AZUL_ESCURO, alignment=TA_CENTER))
        
        # Corretores
        corr_rows = [['#', 'Corretor', 'V', 'Valor']]
        if corretores_result:
            for i, c in enumerate(corretores_result[:5], 1):
                nome = c.get('corretor', '-'); nome = nome[:18] + '..' if len(nome) > 20 else nome
                corr_rows.append([str(i), nome.upper(), str(c.get('vendas', 0)), format_currency_br(float(c.get('valor', 0) or 0))])
        else:
            corr_rows.append(['-', 'Sem vendas no período', '-', 'R$ 0,00'])
        corr_table = Table(corr_rows, colWidths=[6*mm, 45*mm, 8*mm, 35*mm])
        corr_style = [('BACKGROUND', (0, 0), (-1, 0), AZUL_ESCURO), ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO), ('FONTSIZE', (0, 0), (-1, -1), 6),
                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('ALIGN', (1, 1), (1, -1), 'LEFT'), ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                     ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BFDBFE')),
                     ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FEF3C7')), ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#E5E7EB')), ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#FED7AA'))]
        corr_table.setStyle(TableStyle(corr_style))
        
        # Container corretores com título
        corr_container = Table([[corr_title], [corr_table]], colWidths=[96*mm])
        corr_container.setStyle(TableStyle([('BOTTOMPADDING', (0, 0), (0, 0), 2)]))
        
        # Título para Vendas 
        vendas_title = Paragraph("<b>VENDAS DIÁRIAS</b>", ParagraphStyle('VT', fontSize=7, textColor=VERDE_PRIME, alignment=TA_CENTER))
        
        # Vendas diárias - calcular totais
        total_vendas_qtd = sum(d.get('vendas', 0) for d in vendas_diarias_result)
        total_vendas_valor = sum(float(d.get('valor', 0) or 0) for d in vendas_diarias_result)
        
        diario_rows = [['Data', 'Qtd', 'Valor']]
        if vendas_diarias_result:
            for d in vendas_diarias_result:
                diario_rows.append([d.get('data', '-'), str(d.get('vendas', 0)), format_currency_br(float(d.get('valor', 0) or 0))])
            # Linha de total
            diario_rows.append(['TOTAL', str(total_vendas_qtd), format_currency_br(total_vendas_valor)])
        else:
            diario_rows.append(['-', '0', 'R$ 0,00'])
            diario_rows.append(['TOTAL', '0', 'R$ 0,00'])
        
        diario_table = Table(diario_rows, colWidths=[18*mm, 10*mm, 50*mm])
        diario_style = [('BACKGROUND', (0, 0), (-1, 0), VERDE_PRIME), ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO), ('FONTSIZE', (0, 0), (-1, -1), 6),
                       ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                       ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#A7F3D0')),
                       ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#166534')), ('TEXTCOLOR', (0, -1), (-1, -1), BRANCO), ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')]
        diario_table.setStyle(TableStyle(diario_style))
        
        # Container vendas com título
        vendas_container = Table([[vendas_title], [diario_table]], colWidths=[80*mm])
        vendas_container.setStyle(TableStyle([('BOTTOMPADDING', (0, 0), (0, 0), 2)]))
        
        # Título para Recebimentos
        receb_title = Paragraph("<b>RECEBIMENTOS DIÁRIOS</b>", ParagraphStyle('RT', fontSize=7, textColor=colors.HexColor('#0369A1'), alignment=TA_CENTER))
        
        # Recebimentos diários - calcular totais
        total_receb_qtd = sum(r.get('qtd', 0) for r in receb_diarios_result)
        total_receb_valor = sum(float(r.get('valor', 0) or 0) for r in receb_diarios_result)
        
        receb_rows = [['Data', 'Qtd', 'Valor']]
        if receb_diarios_result:
            for r in receb_diarios_result:
                receb_rows.append([r.get('data', '-'), str(r.get('qtd', 0)), format_currency_br(float(r.get('valor', 0) or 0))])
            # Linha de total
            receb_rows.append(['TOTAL', str(total_receb_qtd), format_currency_br(total_receb_valor)])
        else:
            receb_rows.append(['-', '0', 'R$ 0,00'])
            receb_rows.append(['TOTAL', '0', 'R$ 0,00'])
        
        receb_table = Table(receb_rows, colWidths=[18*mm, 10*mm, 55*mm])
        receb_style = [('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0369A1')), ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO), ('FONTSIZE', (0, 0), (-1, -1), 6),
                      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                      ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#7DD3FC')),
                      ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#0C4A6E')), ('TEXTCOLOR', (0, -1), (-1, -1), BRANCO), ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')]
        receb_table.setStyle(TableStyle(receb_style))
        
        # Container recebimentos com título
        receb_container = Table([[receb_title], [receb_table]], colWidths=[85*mm])
        receb_container.setStyle(TableStyle([('BOTTOMPADDING', (0, 0), (0, 0), 2)]))
        
        # Título para Cancelamentos
        cancel_title = Paragraph("<b>CANCELAMENTOS DIÁRIOS</b>", ParagraphStyle('CT', fontSize=7, textColor=colors.HexColor('#B91C1C'), alignment=TA_CENTER))
        
        # Cancelamentos diários - calcular totais (com valores)
        total_cancel_qtd = sum(c.get('cancelamentos', 0) for c in cancelamentos_diarios_result)
        total_cancel_valor = sum(float(c.get('valor', 0) or 0) for c in cancelamentos_diarios_result)
        
        cancel_rows = [['Data', 'Qtd', 'Valor']]
        if cancelamentos_diarios_result:
            for c in cancelamentos_diarios_result:
                cancel_rows.append([c.get('data', '-'), str(c.get('cancelamentos', 0)), format_currency_br(float(c.get('valor', 0) or 0))])
            cancel_rows.append(['TOTAL', str(total_cancel_qtd), format_currency_br(total_cancel_valor)])
        else:
            cancel_rows.append(['-', '0', 'R$ 0,00'])
            cancel_rows.append(['TOTAL', '0', 'R$ 0,00'])
        
        cancel_table = Table(cancel_rows, colWidths=[18*mm, 10*mm, 55*mm])
        cancel_style = [('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B91C1C')), ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO), ('FONTSIZE', (0, 0), (-1, -1), 6),
                       ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                       ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#FECACA')),
                       ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#7F1D1D')), ('TEXTCOLOR', (0, -1), (-1, -1), BRANCO), ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')]
        cancel_table.setStyle(TableStyle(cancel_style))
        
        # Container cancelamentos com título
        cancel_container = Table([[cancel_title], [cancel_table]], colWidths=[85*mm])
        cancel_container.setStyle(TableStyle([('BOTTOMPADDING', (0, 0), (0, 0), 2)]))
        
        # LAYOUT REORGANIZADO: 2 LINHAS
        # Linha 1: Corretores (grande) | Vendas Diárias
        row1 = Table([[corr_container, '', vendas_container]], colWidths=[100*mm, 5*mm, 85*mm])
        row1.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        elements.append(row1)
        elements.append(Spacer(1, 1*mm))
        
        # Linha 2: Cancelamentos Diários | Recebimentos Diários
        row2 = Table([[cancel_container, '', receb_container]], colWidths=[95*mm, 5*mm, 95*mm])
        row2.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        elements.append(row2)
        
        # RODAPÉ
        elements.append(Spacer(1, 2*mm))
        elements.append(Paragraph("Prime Imóveis - Sistema de Controle de Vendas e Boletos | © 2025 Valle Prime", ParagraphStyle('F', fontSize=7, textColor=colors.HexColor('#9CA3AF'), alignment=TA_CENTER)))
        elements.append(Paragraph("Desenvolvido por Vinicius Dev", ParagraphStyle('F2', fontSize=7, textColor=colors.HexColor('#64748B'), alignment=TA_CENTER, fontName='Helvetica-Oblique')))
        
        doc.build(elements)
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_executivo_{obra}.pdf"})
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}\n{traceback.format_exc()}")
