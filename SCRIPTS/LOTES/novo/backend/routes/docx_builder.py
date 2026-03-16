import os
from io import BytesIO
from datetime import datetime
from docx import Document
from docx.shared import Pt, Cm, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_margins(cell, top=0, bottom=0, start=0, end=0):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    margins = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', start), ('right', end)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        margins.append(node)
    tcPr.append(margins)

def gerar_docx_termo_quitacao(dados, empresa, form_data, lote, dt_receb=None, val_pago=None, vl_confirm=None, vl_menor=None, p=None, TIPO_PARCELA_MAP=None):
    # This is a customized DOCX generator to ensure perfect Word layout
    from routes.quitacao import format_currency, normalize_city_name

    doc = Document()
    
    # Set page layout to match ReportLab A4
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.left_margin = Mm(20)
    section.right_margin = Mm(15)
    section.top_margin = Mm(25)
    section.bottom_margin = Mm(15)
    
    # Configure Header / Footer
    header = section.header
    header.is_linked_to_previous = False
    
    # Add Logo setup here if needed (skipping image embed to keep it simple, or we can add it)
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logoazulvalle.png')
    if os.path.exists(logo_path):
        header_para = header.paragraphs[0]
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = header_para.add_run()
        run.add_picture(logo_path, width=Cm(7))
        
    # Footer
    footer = section.footer
    footer.is_linked_to_previous = False
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_footer = footer_para.add_run("www.valleprime.com.br")
    run_footer.font.size = Pt(9)
    run_footer.font.color.rgb = RGBColor(107, 114, 128)
    
    # Page Numbers in Word are complex XML, we will use a simple text or right aligned in the footer
    run_footer.add_text(" " * 60) # Spacer
    run_page = footer_para.add_run("Pag: 1") # In Word, this should ideally be dynamic but for 1-2 pages static is often okay if we don't inject fields.
    run_page.font.size = Pt(10)
    run_page.font.color.rgb = RGBColor(0, 0, 0)

    # TITULO
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("TERMO DE QUITAÇÃO")
    r_title.bold = True
    r_title.font.size = Pt(24)
    r_title.font.name = 'Helvetica'
    
    # Subtitulo
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("DE LOTE/TERRENO")
    r_sub.bold = True
    r_sub.font.size = Pt(20)
    r_sub.font.name = 'Helvetica'
    p_sub.paragraph_format.space_after = Pt(20)
    
    # Vendedora
    emp = dados['empresa']
    p_vend = doc.add_paragraph()
    r_vend_label = p_vend.add_run("VENDEDORA: ")
    r_vend_label.bold = True
    r_vend_label.font.name = 'Helvetica'
    r_vend_label.font.size = Pt(10)
    
    r_vend_val = p_vend.add_run(f"{emp['razao_social']}, pessoa jurídica de direito privado, CNPJ {emp['cnpj']}, com sede à {emp['endereco']}, Número {emp['numero']}, Bairro {emp['bairro']}, CEP {emp.get('cep', '')} Município de {emp['cidade']} - {emp['uf']}.")
    r_vend_val.font.name = 'Helvetica'
    r_vend_val.font.size = Pt(10)
    
    # Comprador
    cli = dados['cliente']
    p_comp = doc.add_paragraph()
    r_comp_label = p_comp.add_run("COMPRADOR: ")
    r_comp_label.bold = True
    r_comp_label.font.name = 'Helvetica'
    r_comp_label.font.size = Pt(10)
    
    rg_str = f", RG nº {cli.get('rg', '')} {cli.get('orgaoExpedidor', '')}" if cli.get('rg') else ""
    r_comp_val = p_comp.add_run(f"{cli['nome']}, CPF/CNPJ nº {cli['cpfCnpj']}{rg_str}, residente e domiciliado à {cli.get('endereco', '')}, Número {cli.get('numero', '')}, Bairro {cli.get('bairro', '')}, CEP {cli.get('cep', '')}, Município de {cli.get('cidade', '')} - {cli.get('uf', '')}.")
    r_comp_val.font.name = 'Helvetica'
    r_comp_val.font.size = Pt(10)
    p_comp.paragraph_format.space_after = Pt(20)
    
    # Tabela Lote
    table = doc.add_table(rows=2, cols=4)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    headers = ["LOTE/TERRENO", "QUADRA", "ÁREA TOTAL", "SITUAÇÃO"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        set_cell_margins(cell, top=100, bottom=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.name = 'Helvetica'
        
    vals = [str(lote.get('lote', '')), str(lote.get('quadra', '')), f"{lote.get('area', '')} m²", "QUITADO"]
    for i, v in enumerate(vals):
        cell = table.cell(1, i)
        set_cell_margins(cell, top=100, bottom=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(v)
        r.font.size = Pt(10)
        r.font.name = 'Helvetica'
        
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    
    # Autorizacao
    p_aut_tit = doc.add_paragraph()
    r_aut_tit = p_aut_tit.add_run("DA AUTORIZAÇÃO PARA ESCRITURA")
    r_aut_tit.bold = True
    r_aut_tit.font.name = 'Helvetica'
    r_aut_tit.font.size = Pt(10)
    
    p_aut = doc.add_paragraph()
    p_aut.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_aut = p_aut.add_run(f"A VENDEDORA DECLARA QUE TODAS AS OBRIGAÇÕES CONTRATUAIS DO COMPRADOR ESTÃO QUITADAS E, POR ISSO, AUTORIZA O CARTÓRIO DE REGISTRO DE IMÓVEIS DA COMARCA DE {lote.get('cidadeObra', '').upper()} - {lote.get('ufObra', '').upper()}, A LAVRAR ESCRITURA PÚBLICA DE COMPRA E VENDA DO IMÓVEL IDENTIFICADO NO PREÂMBULO EM FAVOR DO COMPRADOR ACIMA QUALIFICADO.")
    r_aut.font.name = 'Helvetica'
    r_aut.font.size = Pt(10)
    
    # Preco
    p_pr_tit = doc.add_paragraph()
    r_pr_tit = p_pr_tit.add_run("DO PREÇO")
    r_pr_tit.bold = True
    r_pr_tit.font.name = 'Helvetica'
    r_pr_tit.font.size = Pt(10)
    
    p_pr = doc.add_paragraph()
    p_pr.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    ultimo_receb_raw = dados['venda'].get('ultimoRecebimento')
    ultimo_receb_str = '-'
    if ultimo_receb_raw:
        try:
            if hasattr(ultimo_receb_raw, 'strftime'):
                 ultimo_receb_str = ultimo_receb_raw.strftime('%d/%m/%Y')
            else:
                dt = datetime.fromisoformat(str(ultimo_receb_raw).replace('Z', ''))
                ultimo_receb_str = dt.strftime('%d/%m/%Y')
        except:
             ultimo_receb_str = str(ultimo_receb_raw)[:10]

    r_pr = p_pr.add_run(f"O VALOR DO LOTE/TERRENO É DE ")
    r_pr.font.name = 'Helvetica'
    r_pr.font.size = Pt(10)
    r_pr_val = p_pr.add_run(f"{format_currency(dados['venda']['valor'])}")
    r_pr_val.bold = True
    r_pr_val.font.name = 'Helvetica'
    r_pr_val.font.size = Pt(10)
    r_pr2 = p_pr.add_run(f", QUE JÁ FOI QUITADO PERANTE A VENDEDORA EM ")
    r_pr2.font.name = 'Helvetica'
    r_pr2.font.size = Pt(10)
    r_pr_dt = p_pr.add_run(f"{ultimo_receb_str}.")
    r_pr_dt.bold = True
    r_pr_dt.font.name = 'Helvetica'
    r_pr_dt.font.size = Pt(10)
    
    # Validade
    p_val_tit = doc.add_paragraph()
    r_val_tit = p_val_tit.add_run("DA VALIDADE")
    r_val_tit.bold = True
    r_val_tit.font.name = 'Helvetica'
    r_val_tit.font.size = Pt(10)
    
    p_val = doc.add_paragraph()
    p_val.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_val = p_val.add_run("A PRESENTE AUTORIZAÇÃO TERÁ VALIDADE DE 120 (CENTO E VINTE) DIAS, A CONTAR DA DATA DE SUA EMISSÃO.\n\nPOR SER EXPRESSÃO DA VERDADE, FIRMAMOS A PRESENTE EM 03 (TRÊS) VIAS DE IGUAL TEOR E FORMA.")
    r_val.font.name = 'Helvetica'
    r_val.font.size = Pt(10)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(20)
    
    # Data Local
    data_para_usar = form_data.get('data')
    if data_para_usar:
        try:
            data_para_usar = datetime.strptime(data_para_usar, '%Y-%m-%d')
        except:
            data_para_usar = datetime.now()
    else:
        data_para_usar = datetime.now()
        
    meses_upper = {
        1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL', 5: 'MAIO', 6: 'JUNHO',
        7: 'JULHO', 8: 'AGOSTO', 9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
    }
    mes_nome = meses_upper.get(data_para_usar.month, '')
    local_nome = normalize_city_name(lote.get('cidadeObra'), lote.get('cep'))
    local_data = f"{local_nome} - {lote.get('ufObra', 'PA').upper()}, {data_para_usar.day} DE {mes_nome} DE {data_para_usar.year}."
    
    p_data = doc.add_paragraph()
    p_data.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_data = p_data.add_run(local_data)
    r_data.font.name = 'Helvetica'
    r_data.font.size = Pt(10)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(40)
    
    # Assinaturas
    p_ass1 = doc.add_paragraph()
    p_ass1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ass1.add_run("__________________________________________________________________\n").bold = True
    r_ass1 = p_ass1.add_run(f"{emp['razao_social'].upper()}")
    r_ass1.bold = True
    r_ass1.font.name = 'Helvetica'
    r_ass1.font.size = Pt(10)
    
    p_ass1.paragraph_format.space_after = Pt(40)
    
    p_ass2 = doc.add_paragraph()
    p_ass2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    len_line = max(43, int(len(cli['nome']) * 1.3))
    line_str = "_" * len_line
    p_ass2.add_run(line_str + "\n").bold = True
    r_ass2 = p_ass2.add_run(f"{cli['nome'].upper()}")
    r_ass2.bold = True
    r_ass2.font.name = 'Helvetica'
    r_ass2.font.size = Pt(10)
    
    p_ass2.paragraph_format.space_after = Pt(40)
    
    # Testemunhas
    p_test = doc.add_paragraph()
    r_test = p_test.add_run("TESTEMUNHAS:")
    r_test.bold = True
    r_test.font.name = 'Helvetica'
    r_test.font.size = Pt(10)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(40)
    
    # Tabela Testemunhas
    ttable = doc.add_table(rows=3, cols=3)
    ttable.autofit = False
    
    # Larguras
    for row in ttable.rows:
        row.cells[0].width = Cm(7)
        row.cells[1].width = Cm(3) # Espaço
        row.cells[2].width = Cm(7)
        
    tdata = [
        ["_____________________________", "", "_____________________________"],
        ["NOME:", "", "NOME:"],
        ["CPF:", "", "CPF:"]
    ]
    
    for i, row in enumerate(tdata):
        for j, val in enumerate(row):
            p = ttable.cell(i, j).paragraphs[0]
            r = p.add_run(val)
            r.font.name = 'Helvetica'
            r.font.size = Pt(10)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
