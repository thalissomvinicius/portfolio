"""
Valle Prime - Estilos compartilhados para PDFs
Paleta de cores e funções utilitárias para geração de PDFs profissionais
"""

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.units import mm
import os

# Cores Valle Prime
AZUL_ESCURO = colors.HexColor('#00528F')
AZUL_CLARO = colors.HexColor('#0089D6')
VERDE = colors.HexColor('#8CC63E')
CINZA_TEXTO = colors.HexColor('#1F2A33')
CINZA_SECUNDARIO = colors.HexColor('#6B7280')
CINZA_CLARO = colors.HexColor('#F8FAFC')
BRANCO = colors.white

# Caminho do logo
LOGO_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'logoprime.png')


def get_header_style():
    """Retorna estilo para título principal"""
    return ParagraphStyle(
        'HeaderStyle',
        fontSize=18,
        textColor=AZUL_ESCURO,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=3*mm
    )


def get_subtitle_style():
    """Retorna estilo para subtítulo"""
    return ParagraphStyle(
        'SubtitleStyle',
        fontSize=10,
        textColor=CINZA_SECUNDARIO,
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=5*mm
    )


def get_section_style():
    """Retorna estilo para seções"""
    return ParagraphStyle(
        'SectionStyle',
        fontSize=12,
        textColor=AZUL_ESCURO,
        fontName='Helvetica-Bold',
        spaceBefore=8*mm,
        spaceAfter=4*mm
    )


def get_table_style(has_footer=True):
    """Retorna estilo padrão para tabelas Valle Prime"""
    style = [
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_ESCURO),
        ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Body
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        
        # Linhas alternadas (zebra)
        ('ROWBACKGROUNDS', (0, 1), (-1, -2 if has_footer else -1), [BRANCO, CINZA_CLARO]),
    ]
    
    if has_footer:
        # Footer
        style.extend([
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F5E9')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, -1), (-1, -1), AZUL_ESCURO),
        ])
    
    return TableStyle(style)


def create_header(titulo: str, subtitulo: str = "", nome_obra: str = "", data_geracao: str = ""):
    """Cria cabeçalho padrão para PDFs Valle Prime"""
    elements = []
    
    # Logo (se existir)
    if os.path.exists(LOGO_PATH):
        try:
            # Usar proporção original da imagem
            from PIL import Image as PILImage
            with PILImage.open(LOGO_PATH) as img:
                img_width, img_height = img.size
                aspect_ratio = img_width / img_height
                # Altura desejada de 20mm (maior), largura proporcional
                target_height = 20*mm
                target_width = target_height * aspect_ratio
            
            logo = Image(LOGO_PATH, width=target_width, height=target_height)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 5*mm))
        except ImportError:
            # PIL não disponível, usar dimensões fixas conservadoras
            logo = Image(LOGO_PATH, width=65*mm, height=20*mm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 5*mm))
        except Exception:
            pass
    
    # Título
    elements.append(Paragraph(titulo, get_header_style()))
    
    # Subtítulo com obra e data
    sub_parts = []
    if nome_obra:
        sub_parts.append(nome_obra)
    if subtitulo:
        sub_parts.append(subtitulo)
    if data_geracao:
        sub_parts.append(f"Gerado em: {data_geracao}")
    
    if sub_parts:
        elements.append(Paragraph(" | ".join(sub_parts), get_subtitle_style()))
    
    # Linha divisória
    elements.append(Spacer(1, 3*mm))
    
    return elements


def format_currency_br(value) -> str:
    """Formata valor para moeda brasileira"""
    try:
        val = float(value or 0)
        return f"{val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "0,00"


def format_date_br(date_str) -> str:
    """Formata data para formato brasileiro"""
    if not date_str:
        return "-"
    try:
        from datetime import datetime
        if isinstance(date_str, datetime):
            return date_str.strftime('%d/%m/%Y')
        return str(date_str)[:10]
    except:
        return str(date_str)[:10] if date_str else "-"


def get_page_footer(canvas, doc, data_geracao: str = None):
    """Adiciona rodapé com paginação, assinatura e data em cada página"""
    from datetime import datetime
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    
    canvas.saveState()
    
    # Configurações do rodapé
    page_width = doc.pagesize[0]
    page_height = doc.pagesize[1]
    footer_y = 10*mm
    
    # Fonte
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#6B7280'))
    
    # Paginação (direita)
    page_text = f"Página {doc.page}"
    canvas.drawRightString(page_width - 15*mm, footer_y, page_text)
    
    # Desenvolvedor (centro)
    dev_text = "Desenvolvido por Vinicius Dev"
    canvas.drawCentredString(page_width / 2, footer_y, dev_text)
    
    # Data e hora (esquerda)
    if data_geracao:
        date_text = f"Gerado em: {data_geracao}"
    else:
        date_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    canvas.drawString(15*mm, footer_y, date_text)
    
    # Linha separadora do rodapé
    canvas.setStrokeColor(colors.HexColor('#E2E8F0'))
    canvas.setLineWidth(0.5)
    canvas.line(15*mm, footer_y + 5*mm, page_width - 15*mm, footer_y + 5*mm)
    
    canvas.restoreState()


def make_footer_callback(data_geracao: str = None):
    """Retorna função callback para rodapé com data específica"""
    from datetime import datetime
    if not data_geracao:
        data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    def footer_callback(canvas, doc):
        get_page_footer(canvas, doc, data_geracao)
    
    return footer_callback

