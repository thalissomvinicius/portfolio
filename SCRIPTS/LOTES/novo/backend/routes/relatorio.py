"""
VallePrime Dashboard - Relatório Routes
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from datetime import datetime
from database import execute_query
import os

router = APIRouter()

@router.get("/relatorio/pdf")
async def gerar_relatorio_pdf(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Gera relatório em PDF"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm, mm
        from reportlab.lib.enums import TA_CENTER
        
        # Importar estilos Valle Prime
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from pdf_styles import (
            AZUL_ESCURO, AZUL_CLARO, VERDE, CINZA_CLARO, LOGO_PATH, 
            format_currency_br, create_header, get_table_style, make_footer_callback
        )
        
        # Buscar nome da obra
        obra_query = f"SELECT Descr_Obr FROM Obras WITH(NOLOCK) WHERE Empresa_Obr = {empresa} AND Cod_Obr = '{obra}'"
        obra_result = execute_query(obra_query)
        nome_obra = obra_result[0].get('Descr_Obr', '') if obra_result else obra
        
        # Buscar dados
        vendas_query = """
        SELECT 
            Vendas.Num_Ven AS venda,
            Pessoas.nome_pes AS cliente,
            Vendas.Obra_Ven + ' - Q' + ISNULL(u.C1_unid, '') + ' L' + ISNULL(u.C2_unid, '') AS identificador,
            PessoasVendedor.nome_pes AS corretor,
            FORMAT(Vendas.Data_Ven, 'dd/MM/yyyy') AS dataVenda,
            (Vendas.ValorTot_Ven + Vendas.Acrescimo_Ven - Vendas.Desconto_Ven) AS valorTotal
        FROM Vendas WITH(NOLOCK)
        INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.cod_pes
        LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
        LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_itv 
            AND Vendas.Obra_Ven = ItensVenda.Obra_Itv 
            AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
        LEFT JOIN UnidadePer u WITH(NOLOCK) ON ItensVenda.Empresa_itv = u.Empresa_unid 
            AND ItensVenda.Produto_Itv = u.Prod_unid 
            AND ItensVenda.CodPerson_Itv = u.NumPer_unid
        WHERE Vendas.Empresa_Ven = ? AND Vendas.Obra_Ven = ?
        ORDER BY Vendas.Num_Ven
        """
        
        boletos_query = """
        SELECT DISTINCT RecebAuto.NumVendPrc_Rea AS venda
        FROM RecebAuto WITH(NOLOCK)
        INNER JOIN Boleto WITH(NOLOCK) 
            ON RecebAuto.SeuNum_Rea = Boleto.SeuNum_Bol
            AND RecebAuto.Banco_Rea = Boleto.Banco_Bol
        WHERE RecebAuto.Empresa_rea = ?
        """
        
        sinais_query = f"""
        SELECT 
            r.NumVend_prc AS venda,
            COUNT(*) AS qtdSinaisAberto
        FROM ContasReceber r WITH(NOLOCK)
        WHERE r.Empresa_prc = {empresa}
          AND r.Obra_Prc = '{obra}'
          AND r.Tipo_Prc = 'S'
          AND r.Status_Prc = 0
        GROUP BY r.NumVend_prc
        """
        
        vendas = execute_query(vendas_query, (empresa, obra))
        boletos_result = execute_query(boletos_query, (empresa,))
        sinais_result = execute_query(sinais_query)
        
        vendas_com_boleto = {b['venda'] for b in boletos_result}
        sinais_map = {s['venda']: s['qtdSinaisAberto'] for s in sinais_result}
        
        # Build resumo
        resumo = []
        for v in vendas:
            resumo.append({
                **v,
                "boletoGerado": "Sim" if v['venda'] in vendas_com_boleto else "Não",
                "sinaisAberto": sinais_map.get(v['venda'], 0)
            })
        
        # Calculate metrics
        total_vendas = len(resumo)
        vendas_com_boleto_count = sum(1 for r in resumo if r['boletoGerado'] == "Sim")
        vendas_sem_boleto = total_vendas - vendas_com_boleto_count
        total_sinais = sum(r['sinaisAberto'] for r in resumo)
        valor_total = sum(r['valorTotal'] or 0 for r in resumo)
        
        # Generate PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                                leftMargin=1*cm, rightMargin=1*cm,
                                topMargin=1*cm, bottomMargin=1*cm)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Cabeçalho com logo Valle Prime
        elements.extend(create_header(
            titulo="VALLE PRIME - RELATÓRIO DE VENDAS",
            nome_obra=nome_obra,
            data_geracao=datetime.now().strftime('%d/%m/%Y %H:%M')
        ))
        
        elements.append(Spacer(1, 5*mm))
        
        # Stats table - cores Valle Prime
        stats_data = [
            ['Total Vendas', 'Com Boleto', 'Sem Boleto', 'Sinais Aberto', 'Valor Total'],
            [str(total_vendas), str(vendas_com_boleto_count), str(vendas_sem_boleto), 
             str(int(total_sinais)), format_currency_br(valor_total)]
        ]
        
        stats_table = Table(stats_data, colWidths=[4*cm, 3*cm, 3*cm, 4*cm, 5*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), AZUL_ESCURO),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, 1), CINZA_CLARO),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 8*mm))
        
        # Data table section
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=AZUL_ESCURO,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph("Detalhamento das Vendas", section_style))
        
        table_data = [['Venda', 'Cliente', 'Identificador', 'Corretor', 'Data', 'Valor', 'Boleto', 'Sinais']]
        for row in resumo:
            table_data.append([
                str(row['venda']),
                str(row['cliente'] or '')[:30],
                str(row['identificador'] or ''),
                str(row['corretor'] or '')[:25],
                str(row['dataVenda'] or ''),
                format_currency_br(row['valorTotal']) if row['valorTotal'] else '0,00',
                str(row['boletoGerado']),
                str(row['sinaisAberto'])
            ])
        
        data_table = Table(table_data, colWidths=[1.5*cm, 5*cm, 3*cm, 4*cm, 2.5*cm, 3*cm, 2*cm, 2*cm])
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), AZUL_ESCURO),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CINZA_CLARO]),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
        ]))
        elements.append(data_table)
        
        # Build com callback de rodapé (footer automático com paginação e assinatura)
        data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M')
        doc.build(elements, onFirstPage=make_footer_callback(data_geracao), onLaterPages=make_footer_callback(data_geracao))
        buffer.seek(0)
        
        filename = f"relatorio_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
        
    except ImportError as e:
        raise HTTPException(status_code=500, detail="Biblioteca reportlab não instalada")
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")

