"""
VallePrime Dashboard - Inadimplentes Routes
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from datetime import datetime
from typing import Optional
from database import execute_query

router = APIRouter()

def get_inadimplentes_query(empresa: int, obra: str, dias_minimo: int, corretor: str = None, estrutura: int = None):
    """Retorna a query de inadimplentes"""
    corretor_filter = f"AND PessoasVendedor.nome_pes = '{corretor}'" if corretor else ""
    
    # Filtro de estrutura
    estrutura_join = ""
    estrutura_where = ""
    
    if estrutura:
        estrutura_join = """
        INNER JOIN (SELECT DISTINCT CodPes_hqi, CodPesSuper_hqi FROM HierarquiaIntegrante WITH(NOLOCK)) HI 
            ON Vendas.Vendedor_Ven = HI.CodPes_hqi
        """
        estrutura_where = f"AND HI.CodPesSuper_hqi = {estrutura}"
    
    return f"""
    SELECT 
        CR2.Venda AS venda,
        Pessoas.nome_pes AS cliente,
        UPPER(UnidadePer.Identificador_unid) AS identificador,
        ISNULL(UnidadePer.C1_unid, '') AS quadra,
        ISNULL(UnidadePer.C2_unid, '') AS lote,
        PessoasVendedor.nome_pes AS corretor,
        Parcelas.Descricao_par AS tipoParcela,
        CAST(CR.NumParc_prc AS VARCHAR) + '/' + CAST(CR.TotParc_prc AS VARCHAR) AS parcelaNumero,
        FORMAT(CR.Data_Prc, 'dd/MM/yyyy') AS dataVencimento,
        CR.Data_Prc AS dataVencimentoRaw,
        DATEDIFF(DAY, CAST(CR.Data_Prc AS DATE), GETDATE()) AS diasAtraso,
        CR.Valor_Prc AS valor,
        Pessoas.Email_pes AS email,
        PesTel.FoneCel AS telefone,
        FORMAT(CR.DataPror_Prc, 'dd/MM/yyyy') AS dataProrrogacao,
        CR.DataPror_Prc AS dataProrrogacaoRaw,
        CASE 
            WHEN CR.DataPror_Prc IS NOT NULL AND CR.DataPror_Prc > CR.Data_Prc 
            THEN 1 
            ELSE 0 
        END AS foiProrrogado,
        CASE 
            WHEN CR.DataPror_Prc IS NOT NULL AND CR.DataPror_Prc > CR.Data_Prc 
                 AND CR.DataPror_Prc < CAST(GETDATE() AS DATE)
            THEN 1 
            ELSE 0 
        END AS prorrogacaoVencida
    FROM ContasReceber CR WITH(NOLOCK)
    
    INNER JOIN (
        SELECT 
            MAX(DATEDIFF(DAY, CAST(Data_prc AS DATE), CAST(GETDATE() AS DATE))) AS DiasAtraso,
            Empresa_prc AS Empresa, Obra_Prc AS Obra, NumVend_prc AS Venda
        FROM ContasReceber WITH(NOLOCK)
        WHERE Tipo_Prc != '1' AND Status_Prc = 0
        GROUP BY Empresa_prc, Obra_Prc, NumVend_prc
    ) AS CR2
        ON CR.Empresa_prc = CR2.Empresa
        AND CR.Obra_Prc = CR2.Obra
        AND CR.NumVend_prc = CR2.Venda

    INNER JOIN Parcelas WITH(NOLOCK) ON Parcelas.Tipo_par = CR.Tipo_Prc

    INNER JOIN ItensVenda WITH(NOLOCK)
        ON CR.Empresa_prc = ItensVenda.Empresa_itv
        AND CR.Obra_Prc = ItensVenda.Obra_itv
        AND CR.NumVend_prc = ItensVenda.NumVend_itv

    LEFT OUTER JOIN UnidadePer WITH(NOLOCK)
        ON ItensVenda.Empresa_itv = UnidadePer.Empresa_unid
        AND ItensVenda.Obra_itv = UnidadePer.Obra_unid
        AND ItensVenda.Produto_itv = UnidadePer.Prod_unid
        AND ItensVenda.CodPerson_itv = UnidadePer.NumPer_unid

    INNER JOIN VendaClientes WITH(NOLOCK)
        ON CR.Empresa_prc = VendaClientes.Empresa_cven
        AND CR.Obra_Prc = VendaClientes.Obra_cven
        AND CR.NumVend_prc = VendaClientes.Num_cven

    INNER JOIN Pessoas WITH(NOLOCK) ON Pessoas.cod_pes = VendaClientes.Cliente_cven

    INNER JOIN Vendas WITH(NOLOCK)
        ON CR.Empresa_prc = Vendas.Empresa_Ven
        AND CR.Obra_Prc = Vendas.Obra_Ven
        AND CR.NumVend_prc = Vendas.Num_Ven

    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) 
        ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
        
    {estrutura_join}

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

    WHERE CR.Empresa_prc = {empresa}
      AND CR.Obra_Prc = '{obra}'
      AND CR.Status_Prc = 0
      AND CR2.DiasAtraso >= {dias_minimo}
      AND DATEDIFF(DAY, CAST(CR.Data_Prc AS DATE), GETDATE()) > 0
      AND CR.Tipo_Prc != '1'
      {corretor_filter}
      {estrutura_where}
    ORDER BY PessoasVendedor.nome_pes, Pessoas.nome_pes, CR2.Venda, CR.Data_Prc
    """

@router.get("/inadimplentes")
async def get_inadimplentes(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    dias_minimo: int = Query(1, description="Dias mínimos de atraso"),
    estrutura: Optional[int] = Query(None, description="Filtrar por estrutura")
):
    """Busca boletos em atraso"""
    query = get_inadimplentes_query(empresa, obra, dias_minimo, estrutura=estrutura)
    
    try:
        results = execute_query(query)
        
        # Calculate metrics
        total = len(results)
        valor_total = sum(r.get('valor', 0) or 0 for r in results)
        
        # Group by days range
        ate_30 = len([r for r in results if r.get('diasAtraso', 0) <= 30])
        de_31_a_60 = len([r for r in results if 31 <= r.get('diasAtraso', 0) <= 60])
        de_61_a_90 = len([r for r in results if 61 <= r.get('diasAtraso', 0) <= 90])
        mais_90 = len([r for r in results if r.get('diasAtraso', 0) > 90])
        
        return {
            "data": results,
            "total": total,
            "metrics": {
                "totalBoletos": total,
                "valorTotal": valor_total,
                "ate30Dias": ate_30,
                "de31a60Dias": de_31_a_60,
                "de61a90Dias": de_61_a_90,
                "mais90Dias": mais_90
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inadimplentes/pdf")
async def gerar_pdf_inadimplentes(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    dias_minimo: int = Query(1, description="Dias mínimos de atraso"),
    corretor: str = Query(None, description="Filtrar por corretor"),
    estrutura: Optional[int] = Query(None, description="Filtrar por estrutura")
):
    """Gera PDF de inadimplentes para cobrança com coluna de anotações"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm, mm
        from reportlab.lib.enums import TA_CENTER
        import os
        
        # Importar estilos Valle Prime
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from pdf_styles import AZUL_ESCURO, AZUL_CLARO, VERDE, CINZA_CLARO, LOGO_PATH, format_currency_br, make_footer_callback
        
        # Buscar dados
        query = get_inadimplentes_query(empresa, obra, dias_minimo, corretor, estrutura)
        results = execute_query(query)
        
        if not results:
            raise HTTPException(status_code=404, detail="Nenhum inadimplente encontrado")
        
        # Buscar nome da obra
        obra_query = f"SELECT Descr_Obr FROM Obras WITH(NOLOCK) WHERE Empresa_Obr = {empresa} AND Cod_Obr = '{obra}'"
        obra_result = execute_query(obra_query)
        nome_obra = obra_result[0].get('Descr_Obr', '') if obra_result else obra

        # Buscar nome da estrutura se houver
        nome_estrutura = ""
        if estrutura:
            est_query = f"SELECT nome_pes FROM Pessoas WITH(NOLOCK) WHERE Cod_pes = {estrutura}"
            est_result = execute_query(est_query)
            if est_result:
                nome_estrutura = est_result[0].get('nome_pes', '')
        
        # Gerar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=landscape(A4),
            leftMargin=0.5*cm, 
            rightMargin=0.5*cm,
            topMargin=0.5*cm, 
            bottomMargin=0.5*cm
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilos Valle Prime
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=AZUL_ESCURO,
            spaceAfter=3,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6B7280'),
            spaceAfter=10,
            alignment=TA_CENTER
        )
        
        corretor_header_style = ParagraphStyle(
            'CorretorHeader',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.white,
            backColor=AZUL_ESCURO,
            spaceAfter=5,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        # Agrupar por corretor
        from collections import defaultdict
        por_corretor = defaultdict(list)
        for row in results:
            corretor_nome = row.get('corretor') or 'SEM CORRETOR'
            por_corretor[corretor_nome].append(row)
        
        # Calcular totais
        total_parcelas = len(results)
        valor_total = sum(r.get('valor', 0) or 0 for r in results)
        
        # Logo
        if os.path.exists(LOGO_PATH):
            try:
                from PIL import Image as PILImage
                with PILImage.open(LOGO_PATH) as pil_img:
                    img_width, img_height = pil_img.size
                    aspect_ratio = img_width / img_height
                    target_height = 14*mm
                    target_width = target_height * aspect_ratio
                
                logo = Image(LOGO_PATH, width=target_width, height=target_height)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 3*mm))
            except:
                pass
        
        # Cabeçalho
        title_text = "RELATÓRIO DE INADIMPLÊNCIA"
        if estrutura:
             title_text += f" - ESTRUTURA {nome_estrutura}"
             
        elements.append(Paragraph(f"VALLE PRIME - {title_text}", title_style))
        data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        filtro_info = f" | Dias mín. atraso: {dias_minimo}"
        if corretor:
            filtro_info += f" | Corretor: {corretor}"
        if estrutura:
            filtro_info += f" | Estrutura: {nome_estrutura}"
            
        elements.append(Paragraph(
            f"{nome_obra}{filtro_info} | Gerado: {data_geracao}", 
            subtitle_style
        ))
        
        # Resumo com cores Valle Prime
        resumo_data = [
            ['Total Parcelas', 'Valor Total', 'Corretores'],
            [str(total_parcelas), format_currency_br(valor_total), str(len(por_corretor))]
        ]
        resumo_table = Table(resumo_data, colWidths=[6*cm, 8*cm, 5*cm])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), AZUL_ESCURO),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (-1, 1), CINZA_CLARO),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(resumo_table)
        elements.append(Spacer(1, 15))
        
        # Para cada corretor
        for corretor_nome in sorted(por_corretor.keys()):
            parcelas = por_corretor[corretor_nome]
            valor_corretor = sum(p.get('valor', 0) or 0 for p in parcelas)
            
            # Header do corretor
            header_text = f"👤 {corretor_nome} - {len(parcelas)} parcelas - R$ {valor_corretor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            elements.append(Paragraph(header_text, corretor_header_style))
            
            # Tabela de parcelas
            table_data = [['Venda', 'Q', 'L', 'Cliente', 'Tipo', 'Parc.', 'Venc.', 'Dias', 'Valor', 'Prorr.', 'Telefone', 'Anotações']]
            
            for row in parcelas:
                def safe_str(val, max_len=None):
                    s = str(val) if val else '-'
                    if max_len and len(s) > max_len:
                        s = s[:max_len-2] + '..'
                    return s
                
                valor_fmt = f"R$ {row['valor']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if row.get('valor') else 'R$ 0,00'
                
                # Prorrogado: SIM com data ou -
                prorr = row.get('dataProrrogacao') if row.get('foiProrrogado') == 1 else '-'
                
                table_data.append([
                    safe_str(row.get('venda')),
                    safe_str(row.get('quadra')),
                    safe_str(row.get('lote')),
                    safe_str(row.get('cliente'), 22),
                    safe_str(row.get('tipoParcela'), 10),
                    safe_str(row.get('parcelaNumero')),
                    safe_str(row.get('dataVencimento')),
                    str(row.get('diasAtraso', 0)),
                    valor_fmt,
                    prorr,
                    safe_str(row.get('telefone'), 12),
                    ''  # Coluna de anotações em branco
                ])
            
            # Criar tabela
            col_widths = [1.1*cm, 0.7*cm, 0.7*cm, 4*cm, 2*cm, 1*cm, 1.8*cm, 0.8*cm, 2.2*cm, 1.8*cm, 2.4*cm, 5.5*cm]
            data_table = Table(table_data, colWidths=col_widths)
            
            data_table.setStyle(TableStyle([
                # Header - Azul Valle Prime
                ('BACKGROUND', (0, 0), (-1, 0), AZUL_ESCURO),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),
                ('TOPPADDING', (0, 0), (-1, 0), 4),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                
                # Data rows
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (0, 1), (2, -1), 'CENTER'),  # Venda, Q, L
                ('ALIGN', (5, 1), (7, -1), 'CENTER'),  # Parc, Venc, Dias
                ('ALIGN', (8, 1), (8, -1), 'RIGHT'),   # Valor
                ('ALIGN', (9, 1), (9, -1), 'CENTER'),  # Prorr
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                
                # Anotações column - altura extra para escrever
                ('BACKGROUND', (11, 1), (11, -1), colors.HexColor('#F0FDF4')),
                
                # Grid - cores Valle Prime
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('BOX', (0, 0), (-1, -1), 1, AZUL_ESCURO),
                
                # Alternating rows
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CINZA_CLARO]),
                
                # Dias atraso - cor de alerta
                ('TEXTCOLOR', (7, 1), (7, -1), colors.HexColor('#DC2626')),
                ('FONTNAME', (7, 1), (7, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(data_table)
            elements.append(Spacer(1, 10))
        
        # Rodapé
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#9CA3AF'),
            alignment=TA_CENTER
        )
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("Sistema VallePrime - Relatório de Cobrança para Corretores", footer_style))
        elements.append(Paragraph("© 2025 - Desenvolvido por Vinicius Dev", footer_style))
        
        # Build com callback de rodapé
        doc.build(elements, onFirstPage=make_footer_callback(data_geracao), onLaterPages=make_footer_callback(data_geracao))
        buffer.seek(0)
        
        filename = f"cobranca_inadimplentes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
        
    except ImportError:
        raise HTTPException(status_code=500, detail="Biblioteca reportlab não instalada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
