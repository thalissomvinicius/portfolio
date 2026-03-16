"""
Prime Imóveis Dashboard - Disponibilidades Routes
Lista de lotes do empreendimento com dados para simulação de financiamento
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from database import execute_query
from typing import Optional
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os

router = APIRouter()

# Status dos lotes (Vendido_unid)
STATUS_LABELS = {
    0: "Disponível",
    1: "Vendido",
    2: "Reservado",
    3: "Proposta",
    4: "Quitado",
    5: "Escriturado",
    6: "Em Venda",
    7: "Suspenso",
    8: "Fora de Venda",
    9: "Em Acerto",
    10: "Dação"
}


@router.get("/disponibilidades")
async def get_disponibilidades(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    status: Optional[int] = Query(None, description="Filtrar por status (0=Disponível, 1=Vendido, etc)")
):
    """Lista todos os lotes do empreendimento com dados básicos e cliente (se houver)"""
    
    # Filtro de status
    status_filter = f"AND UnidadePer.Vendido_unid = {status}" if status is not None else ""
    
    # Query baseada no loteamento.py para obter valores corretos
    query = f"""
    SELECT 
        UnidadePer.Identificador_Unid as identificador,
        ISNULL(UnidadePer.C1_unid, '') as quadra,
        ISNULL(UnidadePer.C2_unid, '') as lote,
        UnidadePer.Vendido_unid as status,
        ISNULL(UnidadePer.Qtde_Unid, 0) as area,
        ISNULL(UnidadePer.C3_unid, '') as area_texto,
        ISNULL(UnidadePer.C4_unid, '') as logradouro,
        ISNULL(UnidadePer.C5_unid, '') as m_frente,
        ISNULL(UnidadePer.C7_unid, '') as m_fundo,
        ISNULL(UnidadePer.C9_unid, '') as lado_direito,
        ISNULL(UnidadePer.C11_unid, '') as lado_esquerdo,
        ISNULL(UnidadePer.C12_unid, '') as chanfro,
        CASE 
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
        END * (ISNULL(UnidadePer.PorcentPr_Unid, 100) / 100.0) * ISNULL(UnidadePer.Qtde_Unid, 1) as valor,
        COALESCE(VendasAtivas.Num_Ven, VendaFallback.NumVend_prc) as numVenda,
        UPPER(COALESCE(Pessoas.Nome_Pes, PessoaFallback.Nome_Pes)) as cliente,
        COALESCE(Pessoas.cod_pes, PessoaFallback.cod_pes) as codCliente
    FROM UnidadePer WITH(NOLOCK)
    LEFT JOIN UnidadeDetalhe ud WITH(NOLOCK)
        ON UnidadePer.Empresa_Unid = ud.Empresa_Udt
        AND UnidadePer.Prod_Unid = ud.Prod_Udt
        AND UnidadePer.NumPer_Unid = ud.NumPer_Udt
    LEFT JOIN (
        SELECT DISTINCT
            ItensVenda.Empresa_itv,
            ItensVenda.Obra_Itv,
            ItensVenda.Produto_Itv,
            ItensVenda.CodPerson_Itv,
            Vendas.Num_Ven,
            Vendas.Cliente_Ven
        FROM ItensVenda WITH(NOLOCK)
        INNER JOIN Vendas WITH(NOLOCK) 
            ON ItensVenda.Empresa_itv = Vendas.Empresa_Ven 
            AND ItensVenda.NumVend_Itv = Vendas.Num_Ven
    ) VendasAtivas 
        ON UnidadePer.Empresa_unid = VendasAtivas.Empresa_itv
        AND UnidadePer.Obra_unid = VendasAtivas.Obra_Itv
        AND UnidadePer.Prod_unid = VendasAtivas.Produto_Itv
        AND UnidadePer.NumPer_unid = VendasAtivas.CodPerson_Itv
    LEFT JOIN Pessoas WITH(NOLOCK) 
        ON VendasAtivas.Cliente_Ven = Pessoas.cod_pes
    -- Fallback para lotes quitados (que não têm ItensVenda correspondente)
    OUTER APPLY (
        SELECT TOP 1 CR.NumVend_prc, CR.Cliente_Prc
        FROM ContasReceber CR WITH(NOLOCK)
        INNER JOIN ItensVenda IV WITH(NOLOCK) ON CR.Empresa_prc = IV.Empresa_itv AND CR.NumVend_prc = IV.NumVend_Itv
        WHERE CR.Empresa_prc = UnidadePer.Empresa_unid
          AND CR.Obra_Prc = UnidadePer.Obra_unid
          AND IV.Produto_Itv = UnidadePer.Prod_unid
          AND IV.CodPerson_Itv = UnidadePer.NumPer_unid
          AND CR.Tipo_Prc = 'S'
          AND VendasAtivas.Num_Ven IS NULL
        ORDER BY CR.NumVend_prc DESC
    ) VendaFallback
    LEFT JOIN Pessoas PessoaFallback WITH(NOLOCK) 
        ON VendaFallback.Cliente_Prc = PessoaFallback.cod_pes
    WHERE UnidadePer.Empresa_unid = {empresa} 
      AND UnidadePer.Obra_unid = '{obra}'
      {status_filter}
    ORDER BY UnidadePer.C1_unid, UnidadePer.C2_unid
    """
    
    try:
        result = execute_query(query)
        
        lotes = []
        resumo = {
            "total": 0,
            "disponivel": 0,
            "vendido": 0,
            "reservado": 0,
            "quitado": 0,
            "suspenso": 0,
            "foraVenda": 0,
            "valorDisponivel": 0,
            "valorVendido": 0,
            "valorTotal": 0
        }
        
        for row in result:
            status_code = row.get('status', 0) or 0
            valor = float(row.get('valor', 0) or 0)
            
            lote = {
                "identificador": row.get('identificador', ''),
                "quadra": str(row.get('quadra', '')).strip(),
                "lote": str(row.get('lote', '')).strip(),
                "status": status_code,
                "statusLabel": STATUS_LABELS.get(status_code, "Desconhecido"),
                "area": float(row.get('area', 0) or 0),
                "valor": valor,
                "numVenda": row.get('numVenda'),
                "cliente": row.get('cliente'),
                "codCliente": row.get('codCliente')
            }
            lotes.append(lote)
            
            # Contadores para resumo
            resumo["total"] += 1
            resumo["valorTotal"] += valor
            
            if status_code == 0:
                resumo["disponivel"] += 1
                resumo["valorDisponivel"] += valor
            elif status_code == 1:
                resumo["vendido"] += 1
                resumo["valorVendido"] += valor
            elif status_code == 2:
                resumo["reservado"] += 1
            elif status_code == 4:
                resumo["quitado"] += 1
            elif status_code == 7:
                resumo["suspenso"] += 1
            elif status_code == 8:
                resumo["foraVenda"] += 1
        
        return {
            "lotes": lotes,
            "resumo": resumo
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar disponibilidades: {str(e)}")


@router.get("/disponibilidades/simulacao")
async def simular_financiamento(
    valor_lote: float = Query(..., description="Valor do lote"),
    parcelas_sinal: int = Query(1, description="Quantidade de parcelas do sinal", ge=1, le=24),
    parcelas_mensais: int = Query(36, description="Quantidade de parcelas mensais", ge=2, le=200),
    entrada: float = Query(0, description="Valor de entrada adicional (além do sinal)")
):
    """Simula financiamento do lote com as regras Prime Imóveis"""
    
    # Validações
    if valor_lote <= 0:
        raise HTTPException(status_code=400, detail="Valor do lote deve ser maior que zero")
    
    # Cálculos
    sinal = valor_lote * 0.05  # 5% de sinal
    sinal_por_parcela = sinal / parcelas_sinal
    
    saldo_restante = valor_lote - sinal - entrada  # 95% - entrada
    
    if saldo_restante < 0:
        saldo_restante = 0
    
    parcela_mensal = saldo_restante / parcelas_mensais if parcelas_mensais > 0 else 0
    
    # Determinar tipo do plano
    if parcelas_mensais <= 36:
        plano = "Parcelas Fixas"
        plano_descricao = "Sem correção monetária"
    elif parcelas_mensais <= 72:
        plano = "Parcelas Corrigidas"
        plano_descricao = "Correção anual pelo IPCA"
    else:
        plano = "Parcelas Corrigidas"
        plano_descricao = "Correção anual pelo IPCA"
    
    # À vista (20% desconto sobre o saldo)
    desconto_avista = saldo_restante * 0.20
    valor_avista = sinal + entrada + (saldo_restante - desconto_avista)
    
    return {
        "valorLote": valor_lote,
        "sinal": {
            "valor": sinal,
            "percentual": 5,
            "parcelas": parcelas_sinal,
            "valorParcela": sinal_por_parcela
        },
        "entrada": entrada,
        "saldoFinanciar": saldo_restante,
        "parcelamento": {
            "parcelas": parcelas_mensais,
            "valorParcela": parcela_mensal,
            "plano": plano,
            "descricao": plano_descricao
        },
        "avista": {
            "desconto": desconto_avista,
            "percentualDesconto": 20,
            "valorFinal": valor_avista
        },
        "totalFinanciado": sinal + entrada + saldo_restante
    }


@router.get("/disponibilidades/pdf")
async def export_disponibilidades_pdf(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    status: Optional[int] = Query(None, description="Filtrar por status"),
    usuario: str = Query("", description="Nome do usuário")
):
    """Gera PDF com lista de lotes filtrados - Modelo Valle (Paisagem)"""
    
    # Buscar dados com todos os campos necessários
    status_filter = f"AND UnidadePer.Vendido_unid = {status}" if status is not None else ""
    
    query = f"""
    SELECT 
        UnidadePer.Identificador_Unid as identificador,
        ISNULL(UnidadePer.C1_unid, '') as quadra,
        ISNULL(UnidadePer.C2_unid, '') as lote,
        UnidadePer.Vendido_unid as status,
        ISNULL(UnidadePer.Qtde_Unid, 0) as area,
        ISNULL(UnidadePer.C3_unid, '') as area_texto,
        ISNULL(UnidadePer.C4_unid, '') as logradouro,
        ISNULL(UnidadePer.C5_unid, '') as m_frente,
        ISNULL(UnidadePer.C7_unid, '') as m_fundo,
        ISNULL(UnidadePer.C9_unid, '') as lado_direito,
        ISNULL(UnidadePer.C11_unid, '') as lado_esquerdo,
        ISNULL(UnidadePer.C12_unid, '') as chanfro,
        UnidadePer.Prod_unid as prod,
        CASE 
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
        END * (ISNULL(UnidadePer.PorcentPr_Unid, 100) / 100.0) * ISNULL(UnidadePer.Qtde_Unid, 1) as valor
    FROM UnidadePer WITH(NOLOCK)
    LEFT JOIN UnidadeDetalhe ud WITH(NOLOCK)
        ON UnidadePer.Empresa_Unid = ud.Empresa_Udt
        AND UnidadePer.Prod_Unid = ud.Prod_Udt
        AND UnidadePer.NumPer_Unid = ud.NumPer_Udt
    WHERE UnidadePer.Empresa_unid = {empresa} AND UnidadePer.Obra_unid = '{obra}' {status_filter}
    ORDER BY UnidadePer.C1_unid, UnidadePer.C2_unid
    """
    
    try:
        result = execute_query(query)
        
        # Buscar nome da obra e código do produto
        obra_query = f"SELECT Descr_Obr, Cod_Obr FROM Obras WITH(NOLOCK) WHERE Empresa_Obr = {empresa} AND Cod_Obr = '{obra}'"
        obra_result = execute_query(obra_query)
        nome_obra = obra_result[0].get('Descr_Obr', '') if obra_result else ''
        cod_obra = obra_result[0].get('Cod_Obr', obra) if obra_result else obra
        
        # Pegar código do produto do primeiro lote
        cod_prod = result[0].get('prod', '') if result else ''
        
        # Imports
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import Paragraph, Image, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
        
        # Orientação PAISAGEM (landscape)
        PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)
        
        # Cores do tema Valle - exatas do modelo
        AZUL_VALLE = colors.HexColor('#003366')  # Azul escuro Valle
        AZUL_CLARO = colors.HexColor('#DCE6F2')  # Azul claro para zebra (mais próximo do modelo)
        BRANCO = colors.white
        PRETO = colors.black
        CINZA = colors.HexColor('#666666')
        CINZA_BORDA = colors.HexColor('#999999')
        
        # Função para formatar moeda
        def format_currency_valle(value):
            try:
                return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                return "0,00"
        
        # Logo path - usar logo da pasta assets
        def get_logo_path():
            routes_dir = os.path.dirname(__file__)
            backend_dir = os.path.dirname(routes_dir)
            # Tentar logo da Valle primeiro, depois Prime
            logo_path = os.path.join(backend_dir, 'assets', 'logovalle.png')
            if os.path.exists(logo_path):
                return logo_path
            logo_path = os.path.join(backend_dir, 'assets', 'logoprime.png')
            return logo_path if os.path.exists(logo_path) else None
        
        # Criar PDF com paginação customizada
        buffer = BytesIO()
        
        # Contador de páginas para X/Y
        class PageCounter:
            def __init__(self):
                self.pages = []
        
        page_counter = PageCounter()
        
        # Classe para gerenciar paginação
        class ValleDocTemplate(BaseDocTemplate):
            def __init__(self, filename, **kwargs):
                self.nome_obra = kwargs.pop('nome_obra', '')
                self.cod_prod = kwargs.pop('cod_prod', '')
                self.usuario = kwargs.pop('usuario', '')
                self.logo_path = kwargs.pop('logo_path', None)
                self.page_counter = kwargs.pop('page_counter', None)
                BaseDocTemplate.__init__(self, filename, **kwargs)
                
                # Frame principal para paisagem
                frame = Frame(
                    self.leftMargin, self.bottomMargin + 10*mm,
                    self.width, self.height - 25*mm,
                    id='normal'
                )
                template = PageTemplate(id='valle', frames=[frame], onPage=self.add_header_footer)
                self.addPageTemplates([template])
            
            def afterPage(self):
                """Chamado após cada página - usado para contar páginas"""
                if self.page_counter:
                    self.page_counter.pages.append(self.page)
            
            def add_header_footer(self, canvas, doc):
                canvas.saveState()
                
                width, height = PAGE_WIDTH, PAGE_HEIGHT
                
                # === HEADER ===
                # Logo à esquerda
                if self.logo_path and os.path.exists(self.logo_path):
                    try:
                        canvas.drawImage(self.logo_path, 12*mm, height - 18*mm, width=22*mm, height=12*mm, preserveAspectRatio=True, mask='auto')
                    except:
                        canvas.setFont('Helvetica-Bold', 12)
                        canvas.setFillColor(AZUL_VALLE)
                        canvas.drawString(12*mm, height - 14*mm, "VALLE")
                else:
                    canvas.setFont('Helvetica-Bold', 12)
                    canvas.setFillColor(AZUL_VALLE)
                    canvas.drawString(12*mm, height - 14*mm, "VALLE")
                
                # Título centralizado
                canvas.setFont('Helvetica-Bold', 14)
                canvas.setFillColor(PRETO)
                canvas.drawCentredString(width/2, height - 12*mm, "Relatório de Disponibilidade")
                
                # Subtítulo - Loteamento
                canvas.setFont('Helvetica', 9)
                canvas.setFillColor(CINZA)
                loteamento_text = f"Loteamento:({self.cod_prod}) {self.nome_obra.upper()}"
                canvas.drawCentredString(width/2, height - 18*mm, loteamento_text)
                
                # Usuário à direita
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(CINZA)
                canvas.drawRightString(width - 12*mm, height - 10*mm, f"Usuário: {self.usuario}")
                
                # Linha divisória azul abaixo do header
                canvas.setStrokeColor(AZUL_VALLE)
                canvas.setLineWidth(1.5)
                canvas.line(8*mm, height - 22*mm, width - 8*mm, height - 22*mm)
                
                # === FOOTER ===
                # "Viva Bem, Viva Valle..." à esquerda
                canvas.setFont('Helvetica-Oblique', 8)
                canvas.setFillColor(CINZA)
                canvas.drawString(12*mm, 8*mm, "Viva Bem, Viva Valle...")
                
                # Página centralizada - será atualizada no afterFlowable
                canvas.setFont('Helvetica', 8)
                # Placeholder - será substituído
                canvas.drawCentredString(width/2, 8*mm, f"{doc.page}/--")
                
                # Data de emissão à direita
                canvas.drawRightString(width - 12*mm, 8*mm, f"Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                
                canvas.restoreState()
        
        # Primeiro pass: contar páginas
        temp_buffer = BytesIO()
        temp_doc = ValleDocTemplate(
            temp_buffer,
            pagesize=landscape(A4),
            leftMargin=8*mm,
            rightMargin=8*mm,
            topMargin=22*mm,
            bottomMargin=15*mm,
            nome_obra=nome_obra,
            cod_prod=str(cod_prod),
            usuario=usuario,
            logo_path=get_logo_path(),
            page_counter=page_counter
        )
        
        # Construir dados da tabela
        table_data = [['QD', 'LT', 'Área M²', 'Valor do Lote', 'Logradouro', 'M Frente', 'M Fundo', 'Lado Direito', 'Lado Esquerdo', 'Chanfro', 'Status Lote']]
        
        for row in result:
            status_code = row.get('status', 0) or 0
            valor = float(row.get('valor', 0) or 0)
            
            # Usar área texto se disponível, senão usar área numérica
            area_val = row.get('area_texto', '') or ''
            if not area_val:
                area_num = float(row.get('area', 0) or 0)
                area_val = f"{area_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if area_num else ''
            
            table_data.append([
                str(row.get('quadra', '')).strip(),
                str(row.get('lote', '')).strip(),
                str(area_val).strip(),
                format_currency_valle(valor),
                str(row.get('logradouro', '') or '').strip(),
                str(row.get('m_frente', '') or '').strip(),
                str(row.get('m_fundo', '') or '').strip(),
                str(row.get('lado_direito', '') or '').strip(),
                str(row.get('lado_esquerdo', '') or '').strip(),
                str(row.get('chanfro', '') or '-/-').strip() if row.get('chanfro') else '-/-',
                STATUS_LABELS.get(status_code, 'Disponível')
            ])
        
        # Larguras de colunas ajustadas para paisagem (total ~265mm disponível)
        col_widths = [15*mm, 15*mm, 22*mm, 28*mm, 45*mm, 20*mm, 20*mm, 28*mm, 28*mm, 18*mm, 26*mm]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Estilo da tabela - modelo Valle exato
        table_style = [
            # Header - fundo azul escuro
            ('BACKGROUND', (0, 0), (-1, 0), AZUL_VALLE),
            ('TEXTCOLOR', (0, 0), (-1, 0), BRANCO),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # QD, LT centralizados
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),   # Área à direita
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Valor à direita
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),    # Logradouro à esquerda
            ('ALIGN', (5, 1), (9, -1), 'CENTER'),  # Medidas centralizadas
            ('ALIGN', (10, 1), (10, -1), 'LEFT'),  # Status à esquerda
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            
            # Bordas cinza claro
            ('GRID', (0, 0), (-1, -1), 0.5, CINZA_BORDA),
        ]
        
        # Zebra striping - linhas alternadas em azul claro
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), AZUL_CLARO))
        
        table.setStyle(TableStyle(table_style))
        
        # Build primeiro pass para contar páginas
        elements = [table]
        temp_doc.build(elements)
        total_pages = len(page_counter.pages) if page_counter.pages else 1
        
        # Segundo pass: gerar PDF final com número de páginas correto
        class ValleDocTemplateFinal(BaseDocTemplate):
            def __init__(self, filename, **kwargs):
                self.nome_obra = kwargs.pop('nome_obra', '')
                self.cod_prod = kwargs.pop('cod_prod', '')
                self.usuario = kwargs.pop('usuario', '')
                self.logo_path = kwargs.pop('logo_path', None)
                self.total_pages = kwargs.pop('total_pages', 1)
                BaseDocTemplate.__init__(self, filename, **kwargs)
                
                frame = Frame(
                    self.leftMargin, self.bottomMargin + 10*mm,
                    self.width, self.height - 25*mm,
                    id='normal'
                )
                template = PageTemplate(id='valle', frames=[frame], onPage=self.add_header_footer)
                self.addPageTemplates([template])
            
            def add_header_footer(self, canvas, doc):
                canvas.saveState()
                
                width, height = PAGE_WIDTH, PAGE_HEIGHT
                
                # === HEADER ===
                if self.logo_path and os.path.exists(self.logo_path):
                    try:
                        canvas.drawImage(self.logo_path, 12*mm, height - 18*mm, width=22*mm, height=12*mm, preserveAspectRatio=True, mask='auto')
                    except:
                        canvas.setFont('Helvetica-Bold', 12)
                        canvas.setFillColor(AZUL_VALLE)
                        canvas.drawString(12*mm, height - 14*mm, "VALLE")
                else:
                    canvas.setFont('Helvetica-Bold', 12)
                    canvas.setFillColor(AZUL_VALLE)
                    canvas.drawString(12*mm, height - 14*mm, "VALLE")
                
                canvas.setFont('Helvetica-Bold', 14)
                canvas.setFillColor(PRETO)
                canvas.drawCentredString(width/2, height - 12*mm, "Relatório de Disponibilidade")
                
                canvas.setFont('Helvetica', 9)
                canvas.setFillColor(CINZA)
                loteamento_text = f"Loteamento:({self.cod_prod}) {self.nome_obra.upper()}"
                canvas.drawCentredString(width/2, height - 18*mm, loteamento_text)
                
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(CINZA)
                canvas.drawRightString(width - 12*mm, height - 10*mm, f"Usuário: {self.usuario}")
                
                # Linha divisória azul abaixo do header
                canvas.setStrokeColor(AZUL_VALLE)
                canvas.setLineWidth(1.5)
                canvas.line(8*mm, height - 22*mm, width - 8*mm, height - 22*mm)
                
                # === FOOTER ===
                canvas.setFont('Helvetica-Oblique', 8)
                canvas.setFillColor(CINZA)
                canvas.drawString(12*mm, 8*mm, "Viva Bem, Viva Valle...")
                
                # Página X/Y
                canvas.setFont('Helvetica', 8)
                canvas.drawCentredString(width/2, 8*mm, f"{doc.page}/{self.total_pages}")
                
                canvas.drawRightString(width - 12*mm, 8*mm, f"Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                
                canvas.restoreState()
        
        # Criar documento final
        doc = ValleDocTemplateFinal(
            buffer,
            pagesize=landscape(A4),
            leftMargin=8*mm,
            rightMargin=8*mm,
            topMargin=22*mm,
            bottomMargin=15*mm,
            nome_obra=nome_obra,
            cod_prod=str(cod_prod),
            usuario=usuario,
            logo_path=get_logo_path(),
            total_pages=total_pages
        )
        
        # Recriar tabela para segundo pass
        table2 = Table(table_data, colWidths=col_widths, repeatRows=1)
        table2.setStyle(TableStyle(table_style))
        
        doc.build([table2])
        buffer.seek(0)
        
        filename = f"disponibilidades_{obra}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename={filename}"})
        
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}\n{traceback.format_exc()}")


