"""
Quitação Routes - Endpoints para geração de documentos de quitação
Carta de Quitação e Termo de Quitação para lotes quitados
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from database import execute_query
from typing import Optional
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

router = APIRouter()

# Configuração da representante legal (fixa conforme solicitado)
REPRESENTANTE_LEGAL = {
    "nome": "RAIMUNDA DAS GRAÇAS P. MARQUES",
    "estado_civil": "Casada",
    "cargo": "Gerente Administrativa",
    "rg": "2148954",
    "cpf": "352.369.222-91",
    "domicilio": "Tomé-Açu-PA"
}

# Mapeamento de tipos de parcelas
TIPO_PARCELA_MAP = {
    "0": "Seguro",
    "1": "Custas",
    "2": "Acerto final",
    "A": "Resíduo Agrupado",
    "B": "Balão",
    "C": "Chave",
    "E": "Entrada",
    "ER": "Entrada Renegociada",
    "I": "Intermediação",
    "IN": "Intermediárias",
    "P": "Parcela",
    "R": "Resíduo",
    "S": "Comissão Corretagem",
    "T": "Taxa",
    "M": "Multa",
    "J": "Juros"
}

def build_logo_flowable(max_width_mm: float = 60):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    svg_path = os.path.join(base_dir, 'assets', 'logoazulvalle.svg')
    png_path = os.path.join(base_dir, 'assets', 'logoazulvalle.png')
    max_width = max_width_mm * mm
    if os.path.exists(png_path):
        try:
            from reportlab.lib.utils import ImageReader
            ir = ImageReader(png_path)
            iw, ih = ir.getSize()
            aspect = ih / float(iw) if iw else 1
            lw = max_width
            lh = lw * aspect
            logo = Image(png_path, width=lw, height=lh)
            logo.hAlign = 'CENTER'
            return logo
        except:
            pass
    if os.path.exists(svg_path):
        try:
            from svglib.svglib import svg2rlg
            drawing = svg2rlg(svg_path)
            if drawing:
                if drawing.width:
                    scale = max_width / float(drawing.width)
                    drawing.scale(scale, scale)
                    drawing.width = drawing.width * scale
                    drawing.height = drawing.height * scale
                drawing.hAlign = 'CENTER'
                return drawing
        except:
            pass
    return None


def get_empresa_dados(empresa: int) -> dict:
    """Busca dados da empresa do banco de dados"""
    query = f"""
    SELECT 
        Codigo_emp,
        Desc_emp,
        CGC_emp,
        Endereco_emp,
        NumEnd_emp,
        Setor_emp,
        Cidade_emp,
        UF_emp,
        CEP_emp
    FROM Empresas WITH(NOLOCK)
    WHERE Codigo_emp = {empresa}
    """
    try:
        result = execute_query(query)
        if result:
            emp = result[0]
            # Formatar endereço
            endereco = emp.get('Endereco_emp', '') or ''
            num_end = emp.get('NumEnd_emp', '') or ''
            if num_end:
                endereco = f"{endereco}, {num_end}"
            
            return {
                "razao_social": emp.get('Desc_emp', '') or 'NÃO INFORMADA',
                "cnpj": format_cpf_cnpj(emp.get('CGC_emp', '')),
                "endereco": endereco,
                "bairro": emp.get('Setor_emp', '') or '',
                "cidade": emp.get('Cidade_emp', '') or 'Tomé-Açu',
                "uf": emp.get('UF_emp', '') or 'PA',
                "cep": emp.get('CEP_emp', '') or ''
            }
    except Exception as e:
        print(f"Erro ao buscar dados da empresa: {e}")
    
    # Fallback se não encontrar
    return {
        "razao_social": "NÃO INFORMADA",
        "cnpj": "",
        "endereco": "",
        "bairro": "",
        "cidade": "Tomé-Açu",
        "uf": "PA",
        "cep": ""
    }


def format_cpf_cnpj(doc: str) -> str:
    """Formata CPF ou CNPJ"""
    if not doc:
        return ""
    doc = ''.join(filter(str.isdigit, str(doc)))
    if len(doc) == 11:
        return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
    elif len(doc) == 14:
        return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
    return doc


def format_currency(value: float) -> str:
    """Formata valor monetário"""
    try:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"


def format_date_extenso(dt: datetime) -> str:
    """Formata data por extenso"""
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
             'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    return f"{dt.day} de {meses[dt.month - 1]} de {dt.year}"

def normalize_city_name(name, cep=None):
    """Padroniza o nome da cidade solicitado pelo usuário"""
    name_upper = str(name or "-").upper().strip()
    
    # Regra do CEP: Se for os específicos de Tomé-Açu, força o nome correto
    cep_limpo = ''.join(filter(str.isdigit, str(cep or "")))
    if cep_limpo in ['68680000', '68682000']:
        return "TOMÉ-AÇU"

    # Se contiver variações de QUATRO BOCAS ou TOME ACU, padroniza
    if "QUATRO BOCAS" in name_upper or ("TOME" in name_upper and "ACU" in name_upper):
        return "TOMÉ-AÇU"
        
    return name_upper


def get_regime_casamento_label(codigo):
    """Mapeia código numérico do UAU para regime de casamento"""
    if codigo is None or codigo == "":
        return "" # Retorna vazio se não informado para não sujar o texto
    
    # Se já for uma string descritiva (ex: "0 - COMUNHÃO PARCIAL")
    if isinstance(codigo, str) and "-" in codigo:
        parts = codigo.split("-")
        return parts[-1].strip().upper()
        
    # Converter para int se for string numérica
    try:
        val = int(float(str(codigo)))
    except:
        return str(codigo).upper()

    # Mapeamento corrigido conforme evidência (0 = Comunhão Parcial)
    mapping = {
        0: "COMUNHÃO PARCIAL DE BENS",
        1: "COMUNHÃO UNIVERSAL DE BENS",
        2: "SEPARAÇÃO TOTAL DE BENS",
        3: "PARTICIPAÇÃO FINAL NOS AQUESTOS",
        4: "SEPARAÇÃO OBRIGATÓRIA DE BENS",
        5: "OUTROS",
        6: "UNIÃO ESTÁVEL"
    }
    
    return mapping.get(val, str(codigo).upper())


def get_naturalidade(cod_pes: int) -> dict:
    try:
        pf_cols = execute_query("SELECT name FROM sys.columns WHERE object_id = OBJECT_ID('PesFis')")
        pf_names = [str(c.get('name')).lower() for c in pf_cols] if pf_cols else []
        uf_candidates = ['ufnaturalidade_pf', 'ufnaturalidade', 'uf_naturalidade', 'ufnasc_pf', 'uf_nasc', 'ufnascimento']
        cidade_candidates = ['naturalid_pf', 'cidadenat_pf', 'codmunicnasc_pf', 'naturalidade_pf', 'naturalidade', 'cidnasc_pf', 'cidade_nascimento', 'cidadenascimento']
        uf_col = next((n for n in uf_candidates if n in pf_names), None)
        cidade_col = next((n for n in cidade_candidates if n in pf_names), None)
        cidade_val = None
        uf_val = None
        if uf_col or cidade_col:
            select_cols = []
            if cidade_col:
                select_cols.append(cidade_col)
            if uf_col:
                select_cols.append(uf_col)
            res = execute_query(f"SELECT {', '.join(select_cols)} FROM PesFis WITH(NOLOCK) WHERE cod_pf = {int(cod_pes)}")
            if res:
                r = res[0]
                cidade_val = r.get(cidade_col) if cidade_col else None
                uf_val = r.get(uf_col) if uf_col else None
        if (not cidade_val or str(cidade_val).strip() == '' or str(cidade_val).strip().isdigit()):
            cod_city = str(cidade_val).strip() if cidade_val is not None else None
            cidades_cols = execute_query("SELECT name FROM sys.tables WHERE name IN ('Cidades','CidadeDePara','CidadeLegislacao')")
            for trow in cidades_cols or []:
                tname = trow.get('name')
                cols = execute_query(f"SELECT name FROM sys.columns WHERE object_id = OBJECT_ID('{tname}')")
                names = [str(c.get('name')) for c in cols]
                id_cols = [c for c in names if 'cod' in c.lower() or 'id' in c.lower()]
                name_cols = [c for c in names if 'nome' in c.lower() or 'cidade' in c.lower() or 'descricao' in c.lower()]
                if not id_cols or not name_cols:
                    continue
                idc = id_cols[0]
                namec = name_cols[0]
                if cod_city and cod_city.isdigit():
                    try:
                        row = execute_query(f"SELECT TOP 1 {namec} AS nome FROM {tname} WITH(NOLOCK) WHERE TRY_CONVERT(int, {idc}) = TRY_CONVERT(int, ?)", (cod_city,))
                        if row:
                            cidade_val = row[0].get('nome')
                            break
                    except:
                        pass
        return {
            "cidadeNascimento": str(cidade_val or "").strip(),
            "ufNascimento": str(uf_val or "").strip()
        }
    except:
        pass
    return {"cidadeNascimento": None, "ufNascimento": None}


def get_clientes_venda(empresa: int, obra: str, num_venda: int) -> list:
    """
    Busca todos os clientes (co-proprietários) de uma venda com dados completos.
    Suporta VendaClientes (vendas ativas) e VendaRecClientes (vendas recebidas/histórico).
    """
    query = f"""
    SELECT 
        VC.codCliente,
        VC.tipo,
        VC.participacao,
        P.nome_pes as nome,
        P.cpf_pes as cpf,
        P.dtnasc_pes as dataNascimento,
        PE.Endereco_pend as endereco,
        PE.NumEnd_pend as numero,
        PE.Bairro_pend as bairro,
        PE.Cidade_pend as cidade,
        PE.UF_pend as uf,
        PE.CEP_pend as cep,
        PD.Registro_Doc as rg,
        PD.OrgaoEmissor_Doc as orgao,
        PD.UF_Doc as ufRg,
        PF.estciv_pf as estadoCivil,
        PF.RegCasamento_pf as regimeCasamento
    FROM (
       SELECT 
           Empresa_cven as empresa, Num_CVen as numVenda, Obra_CVen as obra, 
           Cliente_CVen as codCliente, Tipo_CVen as tipo, PorcTitular_Cven as participacao 
       FROM VendaClientes WITH(NOLOCK) 
       UNION ALL
       SELECT 
           Empresa_vrc as empresa, Num_Vrc as numVenda, Obra_Vrc as obra, 
           Cliente_vrc as codCliente, Tipo_vrc as tipo, PorcTitular_Vrc as participacao 
       FROM VendaRecClientes WITH(NOLOCK) 
    ) AS VC
    INNER JOIN Pessoas P WITH(NOLOCK) ON VC.codCliente = P.cod_pes 
    LEFT JOIN PesFis PF WITH(NOLOCK) ON P.cod_pes = PF.cod_pf
    LEFT JOIN PessoasDoc PD WITH(NOLOCK) ON P.cod_pes = PD.CodPes_Doc AND PD.Tipo_Doc = 1
    LEFT JOIN PesEndereco PE WITH(NOLOCK) ON P.cod_pes = PE.CodPes_pend AND PE.Tipo_pend = 0
    WHERE VC.empresa = {empresa}
       AND VC.numVenda = {num_venda}
       AND RTRIM(VC.obra) = '{obra}'
    ORDER BY VC.tipo
    """
    
    try:
        result = execute_query(query)
        clientes = []
        for r in result:
            dt_nasc = r.get('dataNascimento')
            nasc = get_naturalidade(r.get('codCliente'))
            clientes.append({
                'codCliente': r.get('codCliente'),
                'nome': (r.get('nome') or 'NÃO INFORMADO').upper(),
                'cpfCnpj': format_cpf_cnpj(r.get('cpf')),
                'dataNascimento': dt_nasc.strftime('%d/%m/%Y') if hasattr(dt_nasc, 'strftime') else None,
                'rg': r.get('rg') or '',
                'orgaoExpedidor': r.get('orgao') or '',
                'ufRg': r.get('ufRg') or '',
                'estadoCivil': get_estado_civil_label(r.get('estadoCivil')),
                'regimeCasamento': get_regime_casamento_label(r.get('regimeCasamento')),
                'tipo': r.get('tipo'),
                'participacao': float(r.get('participacao') or 0),
                'endereco': (r.get('endereco') or '').upper(),
                'numero': (r.get('numero') or '').upper(),
                'bairro': (r.get('bairro') or '').upper(),
                'cidade': (r.get('cidade') or '').upper(),
                'uf': (r.get('uf') or '').upper(),
                'cep': r.get('cep') or '',
                'cidadeNascimento': (nasc.get('cidadeNascimento') or '').upper(),
                'ufNascimento': (nasc.get('ufNascimento') or '').upper()
            })
        # Deduplicar clientes por código para evitar contagem dupla (caso esteja em VendaClientes e VendaRecClientes)
        seen_clients = set()
        unique_clientes = []
        for c in clientes:
            if c['codCliente'] not in seen_clients:
                unique_clientes.append(c)
                seen_clients.add(c['codCliente'])
        return unique_clientes
    except Exception as e:
        print(f"Erro ao buscar clientes da venda: {e}")
        return []


def calcular_valor_quitacao(empresa: int, obra: str, quadra: str, lote: str, tipos_parcela: list = None):
    """

    Calcula o valor correto para quitação baseado na fórmula do sistema Vinicius.
    Retorna: (valor_quitacao, total_pago, total_confirmado, ultimo_recebimento, historico_transferencias, parcelas_detalhadas)
    
    A lógica usa o MENOR valor entre Val_Parc_Paga e Vl_Confirm para cada parcela.
    Filtra apenas vendas que fazem parte da cadeia de cessões (transferências).
    """
    if tipos_parcela is None:
        tipos_parcela = ['E', 'P', 'S']  # Default: Entrada, Parcela, Comissão
    
    # Escapar strings para SQL
    quadra_safe = quadra.replace("'", "''").strip()
    lote_safe = lote.replace("'", "''").strip()
    
    # Query para buscar a cadeia de cessões usando VendaHist
    # Começa pela venda atual e traça para trás as transferências
    query_vendas_lote = f"""
    WITH VendaAtual AS (
        SELECT DISTINCT V.Num_Ven as NumVenda, V.Empresa_Ven, V.Obra_Ven, V.Data_Ven, 
               V.ValorTot_Ven, V.Status_Ven, P.Nome_pes as Cliente, P.cpf_pes as CPF, P.cod_pes as CodCliente,
               V.DataCessao_Ven as DataCessao, CAST('Vendas' as varchar(20)) as Origem
        FROM ItensVenda IV WITH(NOLOCK)
        INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_Itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven AND IV.Obra_Itv = V.Obra_Ven
        INNER JOIN UnidadePer U WITH(NOLOCK) ON IV.Empresa_Itv = U.Empresa_unid AND IV.Obra_Itv = U.Obra_unid 
            AND IV.Produto_Itv = U.Prod_unid AND IV.CodPerson_Itv = U.NumPer_unid
        LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
        WHERE U.Empresa_unid = {empresa} AND U.Obra_unid = '{obra}' 
          AND RTRIM(LTRIM(U.C1_unid)) = '{quadra_safe}' AND RTRIM(LTRIM(U.C2_unid)) = '{lote_safe}'
          AND V.Status_Ven IN (0, 3)
          
        UNION
        
        SELECT DISTINCT VR.Num_VRec as NumVenda, VR.Empresa_VRec, VR.Obra_VRec, VR.Data_VRec, 
               VR.ValorTot_VRec, VR.Status_VRec, P.Nome_pes as Cliente, P.cpf_pes as CPF, P.cod_pes as CodCliente,
               VR.DataCessao_VRec as DataCessao, CAST('VendasRecebidas' as varchar(20)) as Origem
        FROM ItensRecebidas IR WITH(NOLOCK)
        INNER JOIN VendasRecebidas VR WITH(NOLOCK) ON IR.Empresa_Itr = VR.Empresa_VRec AND IR.NumVend_Itr = VR.Num_VRec AND IR.Obra_Itr = VR.Obra_VRec
        INNER JOIN UnidadePer U WITH(NOLOCK) ON IR.Empresa_Itr = U.Empresa_unid AND IR.Obra_Itr = U.Obra_unid 
            AND IR.Produto_Itr = U.Prod_unid AND IR.CodPerson_Itr = U.NumPer_unid
        LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
        WHERE U.Empresa_unid = {empresa} AND U.Obra_unid = '{obra}' 
          AND RTRIM(LTRIM(U.C1_unid)) = '{quadra_safe}' AND RTRIM(LTRIM(U.C2_unid)) = '{lote_safe}'
          AND VR.Status_VRec IN (0, 3)
    ),
    CadeiaCessoesID AS (
        SELECT NumVenda, Empresa_Ven, Obra_Ven
        FROM VendaAtual
        
        UNION ALL
        
        SELECT VH.NumVend_vhist as NumVenda, C.Empresa_Ven, C.Obra_Ven
        FROM CadeiaCessoesID C
        INNER JOIN VendaHist VH WITH(NOLOCK) 
            ON VH.Empresa_vhist = C.Empresa_Ven 
            AND VH.Obra_vhist = C.Obra_Ven 
            AND VH.NumNovaVend_vhist = C.NumVenda
            AND VH.TipoMnt_vhist IN (2, 8)
    )
    SELECT DISTINCT
        C.NumVenda, C.Empresa_Ven, C.Obra_Ven, V.Data_Ven, V.ValorTot_Ven, P.Nome_pes as Cliente, 
        P.cpf_pes as CPF, P.cod_pes as CodCliente, VH_Origem.DataAssinaturaCessao_vhist as DataCessao,
        CASE WHEN VA.NumVenda IS NOT NULL THEN VA.Origem ELSE CAST('CessaoAnterior' as varchar(20)) END as Origem
    FROM CadeiaCessoesID C
    LEFT JOIN VendaAtual VA ON C.NumVenda = VA.NumVenda AND C.Empresa_Ven = VA.Empresa_Ven AND C.Obra_Ven = VA.Obra_Ven
    LEFT JOIN (
        SELECT Empresa_Ven, Obra_Ven, Num_Ven, Data_Ven, ValorTot_Ven, Cliente_Ven, Status_Ven FROM Vendas WITH(NOLOCK)
        UNION ALL
        SELECT Empresa_VRec, Obra_VRec, Num_VRec, Data_VRec, ValorTot_VRec, Cliente_VRec, Status_VRec FROM VendasRecebidas WITH(NOLOCK)
    ) V ON V.Empresa_Ven = C.Empresa_Ven AND V.Obra_Ven = C.Obra_Ven AND V.Num_Ven = C.NumVenda
    LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
    LEFT JOIN VendaHist VH_Origem WITH(NOLOCK) ON VH_Origem.Empresa_vhist = C.Empresa_Ven AND VH_Origem.Obra_vhist = C.Obra_Ven AND VH_Origem.NumNovaVend_vhist = C.NumVenda AND VH_Origem.TipoMnt_vhist IN (2, 8)
    WHERE C.NumVenda IS NOT NULL
    ORDER BY V.Data_Ven
    OPTION (MAXRECURSION 100)
    """
    
    vendas_result = execute_query(query_vendas_lote)
    if not vendas_result:
        return 0, 0, 0, None, [], []
    
    # Construir lista de vendas para filtrar
    vendas_nums = [str(v.get('NumVenda')) for v in vendas_result if v.get('NumVenda')]
    if not vendas_nums:
        return 0, 0, 0, None, [], []
    
    vendas_in = ','.join(vendas_nums)
    
    # Filtrar por tipos de parcela
    tipos_in = ','.join([f"'{t}'" for t in tipos_parcela])
    
    # Query para calcular pagamentos por venda (soma de MIN(ValParcPaga, VlConfirm))
    query_pagamentos_venda = f"""
    SELECT 
        R.NumVend_Rec AS NumVenda,
        SUM(
            CASE 
                WHEN (R.Valor_Rec + ISNULL(R.VlJurosParc_Rec, 0) + ISNULL(R.VlCorrecao_Rec, 0) + 
                      ISNULL(R.VlAcres_Rec, 0) + ISNULL(R.VlTaxaBol_Rec, 0) + ISNULL(R.VlMulta_Rec, 0) + 
                      ISNULL(R.VlJuros_Rec, 0) + ISNULL(R.VlCorrecaoAtr_Rec, 0)
                      - (ISNULL(R.VlDesconto_Rec, 0) + ISNULL(R.ValDescontoCusta_Rec, 0) + 
                         ISNULL(R.ValDescontoImposto_Rec, 0) + ISNULL(R.ValDescontoCondicional_rec, 0))
                      + ISNULL(R.ValorConf_Rec, 0) + ISNULL(R.VlJurosParcConf_Rec, 0) + 
                      ISNULL(R.VlCorrecaoConf_Rec, 0) + ISNULL(R.VlAcresConf_Rec, 0) + 
                      ISNULL(R.VlTaxaBolConf_Rec, 0) + ISNULL(R.VlMultaConf_Rec, 0) + 
                      ISNULL(R.VlJurosConf_Rec, 0) + ISNULL(R.VlCorrecaoAtrConf_Rec, 0)
                      - (ISNULL(R.VlDescontoConf_Rec, 0) + ISNULL(R.ValDescontoCustaConf_Rec, 0) + 
                         ISNULL(R.ValDescontoImpostoConf_Rec, 0) + ISNULL(R.ValDescontoCondicionalConf_rec, 0)))
                < (ISNULL(R.VlCorrecao_Rec, 0) + ISNULL(R.VlCorrecaoConf_Rec, 0) 
                   + CASE 
                       WHEN R.Tipo_Rec IN ('R', 'A') THEN 0 
                       ELSE CASE ISNULL(VR.AniversarioContr_VRec, 0)
                           WHEN 0 THEN (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0))  
                           ELSE (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0) + 
                                 ISNULL(R.VlJurosParcEmb_Rec, 0) + ISNULL(R.VlJurosParcEmbConf_Rec, 0) + 
                                 ISNULL(R.VlCorrecaoEmb_Rec, 0) + ISNULL(R.VlCorrecaoEmbConf_Rec, 0))
                           END
                    END)
                THEN (R.Valor_Rec + ISNULL(R.VlJurosParc_Rec, 0) + ISNULL(R.VlCorrecao_Rec, 0) + 
                      ISNULL(R.VlAcres_Rec, 0) + ISNULL(R.VlTaxaBol_Rec, 0) + ISNULL(R.VlMulta_Rec, 0) + 
                      ISNULL(R.VlJuros_Rec, 0) + ISNULL(R.VlCorrecaoAtr_Rec, 0)
                      - (ISNULL(R.VlDesconto_Rec, 0) + ISNULL(R.ValDescontoCusta_Rec, 0) + 
                         ISNULL(R.ValDescontoImposto_Rec, 0) + ISNULL(R.ValDescontoCondicional_rec, 0))
                      + ISNULL(R.ValorConf_Rec, 0) + ISNULL(R.VlJurosParcConf_Rec, 0) + 
                      ISNULL(R.VlCorrecaoConf_Rec, 0) + ISNULL(R.VlAcresConf_Rec, 0) + 
                      ISNULL(R.VlTaxaBolConf_Rec, 0) + ISNULL(R.VlMultaConf_Rec, 0) + 
                      ISNULL(R.VlJurosConf_Rec, 0) + ISNULL(R.VlCorrecaoAtrConf_Rec, 0)
                      - (ISNULL(R.VlDescontoConf_Rec, 0) + ISNULL(R.ValDescontoCustaConf_Rec, 0) + 
                         ISNULL(R.ValDescontoImpostoConf_Rec, 0) + ISNULL(R.ValDescontoCondicionalConf_rec, 0)))
                ELSE (ISNULL(R.VlCorrecao_Rec, 0) + ISNULL(R.VlCorrecaoConf_Rec, 0) 
                   + CASE 
                       WHEN R.Tipo_Rec IN ('R', 'A') THEN 0 
                       ELSE CASE ISNULL(VR.AniversarioContr_VRec, 0)
                           WHEN 0 THEN (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0))  
                           ELSE (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0) + 
                                 ISNULL(R.VlJurosParcEmb_Rec, 0) + ISNULL(R.VlJurosParcEmbConf_Rec, 0) + 
                                 ISNULL(R.VlCorrecaoEmb_Rec, 0) + ISNULL(R.VlCorrecaoEmbConf_Rec, 0))
                           END
                    END)
            END
        ) AS ValorPago
    FROM Recebidas R WITH(NOLOCK)
    LEFT JOIN VendasRecebidas VR WITH(NOLOCK) ON R.Empresa_Rec = VR.Empresa_VRec 
        AND R.Obra_Rec = VR.Obra_VRec AND R.NumVend_Rec = VR.Num_VRec
    WHERE R.Empresa_Rec = {empresa}
      AND R.Obra_Rec = '{obra}'
      AND R.NumVend_Rec IN ({vendas_in})
      AND R.Data_Rec IS NOT NULL
      AND R.Tipo_Rec IN ({tipos_in})
    GROUP BY R.NumVend_Rec
    """
    
    try:
        pagamentos_result = execute_query(query_pagamentos_venda)
        pagamentos_map = {str(p.get('NumVenda')): float(p.get('ValorPago') or 0) for p in pagamentos_result}
    except Exception as e:
        print(f"Erro ao calcular pagamentos por venda: {e}")
        pagamentos_map = {}
    
    # Preparar histórico de transferências COM valores de pagamento calculados
    historico_transferencias = []
    for v in vendas_result:
        n_venda = v.get('NumVenda')
        valor_pago = pagamentos_map.get(str(n_venda), 0)
        
        # Buscar TODOS os clientes dessa venda específica para citar no histórico
        clientes_venda = get_clientes_venda(empresa, obra, n_venda)
        
        # Agregar nomes e porcentagens dos Titulares (tipo 0)
        titulares = [c for c in clientes_venda if c.get('tipo') == 0]
        
        # Armazenar detalhes individuais dos titulares
        owners_list = []
        if titulares:
            for t in titulares:
                owners_list.append({
                    'nome': t['nome'].upper(),
                    'participacao': t.get('participacao', 0)
                })
        
        # Criar descrição do cliente (sem porcentagens, apenas nomes separados)
        if not titulares:
            cliente_desc = v.get('Cliente', 'N/A')
        else:
            cliente_desc = ", ".join([t['nome'].upper() for t in titulares])

        historico_transferencias.append({
            'numVenda': n_venda,
            'cliente': cliente_desc,
            'owners': owners_list,  # Lista de {nome, participacao}
            'cpf': v.get('CPF', ''),
            'codCliente': v.get('CodCliente'),
            'dataVenda': v.get('Data_Ven'),
            'dataCessao': v.get('DataCessao'),
            'valorVenda': v.get('ValorTot_Ven', 0),
            'valorPago': valor_pago,
            'origem': v.get('Origem')
        })
    
    vendas_in = ','.join(vendas_nums)
    
    # Filtrar por tipos de parcela
    tipos_in = ','.join([f"'{t}'" for t in tipos_parcela])
    
    # Query principal com a fórmula correta do sistema Vinicius
    query_parcelas = f"""
    SELECT 
        R.NumParc_Rec AS NumParcela,
        R.Tipo_Rec AS Tipo,
        R.NumVend_Rec AS NumVenda,
        CONVERT(varchar, R.Data_Rec, 23) AS DataRecebimento,
        -- Val_Parc_Paga: soma de todos os valores pagos menos descontos
        (R.Valor_Rec + ISNULL(R.VlJurosParc_Rec, 0) + ISNULL(R.VlCorrecao_Rec, 0) + 
         ISNULL(R.VlAcres_Rec, 0) + ISNULL(R.VlTaxaBol_Rec, 0) + ISNULL(R.VlMulta_Rec, 0) + 
         ISNULL(R.VlJuros_Rec, 0) + ISNULL(R.VlCorrecaoAtr_Rec, 0)
         - (ISNULL(R.VlDesconto_Rec, 0) + ISNULL(R.ValDescontoCusta_Rec, 0) + 
            ISNULL(R.ValDescontoImposto_Rec, 0) + ISNULL(R.ValDescontoCondicional_rec, 0))
         + ISNULL(R.ValorConf_Rec, 0) + ISNULL(R.VlJurosParcConf_Rec, 0) + 
         ISNULL(R.VlCorrecaoConf_Rec, 0) + ISNULL(R.VlAcresConf_Rec, 0) + 
         ISNULL(R.VlTaxaBolConf_Rec, 0) + ISNULL(R.VlMultaConf_Rec, 0) + 
         ISNULL(R.VlJurosConf_Rec, 0) + ISNULL(R.VlCorrecaoAtrConf_Rec, 0)
         - (ISNULL(R.VlDescontoConf_Rec, 0) + ISNULL(R.ValDescontoCustaConf_Rec, 0) + 
            ISNULL(R.ValDescontoImpostoConf_Rec, 0) + ISNULL(R.ValDescontoCondicionalConf_rec, 0))
        ) AS ValParcPaga,
        -- Vl_Confirm: valor base + correção, com lógica especial
        (ISNULL(R.VlCorrecao_Rec, 0) + ISNULL(R.VlCorrecaoConf_Rec, 0) 
        + CASE 
            WHEN R.Tipo_Rec IN ('R', 'A') 
            THEN 0 
            ELSE  
                CASE ISNULL(VR.AniversarioContr_VRec, 0)
                    WHEN 0  
                    THEN (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0))  
                    ELSE (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0) + 
                          ISNULL(R.VlJurosParcEmb_Rec, 0) + ISNULL(R.VlJurosParcEmbConf_Rec, 0) + 
                          ISNULL(R.VlCorrecaoEmb_Rec, 0) + ISNULL(R.VlCorrecaoEmbConf_Rec, 0))
                END
        END) AS VlConfirm
    FROM Recebidas R WITH(NOLOCK)
    LEFT JOIN VendasRecebidas VR WITH(NOLOCK) ON R.Empresa_Rec = VR.Empresa_VRec 
        AND R.Obra_Rec = VR.Obra_VRec AND R.NumVend_Rec = VR.Num_VRec
    WHERE R.Empresa_Rec = {empresa}
      AND R.Obra_Rec = '{obra}'
      AND R.NumVend_Rec IN ({vendas_in})
      AND R.Data_Rec IS NOT NULL
      AND R.Tipo_Rec IN ({tipos_in})
    ORDER BY R.Data_Rec, R.NumParc_Rec
    """
    
    try:
        parcelas_result = execute_query(query_parcelas)
    except Exception as e:
        print(f"Erro ao executar query de parcelas: {e}")
        return 0, 0, 0, None, historico_transferencias, []
    
    if not parcelas_result:
        return 0, 0, 0, None, historico_transferencias, []
    
    # Calcular totais
    total_pago = 0.0
    total_confirmado = 0.0
    total_quitacao = 0.0
    ultimo_recebimento = None
    parcelas_detalhadas = []
    
    for p in parcelas_result:
        val_pago = float(p.get('ValParcPaga') or 0)
        vl_confirm = float(p.get('VlConfirm') or 0)
        vl_menor = min(val_pago, vl_confirm) if vl_confirm > 0 else val_pago
        
        total_pago += val_pago
        total_confirmado += vl_confirm
        total_quitacao += vl_menor
        
        dt_receb = p.get('DataRecebimento')
        if dt_receb:
            try:
                dt_obj = datetime.strptime(dt_receb, '%Y-%m-%d')
                if ultimo_recebimento is None or dt_obj > ultimo_recebimento:
                    ultimo_recebimento = dt_obj
            except:
                pass
        
        parcelas_detalhadas.append({
            'parcela': p.get('NumParcela'),
            'tipo': p.get('Tipo'),
            'tipoDescricao': TIPO_PARCELA_MAP.get(str(p.get('Tipo', '')).upper(), p.get('Tipo')),
            'dataRecebimento': dt_receb,
            'valorPago': val_pago,
            'valorConfirmado': vl_confirm,
            'valorMenor': vl_menor,
            'numVenda': p.get('NumVenda')
        })
    
    return total_quitacao, total_pago, total_confirmado, ultimo_recebimento, historico_transferencias, parcelas_detalhadas



def make_header_footer(canvas, doc):
    """Adiciona cabeçalho com logo e rodapé com site em cada página"""
    canvas.saveState()
    
    # Caminho da logo PNG
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logoazulvalle.png')
    
    # Cabeçalho - Logo centralizada
    if os.path.exists(logo_path):
        try:
            # Carregar imagem PNG
            # Ajustar tamanho proporcionalmente
            # Assumindo largura alvo de ~7cm (aprox 200 pontos typográficos)
            target_width = 7 * cm
            
            # Usar utils do reportlab para obter tamanho original se possível, 
            # ou confiar no drawImage que escala se darmos width/height
            # drawImage(image, x, y, width=None, height=None)
            
            # Para centralizar, precisamos saber proporção. 
            # drawImage preserveAspectRatio=True com width definido ajusta height autom?
            # Melhor usar ImageReader para pegar dimensões se necessário, mas vamos tentar fixar height razoável
            
            # Abordagem simples: drawImage com preserveAspectRatio
            # Mas drawImage direto no canvas não tem preserveAspectRatio fácil sem calcular
            
            from reportlab.lib.utils import ImageReader
            img = ImageReader(logo_path)
            iw, ih = img.getSize()
            aspect = ih / float(iw)
            
            img_width = 70  # Logo menor
            img_height = img_width * aspect
            
            x = (A4[0] - img_width) / 2
            y = A4[1] - 10*mm - img_height # Margem superior aumentada para logo ficar mais abaixo
            
            canvas.drawImage(logo_path, x, y, width=img_width, height=img_height, mask='auto')
                
        except Exception as e:
            print(f"Erro ao carregar logo PNG: {e}")
    
    # Rodapé - site centralizado e número da página à direita
    canvas.setFillColor(colors.HexColor('#6B7280'))
    canvas.setFont('Helvetica', 9)
    # Site centralizado
    canvas.drawCentredString(A4[0] / 2, 7*mm, "www.valleprime.com.br")
    # Desenvolvedor à esquerda
    # canvas.setFont('Helvetica', 8)
    # canvas.drawString(15*mm, 7*mm, "Desenvolvido por Vinicius Dev")
    # Número da página à direita
    canvas.setFillColor(colors.black)
    canvas.setFont('Helvetica', 10)
    page_num = canvas.getPageNumber()
    canvas.drawRightString(A4[0] - 20*mm, 12*mm, f"Pag.: {page_num}")
    
    canvas.restoreState()

@router.get("/quitacao/lotes")
async def get_lotes_quitados(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Lista todos os lotes quitados de uma obra"""
    
    # Query com fallback para VendasRecebidas
    query = f"""
    SELECT 
        U.Identificador_Unid as identificador,
        U.C1_unid as quadra,
        U.C2_unid as lote,
        U.Qtde_Unid as area,
        U.C4_unid as logradouro,
        U.C5_unid as frente,
        U.C7_unid as fundo,
        U.C9_unid as ladoDireito,
        U.C11_unid as ladoEsquerdo,
        U.C12_unid as chanfro,
        U.ValPreco_Unid * ISNULL(U.Qtde_Unid, 1) as valorCalculado,
        COALESCE(VendasAtivas.Num_Ven, VendasRec.Num_VRec) as numVenda,
        COALESCE(VendasAtivas.ValorTot_Ven, VendasRec.ValorTot_VRec) as valor,
        COALESCE(VendasAtivas.Nome_pes, VendasRec.Nome_pes) as cliente,
        COALESCE(VendasAtivas.cpf_pes, VendasRec.cpf_pes) as cpf,
        COALESCE(VendasAtivas.cod_pes, VendasRec.cod_pes) as codCliente,
        O.Descr_Obr as nomeObra,
        CASE 
            WHEN VendasAtivas.Num_Ven IS NOT NULL THEN 'V'
            WHEN VendasRec.Num_VRec IS NOT NULL THEN 'VR'
            ELSE NULL
        END as tipoVenda
    FROM UnidadePer U WITH(NOLOCK)
    INNER JOIN Obras O WITH(NOLOCK) ON U.Empresa_unid = O.Empresa_Obr AND U.Obra_unid = O.Cod_Obr
    -- Tentar via Vendas + ItensVenda
    OUTER APPLY (
        SELECT TOP 1 V.Num_Ven, V.ValorTot_Ven, P.Nome_pes, P.cpf_pes, P.cod_pes
        FROM ItensVenda IV WITH(NOLOCK)
        INNER JOIN Vendas V WITH(NOLOCK) 
            ON IV.Empresa_itv = V.Empresa_Ven 
            AND IV.Obra_Itv = V.Obra_Ven
            AND IV.NumVend_Itv = V.Num_Ven
        LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
        WHERE IV.Empresa_itv = U.Empresa_unid 
          AND IV.Obra_Itv = U.Obra_unid
          AND IV.Produto_Itv = U.Prod_unid 
          AND IV.CodPerson_Itv = U.NumPer_unid
          AND V.Status_Ven IN (0, 3)
    ) VendasAtivas
    -- Fallback via VendasRecebidas + ItensRecebidas
    OUTER APPLY (
        SELECT TOP 1 VR.Num_VRec, VR.ValorTot_VRec, P.Nome_pes, P.cpf_pes, P.cod_pes
        FROM ItensRecebidas IR WITH(NOLOCK)
        INNER JOIN VendasRecebidas VR WITH(NOLOCK)
            ON IR.Empresa_Itr = VR.Empresa_VRec
            AND IR.Obra_Itr = VR.Obra_VRec
            AND IR.NumVend_Itr = VR.Num_VRec
        LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
        WHERE IR.Empresa_Itr = U.Empresa_unid 
          AND IR.Obra_Itr = U.Obra_unid
          AND IR.Produto_Itr = U.Prod_unid 
          AND IR.CodPerson_Itr = U.NumPer_unid
          AND VR.Status_VRec IN (0, 3)
          AND VendasAtivas.Num_Ven IS NULL
    ) VendasRec
    WHERE U.Empresa_unid = {empresa}
      AND U.Obra_unid = '{obra}'
      AND U.Vendido_unid = 4
    ORDER BY U.C1_unid, U.C2_unid
    """
    
    try:
        result = execute_query(query)
        lotes = []
        for row in result:
            valor = row.get('valor') or row.get('valorCalculado') or 0
            lotes.append({
                "identificador": row.get('identificador', ''),
                "quadra": str(row.get('quadra', '')).strip(),
                "lote": str(row.get('lote', '')).strip(),
                "area": float(row.get('area', 0) or 0),
                "logradouro": row.get('logradouro', ''),
                "numVenda": row.get('numVenda'),
                "valor": float(valor),
                "cliente": row.get('cliente', ''),
                "cpf": format_cpf_cnpj(row.get('cpf', '')),
                "codCliente": row.get('codCliente'),
                "nomeObra": row.get('nomeObra', ''),
                "tipoVenda": row.get('tipoVenda')
            })
        
        return {
            "lotes": lotes,
            "total": len(lotes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar lotes quitados: {str(e)}")


@router.get("/empresas")
async def get_empresas():
    """Lista todas as empresas disponíveis"""
    query = """
    SELECT DISTINCT Codigo_emp as codigo, RTRIM(LTRIM(Desc_emp)) as nome
    FROM Empresas WITH(NOLOCK)
    WHERE Codigo_emp IN (SELECT DISTINCT Empresa_unid FROM UnidadePer WITH(NOLOCK))
    ORDER BY Codigo_emp
    """
    try:
        result = execute_query(query)
        empresas = [{"codigo": r.get('codigo'), "nome": r.get('nome', '')} for r in result]
        return {"empresas": empresas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar empresas: {e}")


@router.get("/obras")
async def get_obras(empresa: int = Query(..., description="Código da empresa")):
    """Lista todas as obras de uma empresa"""
    query = f"""
    SELECT DISTINCT 
        RTRIM(LTRIM(Cod_Obr)) as codigo, 
        RTRIM(LTRIM(Descr_Obr)) as nome
    FROM Obras WITH(NOLOCK)
    WHERE Empresa_Obr = {empresa}
      AND Cod_Obr IN (SELECT DISTINCT Obra_unid FROM UnidadePer WITH(NOLOCK) WHERE Empresa_unid = {empresa})
    ORDER BY codigo
    """
    try:
        result = execute_query(query)
        # Remove espaços internos do código da obra
        obras = [{"codigo": str(r.get('codigo', '')).replace(' ', ''), "nome": r.get('nome', '')} for r in result]
        return {"obras": obras}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar obras: {e}")


@router.get("/quitacao/dados")
async def get_dados_quitacao(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    venda: Optional[int] = Query(None, description="Número da venda (opcional)"),
    quadra: Optional[str] = Query(None, description="Quadra do lote (opcional)"),
    lote: Optional[str] = Query(None, description="Lote (opcional)")
):
    """Busca dados completos para documentos de quitação.
    Pode buscar por número de venda OU por quadra/lote."""
    
    # Se não tiver venda, precisa ter quadra E lote
    if venda is None and (quadra is None or lote is None):
        raise HTTPException(status_code=400, detail="Informe número da venda OU quadra e lote")
    
    # Query principal com fallback para VendasRecebidas
    if venda:
        # Buscar por venda (Vendas ou VendasRecebidas)
        query_lote = f"""
        SELECT 
            U.Identificador_Unid as identificador,
            U.C1_unid as quadra,
            U.C2_unid as lote,
            U.Qtde_Unid as area,
            U.C4_unid as logradouro,
            U.C5_unid as frente,
            U.C7_unid as fundo,
            U.C9_unid as ladoDireito,
            U.C11_unid as ladoEsquerdo,
            U.C12_unid as chanfro,
            U.ValPreco_Unid * ISNULL(U.Qtde_Unid, 1) as valorCalculado,
            COALESCE(V.Num_Ven, VR.Num_VRec) as numVenda,
            COALESCE(V.ValorTot_Ven, VR.ValorTot_VRec) as valor,
            COALESCE(P.Nome_pes, P2.Nome_pes) as cliente,
            COALESCE(P.cpf_pes, P2.cpf_pes) as cpf,
            COALESCE(P.dtnasc_pes, P2.dtnasc_pes) as dataNascCliente,
            COALESCE(P.cod_pes, P2.cod_pes) as codCliente,
            O.Descr_Obr as nomeObra,
            COALESCE(Cidades.Desc_cid, O.cid_obr) as cidadeObra,
            COALESCE(Cidades.DescUF_cid, O.uf_obr) as ufObra
        FROM UnidadePer U WITH(NOLOCK)
        INNER JOIN Obras O WITH(NOLOCK) ON U.Empresa_unid = O.Empresa_Obr AND U.Obra_unid = O.Cod_Obr
        -- Join para buscar cidade real via UnidadeDetalhe -> LogBairro -> Bairro -> Cidades
        LEFT JOIN UnidadeDetalhe UD WITH(NOLOCK) 
            ON UD.Empresa_udt = U.Empresa_unid 
            AND UD.Prod_udt = U.Prod_unid 
            AND UD.NumPer_udt = U.NumPer_unid
        LEFT JOIN LogBairro ON UD.NumBrrLogBrr_udt = LogBairro.NumBrr_logBrr 
            AND UD.NumLogrLogBrr_udt = LogBairro.NumLogr_logBrr
        LEFT JOIN Bairro ON Bairro.Num_brr = LogBairro.NumBrr_logBrr
        LEFT JOIN Cidades ON Cidades.Num_cid = Bairro.NumCid_brr
        -- Tentar via Vendas
        LEFT JOIN ItensVenda IV WITH(NOLOCK) 
            ON U.Empresa_unid = IV.Empresa_itv AND U.Prod_unid = IV.Produto_Itv AND U.NumPer_unid = IV.CodPerson_Itv
        LEFT JOIN Vendas V WITH(NOLOCK) 
            ON IV.Empresa_itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven AND V.Num_Ven = {venda}
        LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
        -- Fallback via VendasRecebidas + ItensRecebidas
        LEFT JOIN ItensRecebidas IR WITH(NOLOCK)
            ON U.Empresa_unid = IR.Empresa_Itr AND U.Prod_unid = IR.Produto_Itr AND U.NumPer_unid = IR.CodPerson_Itr
        LEFT JOIN VendasRecebidas VR WITH(NOLOCK) 
            ON IR.Empresa_Itr = VR.Empresa_VRec AND IR.NumVend_Itr = VR.Num_VRec AND VR.Num_VRec = {venda}
        LEFT JOIN Pessoas P2 WITH(NOLOCK) ON VR.Cliente_VRec = P2.cod_pes
        WHERE U.Empresa_unid = {empresa}
          AND U.Obra_unid = '{obra}'
          AND U.Vendido_unid = 4
          AND (V.Num_Ven = {venda} OR VR.Num_VRec = {venda})
        """
    else:
        # Buscar por quadra/lote
        query_lote = f"""
        SELECT 
            U.Identificador_Unid as identificador,
            U.C1_unid as quadra,
            U.C2_unid as lote,
            U.Qtde_Unid as area,
            U.C4_unid as logradouro,
            U.C5_unid as frente,
            U.C7_unid as fundo,
            U.C9_unid as ladoDireito,
            U.C11_unid as ladoEsquerdo,
            U.C12_unid as chanfro,
            U.ValPreco_Unid * ISNULL(U.Qtde_Unid, 1) as valorCalculado,
            COALESCE(VendasAtivas.Num_Ven, VendasRec.Num_VRec) as numVenda,
            COALESCE(VendasAtivas.ValorTot_Ven, VendasRec.ValorTot_VRec, U.ValPreco_Unid * ISNULL(U.Qtde_Unid, 1)) as valor,
            COALESCE(VendasAtivas.Nome_pes, VendasRec.Nome_pes) as cliente,
            COALESCE(VendasAtivas.cpf_pes, VendasRec.cpf_pes) as cpf,
            COALESCE(VendasAtivas.dtnasc_pes, VendasRec.dtnasc_pes) as dataNascCliente,
            COALESCE(VendasAtivas.cod_pes, VendasRec.cod_pes) as codCliente,
            O.Descr_Obr as nomeObra,
            COALESCE(Cidades.Desc_cid, O.cid_obr) as cidadeObra,
            COALESCE(Cidades.DescUF_cid, O.uf_obr) as ufObra
        FROM UnidadePer U WITH(NOLOCK)
        INNER JOIN Obras O WITH(NOLOCK) ON U.Empresa_unid = O.Empresa_Obr AND U.Obra_unid = O.Cod_Obr
        -- Join para buscar cidade real via UnidadeDetalhe -> LogBairro -> Bairro -> Cidades
        LEFT JOIN UnidadeDetalhe UD WITH(NOLOCK) 
            ON UD.Empresa_udt = U.Empresa_unid 
            AND UD.Prod_udt = U.Prod_unid 
            AND UD.NumPer_udt = U.NumPer_unid
        LEFT JOIN LogBairro ON UD.NumBrrLogBrr_udt = LogBairro.NumBrr_logBrr 
            AND UD.NumLogrLogBrr_udt = LogBairro.NumLogr_logBrr
        LEFT JOIN Bairro ON Bairro.Num_brr = LogBairro.NumBrr_logBrr
        LEFT JOIN Cidades ON Cidades.Num_cid = Bairro.NumCid_brr
        -- Tentar via Vendas + ItensVenda - ORDENAR por Num_Ven DESC para pegar a ÚLTIMA venda (cliente atual)
        OUTER APPLY (
            SELECT TOP 1 V.Num_Ven, V.ValorTot_Ven, P.Nome_pes, P.cpf_pes, P.dtnasc_pes, P.cod_pes
            FROM ItensVenda IV WITH(NOLOCK)
            INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven
            LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
            WHERE IV.Empresa_itv = U.Empresa_unid 
              AND IV.Produto_Itv = U.Prod_unid 
              AND IV.CodPerson_Itv = U.NumPer_unid
            ORDER BY V.Num_Ven DESC
        ) VendasAtivas
        -- Fallback via VendasRecebidas + ItensRecebidas (vinculando ao lote correto)
        OUTER APPLY (
            SELECT TOP 1 VR.Num_VRec, VR.ValorTot_VRec, P.Nome_pes, P.cpf_pes, P.dtnasc_pes, P.cod_pes
            FROM ItensRecebidas IR WITH(NOLOCK)
            INNER JOIN VendasRecebidas VR WITH(NOLOCK) 
                ON IR.Empresa_Itr = VR.Empresa_VRec 
                AND IR.NumVend_Itr = VR.Num_VRec 
                AND IR.Obra_Itr = VR.Obra_VRec
            LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
            WHERE IR.Empresa_Itr = U.Empresa_unid 
              AND IR.Obra_Itr = U.Obra_unid
              AND IR.Produto_Itr = U.Prod_unid
              AND IR.CodPerson_Itr = U.NumPer_unid
              AND VR.Status_VRec IN (0, 3)
            ORDER BY VR.Num_VRec DESC
        ) VendasRec
        WHERE U.Empresa_unid = {empresa}
          AND U.Obra_unid = '{obra}'
          AND U.Vendido_unid = 4
          AND RTRIM(LTRIM(U.C1_unid)) = '{quadra}'
          AND RTRIM(LTRIM(U.C2_unid)) = '{lote}'
        """
    
    try:
        lote_result = execute_query(query_lote)
        
        if not lote_result:
            raise HTTPException(status_code=404, detail="Lote não encontrado ou não está quitado")
        
        lote_data = lote_result[0]
        cod_cliente = lote_data.get('codCliente')
        num_venda_atual = lote_data.get('numVenda')
        
        # Identificar o lote único para buscar histórico
        # Precisamos de Prod_unid e NumPer_unid que não estavam na query anterior, 
        # mas podemos buscar agora com base na Quadra/Lote se não estiverem
        # Vou assumir que o identificador único (Empresa, Obra, Quadra, Lote) é suficiente para achar o UnitID
        
        quadra_str = lote_data.get('quadra', '').strip()
        lote_str = lote_data.get('lote', '').strip()
        
        # Buscar histórico de vendas para este lote (Soma de pagamentos)
        total_pago_historico = 0.0
        ultimo_receb = None
        
        # Query para encontrar TODAS as vendas deste lote e somar seus pagamentos
        query_historico = f"""
        WITH VendasLote AS (
            SELECT V.Num_Ven as NumVenda, V.Empresa_Ven, V.Obra_Ven
            FROM ItensVenda IV WITH(NOLOCK)
            INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_Itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven
            INNER JOIN UnidadePer U WITH(NOLOCK) ON IV.Empresa_Itv = U.Empresa_unid AND IV.Obra_Itv = U.Obra_unid AND IV.Produto_Itv = U.Prod_unid AND IV.CodPerson_Itv = U.NumPer_unid
            WHERE U.Empresa_unid = {empresa} AND U.Obra_unid = '{obra}' 
              AND RTRIM(LTRIM(U.C1_unid)) = '{quadra_str}' AND RTRIM(LTRIM(U.C2_unid)) = '{lote_str}'
              
            UNION
            
            SELECT VR.Num_VRec as NumVenda, VR.Empresa_VRec, VR.Obra_VRec
            FROM ItensRecebidas IR WITH(NOLOCK)
            INNER JOIN VendasRecebidas VR WITH(NOLOCK) ON IR.Empresa_Itr = VR.Empresa_VRec AND IR.NumVend_Itr = VR.Num_VRec
            INNER JOIN UnidadePer U WITH(NOLOCK) ON IR.Empresa_Itr = U.Empresa_unid AND IR.Obra_Itr = U.Obra_unid AND IR.Produto_Itr = U.Prod_unid AND IR.CodPerson_Itr = U.NumPer_unid
            WHERE U.Empresa_unid = {empresa} AND U.Obra_unid = '{obra}' 
              AND RTRIM(LTRIM(U.C1_unid)) = '{quadra_str}' AND RTRIM(LTRIM(U.C2_unid)) = '{lote_str}'
        )
        SELECT 
            SUM(R.Valor_Rec + R.ValorConf_Rec + ISNULL(R.VlCorrecao_Rec,0) + ISNULL(R.VlCorrecaoConf_Rec,0) + ISNULL(R.VlJuros_Rec,0) + ISNULL(R.VlJurosConf_Rec,0) + ISNULL(R.VlMulta_Rec,0) + ISNULL(R.VlMultaConf_Rec,0)) as TotalPago,
            MAX(R.Data_Rec) as UltimoRecebimento
        FROM Recebidas R WITH(NOLOCK)
        INNER JOIN VendasLote VL ON R.Empresa_Rec = VL.Empresa_Ven AND R.Obra_Rec = VL.Obra_Ven AND R.NumVend_Rec = VL.NumVenda
        WHERE R.Tipo_Rec IN ('P', 'S', 'I') -- Parcelas, Sinais, Intermediarias (Geralmente principal)
        """
        
        try:
            hist_result = execute_query(query_historico)
            if hist_result and hist_result[0].get('TotalPago'):
                total_pago_historico = float(hist_result[0]['TotalPago'])
                ultimo_receb = hist_result[0]['UltimoRecebimento']
        except Exception as e:
            print(f"Erro ao calcular histórico: {e}")
            
        # Se não achou pagamentos no histórico (caso raro ou erro), tenta fallback para o valor da venda atual
        # Mas se achou, usa o total pago como o valor do lote
        valor_final = total_pago_historico if total_pago_historico > 0 else (lote_data.get('valor') or 0)
        
        # Atualiza o dicionário de lote_data para usar depois
        lote_data['valor'] = valor_final
        
        # Endereço do cliente
        endereco = {}
        if cod_cliente:
            query_endereco = f"""
            SELECT TOP 1
                Endereco_pend as endereco,
                NumEnd_pend as numero,
                Bairro_pend as bairro,
                Cidade_pend as cidade,
                UF_pend as uf,
                CEP_pend as cep
            FROM PesEndereco WITH(NOLOCK)
            WHERE CodPes_pend = {cod_cliente}
            AND Tipo_pend = 0
            """
            endereco_result = execute_query(query_endereco)
            if endereco_result:
                endereco = endereco_result[0]
        
        # Dados da empresa vendedora (busca do banco de dados)
        empresa_vendedora = get_empresa_dados(empresa)
        
        valor = lote_data.get('valor') or lote_data.get('valorCalculado') or 0
        
        return {
            "lote": {
                "quadra": str(lote_data.get('quadra', '')).strip(),
                "lote": str(lote_data.get('lote', '')).strip(),
                "area": float(lote_data.get('area', 0) or 0),
                "logradouro": lote_data.get('logradouro', ''),
                "frente": lote_data.get('frente', ''),
                "fundo": lote_data.get('fundo', ''),
                "ladoDireito": lote_data.get('ladoDireito', ''),
                "ladoEsquerdo": lote_data.get('ladoEsquerdo', ''),
                "chanfro": lote_data.get('chanfro', ''),
                # Formatar nome da obra com cidade e UF
                "nomeObra": "RESIDENCIAL IPITINGA - TOMÉ-AÇU - PA" if (empresa == 999 and str(obra).strip() == '70100') else f"{lote_data.get('nomeObra', '')} - {lote_data.get('cidadeObra', 'Tomé-Açu') or 'Tomé-Açu'}-{lote_data.get('ufObra', 'PA') or 'PA'}",
                "cidadeObra": lote_data.get('cidadeObra', '') or 'Tomé-Açu',
                "ufObra": lote_data.get('ufObra', '') or 'PA'
            },
            "venda": {
                "numero": num_venda_atual,
                "valor": float(valor),
                "ultimoRecebimento": ultimo_receb.strftime('%d/%m/%Y') if ultimo_receb else None
            },
            "cliente": {
                "nome": lote_data.get('cliente', '') or 'NÃO INFORMADO',
                "cpfCnpj": format_cpf_cnpj(lote_data.get('cpf', '')),
                "dataNascimento": lote_data.get('dataNascCliente').strftime('%d/%m/%Y') if lote_data.get('dataNascCliente') else None,
                "endereco": endereco.get('endereco', ''),
                "numero": endereco.get('numero', ''),
                "bairro": endereco.get('bairro', ''),
                "cidade": endereco.get('cidade', ''),
                "uf": endereco.get('uf', ''),
                "cep": endereco.get('cep', '')
            },
            "empresaVendedora": empresa_vendedora,
            "representanteLegal": REPRESENTANTE_LEGAL
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados: {str(e)}")


@router.get("/quitacao/carta")
async def gerar_carta_quitacao(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    venda: Optional[int] = Query(None, description="Número da venda (opcional)"),
    quadra: Optional[str] = Query(None, description="Quadra do lote (opcional)"),
    lote: Optional[str] = Query(None, description="Lote (opcional)"),
    cidade: Optional[str] = Query(None, description="Cidade para o documento (opcional)"),
    uf: Optional[str] = Query(None, description="UF para o documento (opcional)"),
    data: Optional[str] = Query(None, description="Data do documento YYYY-MM-DD (opcional)")
):
    """Gera PDF da Carta de Quitação"""
    
    # Buscar dados
    try:
        dados = await get_dados_quitacao(empresa, obra, venda, quadra, lote)
    except HTTPException as e:
        raise e
    
    # Sobrescrever cidade/uf/data se fornecidos
    if cidade:
        dados['lote']['cidadeObra'] = cidade
    if uf:
        dados['lote']['ufObra'] = uf
    
    # Processar data
    data_documento = None
    if data:
        try:
            data_documento = datetime.strptime(data, '%Y-%m-%d')
        except:
            pass
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=25*mm,
        rightMargin=25*mm,
        topMargin=25*mm,
        bottomMargin=25*mm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName='Helvetica-Bold'
    )
    
    corpo_style = ParagraphStyle(
        'Corpo',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_JUSTIFY,
        spaceAfter=15,
        leading=18,
        fontName='Helvetica'
    )
    
    local_style = ParagraphStyle(
        'Local',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_RIGHT,
        spaceAfter=40,
        fontName='Helvetica'
    )
    
    assinatura_style = ParagraphStyle(
        'Assinatura',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    elements = []
    
    logo = build_logo_flowable(60)
    if logo:
        elements.append(logo)
        elements.append(Spacer(1, 6*mm))
    
    # Título
    elements.append(Paragraph("DECLARAÇÃO DE QUITAÇÃO", titulo_style))
    elements.append(Spacer(1, 20))
    
    # Montar texto do corpo
    emp = dados['empresaVendedora']
    rep = dados['representanteLegal']
    cliente = dados['cliente']
    lote = dados['lote']
    venda_data = dados['venda']
    
    texto = f"""
    A <b>{emp['razao_social']}</b>, com sede na {emp['endereco']}, {emp['bairro']}, 
    {emp['cidade']} - {emp['uf']}, Inscrita no CNPJ/MF sob o Nº {emp['cnpj']}, 
    neste ato representada por, <b>{rep['nome']}</b>, {rep['estado_civil']}, {rep['cargo']}, 
    portador da cédula de identidade RG Nº {rep['rg']} e inscrito no CPF/MF Nº {rep['cpf']} 
    domiciliado em {rep['domicilio']}, <b>DECLARA</b>, para os devidos fins de direito, 
    que O Sr(a). <b>{cliente['nome']}</b> portador CPF/CNPJ Nº <b>{cliente['cpfCnpj']}</b>, 
    promitente comprador do imóvel constituído pela unidade designada <b>QUADRA {lote['quadra']} LOTE {lote['lote']}</b> 
    do empreendimento denominado em "<b>{lote['nomeObra']}</b>", pagou integralmente as parcelas 
    do financiamento do preço de venda previstas no Instrumento Particular de Promessa de Venda e Compra 
    quitado em <b>{venda_data['ultimoRecebimento'] or 'data não informada'}</b>.
    """
    
    elements.append(Paragraph(texto, corpo_style))
    elements.append(Spacer(1, 30))
    
    # Local e data - usando cidade e UF configurados ou da obra
    cidade_obra = lote.get('cidadeObra', '') or 'Tomé-Açu'
    uf_obra = lote.get('ufObra', '') or 'PA'
    # Formatar cidade em title case (padrão normal) com espaço ao redor do hífen
    cidade_emissao = f"{cidade_obra.title()} - {uf_obra.upper()}" if uf_obra else cidade_obra.title()
    # Usar data_documento se fornecida, senão usar data atual
    data_emissao = format_date_extenso(data_documento if data_documento else datetime.now())
    elements.append(Paragraph(f"{cidade_emissao}, {data_emissao}.", local_style))
    
    elements.append(Spacer(1, 60))
    
    # Assinatura - com espaçamento maior entre linha e nome
    elements.append(Paragraph("________________________________________________", assinatura_style))
    elements.append(Spacer(1, 15))  # Espaço entre a linha e o nome
    elements.append(Paragraph(f"<b>{rep['nome']}</b>", assinatura_style))
    elements.append(Paragraph(rep['cargo'], assinatura_style))
    
    doc.build(elements, onFirstPage=make_header_footer, onLaterPages=make_header_footer)
    buffer.seek(0)
    
    filename = f"carta_quitacao_Q{lote['quadra']}_L{lote['lote']}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


@router.get("/quitacao/extrato")
async def gerar_extrato_quitacao(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    venda: Optional[int] = Query(None, description="Número da venda (opcional)"),
    quadra: Optional[str] = Query(None, description="Quadra do lote (opcional)"),
    lote: Optional[str] = Query(None, description="Lote (opcional)"),
    tipos: Optional[str] = Query(None, description="Tipos de parcela separados por vírgula (E,P,S,B,C,IN)"),
    matricula: Optional[str] = Query(None),
    folha: Optional[str] = Query(None),
    livro: Optional[str] = Query(None)
):
    """Gera PDF de Extrato Detalhado de Pagamentos para Quitação"""
    
    # Buscar dados
    try:
        dados = await get_dados_quitacao(empresa, obra, venda, quadra, lote)
    except HTTPException as e:
        raise e
    
    # Processar tipos de parcela
    tipos_parcela = ['E', 'P', 'S']  # Default
    if tipos:
        tipos_parcela = [t.strip().upper() for t in tipos.split(',') if t.strip()]
    
    # Calcular valor correto usando a função
    lote_data = dados['lote']
    quadra_str = lote_data.get('quadra', '').strip()
    lote_str = lote_data.get('lote', '').strip()
    
    valor_quitacao, total_pago, total_confirmado, ultimo_receb, historico_transf, parcelas_det = calcular_valor_quitacao(
        empresa, obra, quadra_str, lote_str, tipos_parcela
    )
    
    # CORREÇÃO: Usar o cliente da ÚLTIMA venda no histórico de transferências
    if historico_transf and len(historico_transf) > 0:
        ultimo_cliente_hist = historico_transf[-1]  # Último = cliente atual
        if ultimo_cliente_hist.get('cliente'):
            cliente_nome_hist = ultimo_cliente_hist.get('cliente', '')
            cliente_cpf_hist = ultimo_cliente_hist.get('cpf', '')
            cliente_cod_hist = ultimo_cliente_hist.get('codCliente')
            numero_venda_atual = ultimo_cliente_hist.get('numVenda')
            
            # Usar lógica do sistema: ISNULL com fallback para endereço da empresa vinculada
            if cliente_cod_hist:
                query_cliente_atual = f"""
                SELECT TOP 1 
                    P.Nome_pes as nome, P.cpf_pes as cpf, P.dtnasc_pes as dataNascimento,
                    ISNULL(PE.Endereco_pend, PEComercial.Endereco_pend) as endereco, 
                    ISNULL(PE.NumEnd_pend, PEComercial.NumEnd_pend) as numero, 
                    ISNULL(PE.Bairro_pend, PEComercial.Bairro_pend) as bairro,
                    ISNULL(PE.Cidade_pend, PEComercial.Cidade_pend) as cidade, 
                    ISNULL(PE.UF_pend, PEComercial.UF_pend) as uf, 
                    ISNULL(PE.CEP_pend, PEComercial.CEP_pend) as cep
                FROM Pessoas P WITH(NOLOCK)
                LEFT JOIN PesEndereco PE WITH(NOLOCK) 
                    ON P.cod_pes = PE.CodPes_pend AND PE.Tipo_pend = 0
                LEFT JOIN Pessoas PEmp WITH(NOLOCK) 
                    ON PE.CodEmp_pend = PEmp.cod_pes
                LEFT JOIN PesEndereco PEComercial WITH(NOLOCK) 
                    ON PEComercial.CodPes_pend = PEmp.cod_pes AND PEComercial.Tipo_pend = 0
                WHERE P.cod_pes = {cliente_cod_hist}
                """
                try:
                    cliente_result = execute_query(query_cliente_atual)
                    if cliente_result and cliente_result[0]:
                        cliente_data = cliente_result[0]
                        dados['cliente'] = {
                            'nome': cliente_data.get('nome', cliente_nome_hist) or cliente_nome_hist,
                            'cpfCnpj': format_cpf_cnpj(cliente_data.get('cpf', cliente_cpf_hist) or cliente_cpf_hist),
                            'dataNascimento': cliente_data.get('dataNascimento').strftime('%d/%m/%Y') if cliente_data.get('dataNascimento') else None,
                            'rg': cliente_data.get('rg', ''),
                            'endereco': cliente_data.get('endereco', ''),
                            'numero': cliente_data.get('numero', ''),
                            'bairro': cliente_data.get('bairro', ''),
                            'cidade': cliente_data.get('cidade', ''),
                            'uf': cliente_data.get('uf', ''),
                            'cep': cliente_data.get('cep', '')
                        }
                        if numero_venda_atual:
                            dados['venda']['numero'] = numero_venda_atual
                except Exception as e:
                    print(f"Erro ao buscar cliente atual (extrato): {e}")
                    dados['cliente']['nome'] = cliente_nome_hist
                    dados['cliente']['cpfCnpj'] = format_cpf_cnpj(cliente_cpf_hist)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=25*mm,  # Muito reduzido para logo pequena
        bottomMargin=15*mm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos profissionais
    titulo_style = ParagraphStyle(
        'Titulo', parent=styles['Heading1'], fontSize=14, alignment=TA_CENTER,
        spaceAfter=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#1F2937')
    )
    
    secao_style = ParagraphStyle(
        'Secao', parent=styles['Heading2'], fontSize=10, alignment=TA_LEFT,
        spaceAfter=6, spaceBefore=10, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1F2937')
    )
    
    info_style = ParagraphStyle(
        'Info', parent=styles['Normal'], fontSize=9, alignment=TA_LEFT,
        spaceAfter=2, fontName='Helvetica', leading=12
    )
    
    nota_style = ParagraphStyle(
        'Nota', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER,
        spaceAfter=4, fontName='Helvetica-Oblique', textColor=colors.HexColor('#6B7280')
    )
    
    elements = []
    
    cliente = dados['cliente']
    lote_info = dados['lote']
    venda_data = dados['venda']
    
    # ====== CABEÇALHO ======
    elements.append(Paragraph("EXTRATO DE PAGAMENTOS PARA QUITAÇÃO", titulo_style))
    
    # Box de informações do lote - layout compacto (3 colunas)
    info_data = [
        [Paragraph("<b>QUADRA / LOTE</b>", info_style), 
         Paragraph("<b>CLIENTE ATUAL</b>", info_style),
         Paragraph("<b>Nº VENDA</b>", info_style)],
        [Paragraph(f"{lote_info['quadra']} / {lote_info['lote']}", info_style),
         Paragraph(f"{(cliente['nome'] or '-')[:35]}", info_style),
         Paragraph(f"{venda_data['numero']}", info_style)],
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 9*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3F4F6')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    
    # Obra e Tipos em tabela compacta lado a lado
    nome_obra = lote_info.get('nomeObra', '') or '-'
    tipos_list = [f"{t}" for t in tipos_parcela]
    
    info2_data = [
        [Paragraph("<b>OBRA</b>", info_style), Paragraph("<b>TIPOS DE PARCELA</b>", info_style)],
        [Paragraph(nome_obra, info_style), Paragraph(' | '.join(tipos_list), info_style)],
    ]
    
    info2_table = Table(info2_data, colWidths=[10*cm, 8*cm])
    info2_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E5E7EB')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(info2_table)
    elements.append(Spacer(1, 4))
    
    # ====== DETALHAMENTO POR CLIENTE ======
    elements.append(Paragraph("HISTÓRICO DE PAGAMENTOS POR PROPRIETÁRIO", secao_style))
    
    total_geral_menor = 0
    
    for idx, hist in enumerate(historico_transf):
        num_venda_cliente = hist.get('numVenda')
        cliente_nome = (hist.get('cliente', 'N/A') or 'N/A')
        
        parcelas_cliente = [p for p in parcelas_det if p.get('numVenda') == num_venda_cliente]
        
        subtotal_menor = sum(p.get('valorMenor', 0) for p in parcelas_cliente)
        total_geral_menor += subtotal_menor
        
        # Cabeçalho do proprietário
        header_style = ParagraphStyle(
            'ClienteHeader', parent=info_style, fontSize=9, 
            fontName='Helvetica-Bold', backColor=colors.HexColor('#E5E7EB'),
            spaceBefore=8, spaceAfter=4
        )
        cliente_header = f"{idx + 1}. {cliente_nome} | Venda: {num_venda_cliente} | Subtotal: {format_currency(subtotal_menor)}"
        elements.append(Paragraph(cliente_header, header_style))
        
        if parcelas_cliente:
            # Tabela de pagamentos (sem coluna proprietário)
            table_data = [["TIPO", "PARC.", "DATA", "VAL. PAGO", "VAL. CONFIRM.", "MENOR"]]
            
            for p in parcelas_cliente:
                # Formatar data para padrão brasileiro dd/mm/yyyy
                data_receb = p.get('dataRecebimento', '-') or '-'
                if data_receb and data_receb != '-' and len(data_receb) >= 10:
                    try:
                        partes = data_receb[:10].split('-')
                        if len(partes) == 3:
                            data_receb = f"{partes[2]}/{partes[1]}/{partes[0]}"
                    except:
                        pass
                
                table_data.append([
                    p.get('tipo', '-'),
                    str(p.get('parcela', '-')),
                    data_receb,
                    format_currency(p.get('valorPago', 0)),
                    format_currency(p.get('valorConfirmado', 0)),
                    format_currency(p.get('valorMenor', 0))
                ])
            
            table = Table(table_data, colWidths=[1.8*cm, 1.5*cm, 2.5*cm, 3.8*cm, 3.8*cm, 3.8*cm])
            table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Corpo
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 1), (2, -1), 'CENTER'),
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
                ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("<i>Sem pagamentos registrados.</i>", nota_style))
    
    # ====== RESUMO FINAL ======
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("RESUMO PARA QUITAÇÃO", secao_style))
    
    resumo_data = [
        ["TOTAL PAGO", "TOTAL CONFIRMADO", "DIFERENÇA", "VALOR P/ QUITAÇÃO"],
        [format_currency(total_pago), format_currency(total_confirmado), 
         format_currency(total_pago - total_confirmado), format_currency(valor_quitacao)],
    ]
    
    resumo_table = Table(resumo_data, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
    resumo_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        
        # Valores
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 11),
        ('BACKGROUND', (0, 1), (2, 1), colors.HexColor('#F9FAFB')),
        ('BACKGROUND', (-1, 1), (-1, 1), colors.HexColor('#059669')),
        ('TEXTCOLOR', (-1, 1), (-1, 1), colors.white),
        
        # Grid e alinhamento
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#9CA3AF')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(resumo_table)
    
    # Nota explicativa
    elements.append(Spacer(1, 12))
    nota = "O valor para quitação é calculado somando o MENOR valor entre 'Valor Pago' e 'Valor Confirmado' de cada parcela."
    elements.append(Paragraph(nota, nota_style))
    
    data_emissao = datetime.now().strftime('%d/%m/%Y às %H:%M')
    elements.append(Paragraph(f"Documento gerado em: {data_emissao}", nota_style))
    
    doc.build(elements, onFirstPage=make_header_footer, onLaterPages=make_header_footer)
    buffer.seek(0)
    
    filename = f"extrato_quitacao_Q{quadra_str}_L{lote_str}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )
def get_estado_civil_label(codigo):
    """Mapeia código numérico do UAU para label em string"""
    mapping = {
        1: "SOLTEIRO(A)",
        2: "CASADO(A)",
        3: "DIVORCIADO(A)",
        4: "VIÚVO(A)",
        5: "SEPARADO(A)",
        6: "UNIÃO ESTÁVEL"
    }
    return mapping.get(codigo, "SOLTEIRO(A)")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Desenha "Pag.: X / Y"
        self.saveState()
        self.setFont("Helvetica", 9)
        self.drawRightString(200*mm, 5*mm, f"Pag.: {self._pageNumber} / {page_count}")
        self.restoreState()

# Função de header/footer simplificada para usar com o NumberedCanvas
def make_header_footer_termo(canvas, doc):
    """Header/footer específico para o Termo de Quitação"""
    canvas.saveState()
    
    # Logo centralizada - posicionada um pouco mais abaixo
    try:
        # Caminho robusto: backend/assets/logoazulvalle.png
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logoazulvalle.png')
        if os.path.exists(logo_path):
            from reportlab.lib.utils import ImageReader
            img = ImageReader(logo_path)
            iw, ih = img.getSize()
            aspect = ih / float(iw)
            logo_width = 30*mm
            logo_height = logo_width * aspect
            page_width = A4[0]
            x_pos = (page_width - logo_width) / 2
            y_pos = A4[1] - 28*mm - logo_height
            canvas.drawImage(logo_path, x_pos, y_pos, width=logo_width, height=logo_height, mask='auto')
    except:
        pass
    
    # Rodapé - site centralizado
    canvas.setFillColor(colors.HexColor('#6B7280'))
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(A4[0] / 2, 7*mm, "www.valleprime.com.br")
        
    canvas.restoreState()


@router.get("/quitacao/termo")
async def gerar_termo_quitacao(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    venda: Optional[int] = Query(None, description="Número da venda (opcional)"),
    quadra: Optional[str] = Query(None, description="Quadra do lote (opcional)"),
    lote: Optional[str] = Query(None, description="Lote (opcional)"),
    cidade: Optional[str] = Query(None, description="Cidade para o documento (opcional)"),
    uf: Optional[str] = Query(None, description="UF para o documento (opcional)"),
    data: Optional[str] = Query(None, description="Data do documento YYYY-MM-DD (opcional)"),
    tipos: Optional[str] = Query(None, description="Tipos de parcela separados por vírgula (E,P,S,B,C,IN)"),
    formato: Optional[str] = Query('pdf', description="Formato do documento: pdf ou docx"),
    matricula: Optional[str] = Query(None),
    folha: Optional[str] = Query(None),
    livro: Optional[str] = Query(None)
):
    """Gera PDF ou DOCX do Termo de Quitação e Autorização para Escritura com cálculo correto de valor"""
    
    # Buscar dados
    try:
        dados = await get_dados_quitacao(empresa, obra, venda, quadra, lote)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not dados:
        raise HTTPException(status_code=404, detail="Dados não encontrados")

    # Sobrescrever cidade/uf se fornecidos
    if cidade:
        dados['lote']['cidadeObra'] = cidade
    if uf:
        dados['lote']['ufObra'] = uf
    
    # Processar data
    data_documento = None
    if data:
        try:
            data_documento = datetime.strptime(data, '%Y-%m-%d')
        except:
            pass

    # Inicializar tipos_parcela se não fornecido
    tipos_parcela = ['E', 'P', 'S']
    if tipos:
        tipos_parcela = [t.strip().upper() for t in tipos.split(',') if t.strip()]
    
    # Calcular valor correto usando a nova função
    lote_data = dados['lote']
    quadra_str = lote_data.get('quadra', '').strip()
    lote_str = lote_data.get('lote', '').strip()
    
    valor_quitacao, total_pago, total_confirmado, ultimo_receb, historico_transf, parcelas_det = calcular_valor_quitacao(
        empresa, obra, quadra_str, lote_str, tipos_parcela
    )
    
    # Sempre usar o valor calculado (soma de MIN(ValParcPaga, VlConfirm) de todas as vendas da cadeia)
    # IMPORTANTE: dados['venda']['valor'] é usado no PDF, não lote_data['valor']
    dados['venda']['valor'] = valor_quitacao
    dados['venda']['totalPago'] = total_pago
    dados['venda']['totalConfirmado'] = total_confirmado
    if ultimo_receb:
        dados['venda']['ultimoRecebimento'] = ultimo_receb
    
    # Adicionar histórico de transferências ao dados
    dados['historicoTransferencias'] = historico_transf
    dados['tiposParcelaSelecionados'] = tipos_parcela
    
    # CORREÇÃO: Usar o cliente da ÚLTIMA venda no histórico de transferências
    # O último elemento é o cliente ATUAL do lote
    if historico_transf and len(historico_transf) > 0:
        ultimo_cliente_hist = historico_transf[-1]  # Último = cliente atual
        if ultimo_cliente_hist.get('cliente'):
            # Buscar dados completos do cliente atual
            cliente_nome_hist = ultimo_cliente_hist.get('cliente', '')
            cliente_cpf_hist = ultimo_cliente_hist.get('cpf', '')
            cliente_cod_hist = ultimo_cliente_hist.get('codCliente')
            numero_venda_atual = ultimo_cliente_hist.get('numVenda')
            
            # Query para buscar dados completos do cliente (endereço, etc.)
            # Seguindo EXATAMENTE a estrutura SQL do sistema
            if cliente_cod_hist:
                query_cliente_atual = f"""
                SELECT TOP 1 
                    P.Nome_pes as nome, 
                    P.cpf_pes as cpf, 
                    P.dtnasc_pes as dataNascimento,
                    ISNULL(PE.Endereco_pend, PEComercial.Endereco_pend) as endereco,
                    ISNULL(PE.NumEnd_pend, PEComercial.NumEnd_pend) as numero,
                    ISNULL(PE.Bairro_pend, PEComercial.Bairro_pend) as bairro,
                    ISNULL(PE.Cidade_pend, PEComercial.Cidade_pend) as cidade,
                    ISNULL(PE.UF_pend, PEComercial.UF_pend) as uf,
                    ISNULL(PE.CEP_pend, PEComercial.CEP_pend) as cep,
                    PD.Registro_Doc as rg,
                    PD.OrgaoEmissor_Doc as orgaoExpedidor,
                    PD.UF_Doc as ufRg,
                    PF.estciv_pf as estadoCivil,
                    PF.RegCasamento_pf as regimeCasamento
                FROM Pessoas P WITH(NOLOCK)
                LEFT JOIN PesFis PF WITH(NOLOCK)
                    ON P.cod_pes = PF.cod_pf
                LEFT JOIN PessoasDoc PD WITH(NOLOCK)
                    ON P.cod_pes = PD.CodPes_Doc AND PD.Tipo_Doc = 1
                LEFT JOIN PesEndereco PE WITH(NOLOCK) 
                    ON PE.CodPes_pend = P.cod_pes AND PE.Tipo_pend = 0
                LEFT JOIN Pessoas PEmpresa WITH(NOLOCK) 
                    ON PEmpresa.cod_pes = PE.CodEmp_pend
                LEFT JOIN PesEndereco PEComercial WITH(NOLOCK) 
                    ON PEComercial.CodPes_pend = PEmpresa.cod_pes AND PEComercial.Tipo_pend = 0
                WHERE P.cod_pes = {cliente_cod_hist}
                """
                
                
                try:
                    cliente_result = execute_query(query_cliente_atual)
                    if cliente_result and cliente_result[0]:
                        cliente_data = cliente_result[0]
                        dados['cliente'] = {
                            'nome': cliente_data.get('nome', cliente_nome_hist) or cliente_nome_hist,
                            'cpfCnpj': format_cpf_cnpj(cliente_data.get('cpf', cliente_cpf_hist) or cliente_cpf_hist),
                            'dataNascimento': cliente_data.get('dataNascimento').strftime('%d/%m/%Y') if cliente_data.get('dataNascimento') else None,
                            'rg': cliente_data.get('rg', ''),
                            'orgaoExpedidor': cliente_data.get('orgaoExpedidor', ''),
                            'ufRg': cliente_data.get('ufRg', ''),
                            'endereco': cliente_data.get('endereco', ''),
                            'numero': cliente_data.get('numero', ''),
                            'bairro': cliente_data.get('bairro', ''),
                            'cidade': cliente_data.get('cidade', ''),
                            'uf': cliente_data.get('uf', ''),
                            'cep': cliente_data.get('cep', ''),
                            'estadoCivil': get_estado_civil_label(cliente_data.get('estadoCivil')),
                            'regimeCasamento': get_regime_casamento_label(cliente_data.get('regimeCasamento'))
                        }
                        # Atualizar número da venda também
                        if numero_venda_atual:
                            dados['venda']['numero'] = numero_venda_atual
                except Exception as e:
                    print(f"Erro ao buscar cliente atual: {e}")
                    # Fallback: usar apenas nome e cpf do histórico
                    dados['cliente']['nome'] = cliente_nome_hist
                    dados['cliente']['cpfCnpj'] = format_cpf_cnpj(cliente_cpf_hist)
                    
    # USAR DIRETAMENTE O venda DA ARGUMENTAÇÃO OU DO OBJETO dados
    numero_venda_atual = venda if venda else (dados.get('venda', {}).get('numero') if dados.get('venda') else None)
    todos_clientes = []
    if numero_venda_atual:
        todos_clientes = get_clientes_venda(empresa, obra, numero_venda_atual)
    
    # Se não encontrar via VendaClientes, usar o cliente do histórico (fallback)
    if not todos_clientes:
        todos_clientes = [dados['cliente']]
        
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=15*mm,
        topMargin=25*mm,
        bottomMargin=15*mm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos - Fonte Helvetica (Arial), tamanho 12, espaçamentos compactos
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=12,
        alignment=TA_CENTER,  # Centralizado
        spaceAfter=4,
        spaceBefore=0,
        fontName='Helvetica-Bold',
        leading=14,
        borderWidth=1,
        borderColor=colors.black,
        borderPadding=4
    )
    
    secao_style = ParagraphStyle(
        'Secao',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=8,
        spaceBefore=18,  # Mais espaço antes dos tópicos para distribuir bem
        fontName='Helvetica-Bold',
        leading=15,
        borderWidth=1,
        borderColor=colors.black,
        borderPadding=3
    )
    
    corpo_style = ParagraphStyle(
        'Corpo',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        spaceBefore=12, # Mais espaço antes do texto para distribuir bem
        leading=18,  # Mais espaçamento entre linhas
        fontName='Helvetica',
        firstLineIndent=0
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=14
    )
    
    assinatura_style = ParagraphStyle(
        'Assinatura',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=14
    )
    
    assinatura_esquerda_style = ParagraphStyle(
        'AssinaturaEsquerda',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=14
    )
    
    label_direita_style = ParagraphStyle(
        'LabelDireita',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_RIGHT,
        fontName='Helvetica',
        leading=14
    )
    
    # Estilo compacto para itens de tabela com quebra de linha automática
    tabela_item_style = ParagraphStyle(
        'TabelaItem',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=12
    )
    
    elements = []
    
    # Remover logo do fluxo - usar make_header_footer padrão
    # logo = build_logo_flowable(60)
    # if logo:
    #     elements.append(logo)
    #     elements.append(Spacer(1, 6*mm))
    
    emp = dados['empresaVendedora']
    cliente = dados['cliente']
    lote = dados['lote']
    venda_data = dados['venda']
    
    # Padronizar cidade: Sempre usar TOMÉ-AÇU - PA se for a cidade alvo ou CEP específico
    cidade_obra = normalize_city_name(lote.get('cidadeObra'), lote.get('cep'))
    lote['cidadeObra'] = cidade_obra
    
    # Título em MAIÚSCULAS
    titulo = f"TERMO DE QUITAÇÃO E AUTORIZAÇÃO PARA ESCRITURA CONTRATO PARTICULAR N° {venda_data['numero']} DE COMPROMISSO DE COMPRA E VENDA DE LOTE/TERRENO"
    elements.append(Paragraph(titulo.upper(), titulo_style))
    
    elements.append(Spacer(1, 4*mm)) # Espaço após título (reduzido)
    
    # OBJETO DA QUITAÇÃO
    elements.append(Paragraph("OBJETO DA QUITAÇÃO E AUTORIZAÇÃO DA ESCRITURA", secao_style))
    
    objeto = f"""
    LOTE/TERRENO N° <b>{lote.get('lote')}</b>, DA QUADRA N° <b>{lote.get('quadra')}</b>, DO <b>{(lote.get('nomeObra') or '').upper()}</b> 
    NO MUNICÍPIO DE <b>{(lote.get('cidadeObra') or '').upper()} - {(lote.get('ufObra') or '').upper()}</b>.
    """
    elements.append(Paragraph(objeto.upper(), corpo_style))
    
    # Parágrafo de Registro
    # Parágrafo de Registro - Garantir UPPERCASE
    mat_str = (matricula or '_________').upper()
    folha_str = (folha or '_________').upper()
    livro_str = (livro or '_________').upper()
    
    texto_registro = f"""
    REGISTRADO NA MATRÍCULA Nº {mat_str}, FOLHA: {folha_str}, LIVRO {livro_str}. 
    DO CARTÓRIO DE REGISTRO DE IMÓVEIS DA COMARCA DE {(lote['cidadeObra'].upper() if lote.get('cidadeObra') else '_________')} - {(lote['ufObra'].upper() if lote.get('ufObra') else '___')}.
    """
    elements.append(Paragraph(texto_registro.strip(), corpo_style))
    
    # Tabela de dimensões - compacta, fonte 11pt
    dim_data = [
        ["LOCALIZAÇÃO:", (lote.get('logradouro', '') or '-').upper()],
        ["ÁREA:", f"{lote.get('area', 0) or 0:.2f} M²"],
        ["FRENTE:", f"{lote.get('frente', '') or '-'} M"],
        ["FUNDO:", f"{lote.get('fundo', '') or '-'} M"],
        ["LADO DIREITO:", f"{lote.get('ladoDireito', '') or '-'} M"],
        ["LADO ESQUERDO:", f"{lote.get('ladoEsquerdo', '') or '-'} M"],
        ["CHANFRADO:", f"{lote.get('chanfro', '') or '0,00'} M"],
    ]
    
    dim_table = Table(dim_data, colWidths=[4*cm, 10*cm])
    dim_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
    ]))
    elements.append(dim_table)
    
    # VENDEDORA
    elements.append(Paragraph("VENDEDORA", secao_style))
    vendedora_texto = f"""
    <b>{emp['razao_social'].upper()}</b>, INSCRITA NO CNPJ/MF SOB N° <b>{emp['cnpj']}</b>, SEDIADA NA {emp['endereco'].upper() if emp.get('endereco') else '-'}, 
    BAIRRO: {emp['bairro'].upper() if emp.get('bairro') else '-'}, {emp['cidade'].upper() if emp.get('cidade') else '-'} - {emp['uf'].upper() if emp.get('uf') else '-'}, CEP.: {emp['cep']}.
    """
    elements.append(Paragraph(vendedora_texto, corpo_style))
    
    # COMPRADOR(ES) - Buscar todos os co-proprietários da venda atual
    elements.append(Paragraph("COMPRADOR(ES)", secao_style))
    
    # USAR DIRETAMENTE O venda DA ARGUMENTAÇÃO OU DO OBJETO dados (MAIS ROBUSTO)
    # (Obtenção de todos_clientes já foi feita antes da separação PDF/DOCX)
    
    # Iterar sobre todos os compradores
    num_clientes = len(todos_clientes)
    for idx, cli in enumerate(todos_clientes):
        # Adicionar rótulo: COMPRADOR: se for um só, ou Xº PROPONENTE: se for mais de um
        # Adicionar rótulo: Xº PROPONENTE: apenas se for mais de um. Se for um só, pula (já tem o COMPRADOR(ES) acima)
        if num_clientes > 1:
            label_texto = f"<b>{idx + 1}º PROPONENTE:</b>"
            elements.append(Paragraph(label_texto, secao_style))
        
        cpf_cnpj = cli.get('cpfCnpj', '')
        cpf_cnpj_limpo = ''.join(filter(str.isdigit, cpf_cnpj)) if cpf_cnpj else ''
        
        # Verifica se é CNPJ (mais de 11 dígitos ou contém '/')
        is_cnpj = len(cpf_cnpj_limpo) > 11 or '/' in (cpf_cnpj or '')
        
        cli_nome = cli.get('nome', 'NÃO INFORMADO')
        cli_endereco = cli.get('endereco', '-')
        cli_bairro = cli.get('bairro', '-')
        cli_cidade = normalize_city_name(cli.get('cidade', '-'), cli.get('cep'))
        cli_uf = cli.get('uf', 'PA')
        cli_numero = cli.get('numero', 'S/N')
        
        if is_cnpj:
            # Pessoa Jurídica
            comprador_texto = f"""
            <b>{cli_nome}</b>, INSCRITA NO CNPJ/MF SOB N° <b>{cli.get('cpfCnpj', '-')}</b>, 
            SEDIADA NA {cli_endereco}, {cli_numero}, 
            BAIRRO: {cli_bairro}, {cli_cidade} - {cli_uf}, 
            CEP.: {cli.get('cep', '-')}.
            """
        else:
            # Pessoa Física
            regime = cli.get('regimeCasamento')
            regime_text = f", PELO REGIME DE {regime}" if regime else ""
            
            comprador_texto = f"""
            <b>{cli_nome}</b>, BRASILEIRO(A), {cli.get('estadoCivil', 'SOLTEIRO(A)')}{regime_text}, CI N° {cli.get('rg', '-')} {str(cli.get('orgaoExpedidor', '-') or '').upper()}/{str(cli.get('ufRg', '') or '').upper()}, 
            E CPF N° <b>{cli.get('cpfCnpj', '-')}</b>, NASCIDO(A) AOS {cli.get('dataNascimento', '-')}{" EM " + (cli.get('cidadeNascimento') or '').upper() + (" - " + (cli.get('ufNascimento') or '').upper() if cli.get('ufNascimento') else "") if (cli.get('cidadeNascimento') or cli.get('ufNascimento')) else ""}, 
            RESIDENTE E DOMICILIADO NA {cli_endereco}, {cli_numero}, 
            {cli_bairro}, {cli_cidade} - {cli_uf}.
            """
        elements.append(Paragraph(comprador_texto.upper(), corpo_style))

    
    # HISTÓRICO DE TRANSFERÊNCIAS (se houver mais de uma venda)
    historico = dados.get('historicoTransferencias', [])
    if len(historico) > 1:
        elements.append(Paragraph("HISTÓRICO DE TRANSFERÊNCIAS DO LOTE", secao_style))
        
        historico_intro = """
        O LOTE/TERRENO OBJETO DESTE TERMO TEVE AS SEGUINTES TRANSFERÊNCIAS ANTERIORES, 
        CUJOS PAGAMENTOS FORAM INTEGRALIZADOS E CONSIDERADOS PARA A QUITAÇÃO TOTAL:
        """
        elements.append(Paragraph(historico_intro, corpo_style))
        
        # Verificar se alguma venda tem múltiplos proprietários
        tem_multiplos_owners = any(len(h.get('owners', [])) > 1 for h in historico)
        
        # Definir cabeçalhos e larguras de coluna baseado na necessidade de % PARTICIPAÇÃO
        if tem_multiplos_owners:
            hist_headers = ["Nº VENDA", "CLIENTE", "% PARTICIP.", "DESCRIÇÃO", "VALOR PAGO"]
            col_widths = [1.8*cm, 6.5*cm, 2.3*cm, 3*cm, 3*cm]
        else:
            hist_headers = ["Nº VENDA", "CLIENTE", "DESCRIÇÃO", "VALOR PAGO"]
            col_widths = [2.5*cm, 7*cm, 4*cm, 3*cm]
        
        hist_data = [hist_headers]
        
        total_items = len(historico)
        row_index = 1  # Começar após o cabeçalho
        span_commands = []  # Lista para armazenar comandos de SPAN
        
        for idx, h in enumerate(historico):
            # Definir descrição com base na posição (ordem sequencial)
            if idx == total_items - 1:
                descricao = "CLIENTE ATUAL"
            else:
                numero_ordem = idx + 1
                descricao = f"{numero_ordem}° CLIENTE"
            
            owners = h.get('owners', [])
            num_venda = str(h.get('numVenda', '-'))
            valor_pago = format_currency(h.get('valorPago', 0))
            
            if tem_multiplos_owners:
                if len(owners) > 1:
                    # Múltiplos proprietários: mesclar células de Nº Venda, Descrição e Valor
                    num_rows = len(owners)
                    
                    # Verificar se todas as porcentagens são iguais para decidir se mescla
                    all_percentages_equal = len(set(o.get('participacao', 0) for o in owners)) == 1
                    
                    # Adicionar todas as linhas dos proprietários
                    for owner_idx, owner in enumerate(owners):
                        pct_str = f"{owner['participacao']:.0f}%"
                        
                        if owner_idx == 0:
                            # Primeira linha: incluir todos os dados
                            hist_data.append([
                                num_venda,
                                Paragraph(owner['nome'], tabela_item_style),
                                pct_str,
                                descricao,
                                valor_pago
                            ])
                        else:
                            # Linhas subsequentes
                            # Se porcentagens iguais, deixa vazio (será mesclado). Se diferentes, mostra valor.
                            current_pct = "" if all_percentages_equal else pct_str
                            
                            hist_data.append([
                                "",  # Será mesclado
                                Paragraph(owner['nome'], tabela_item_style),
                                current_pct,
                                "",  # Será mesclado
                                ""   # Será mesclado
                            ])
                    
                    # Adicionar comandos de SPAN para mesclar células
                    # SPAN(col, row_start, col, row_end)
                    span_commands.append(('SPAN', (0, row_index), (0, row_index + num_rows - 1)))  # Nº VENDA
                    span_commands.append(('SPAN', (3, row_index), (3, row_index + num_rows - 1)))  # DESCRIÇÃO
                    span_commands.append(('SPAN', (4, row_index), (4, row_index + num_rows - 1)))  # VALOR PAGO
                    
                    if all_percentages_equal:
                         span_commands.append(('SPAN', (2, row_index), (2, row_index + num_rows - 1)))  # % PARTICIP.
                    
                    row_index += num_rows
                else:
                    # Proprietário único
                    cliente_nome = (h.get('cliente', 'N/A') or 'N/A').upper()
                    participacao = f"{owners[0]['participacao']:.0f}%" if owners and owners[0]['participacao'] > 0 else "100%"
                    hist_data.append([
                        num_venda,
                        Paragraph(cliente_nome, tabela_item_style),
                        participacao,
                        descricao,
                        valor_pago
                    ])
                    row_index += 1
            else:
                # Sem coluna de porcentagem
                cliente_nome = (h.get('cliente', 'N/A') or 'N/A').upper()
                hist_data.append([
                    num_venda,
                    Paragraph(cliente_nome, tabela_item_style),
                    descricao,
                    valor_pago
                ])
                row_index += 1
        
        # Criar tabela com larguras dinâmicas
        hist_table = Table(hist_data, colWidths=col_widths)
        
        # Estilos da tabela
        if tem_multiplos_owners:
            table_style = [
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E5E7EB')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Headers
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Nº VENDA
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # % PARTICIP.
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # DESCRIÇÃO
                ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # VALOR PAGO
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]
            # Adicionar comandos de SPAN
            table_style.extend(span_commands)
        else:
            table_style = [
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E5E7EB')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Headers
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Nº VENDA
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # DESCRIÇÃO
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # VALOR PAGO
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]
        
        hist_table.setStyle(TableStyle(table_style))
        elements.append(hist_table)
        elements.append(Spacer(1, 10))
    
    # DA AUTORIZAÇÃO PARA ESCRITURA
    elements.append(Paragraph("DA AUTORIZAÇÃO PARA ESCRITURA", secao_style))
    autorizacao = f"""
    A VENDEDORA DECLARA QUE TODAS AS OBRIGAÇÕES CONTRATUAIS DO COMPRADOR ESTÃO QUITADAS E, POR ISSO, 
    AUTORIZA O CARTÓRIO DE REGISTRO DE IMÓVEIS DA COMARCA DE {lote['cidadeObra']} - {lote['ufObra']}, 
    A LAVRAR ESCRITURA PÚBLICA DE COMPRA E VENDA DO IMÓVEL IDENTIFICADO NO PREÂMBULO EM FAVOR DO 
    COMPRADOR ACIMA QUALIFICADO.
    """
    elements.append(Paragraph(autorizacao.upper(), corpo_style))
    
    # DO PREÇO
    elements.append(Paragraph("DO PREÇO", secao_style))
    # Formatar data do último recebimento
    ultimo_receb_raw = venda_data.get('ultimoRecebimento')
    ultimo_receb_str = '-'
    if ultimo_receb_raw:
        try:
            # Tenta converter se for string ISO ou datetime
            if hasattr(ultimo_receb_raw, 'strftime'):
                 ultimo_receb_str = ultimo_receb_raw.strftime('%d/%m/%Y')
            else:
                dt = datetime.fromisoformat(str(ultimo_receb_raw).replace('Z', ''))
                ultimo_receb_str = dt.strftime('%d/%m/%Y')
        except:
             ultimo_receb_str = str(ultimo_receb_raw)[:10]

    preco = f"""
    O VALOR DO LOTE/TERRENO É DE <b>{format_currency(venda_data['valor'])}</b>, QUE JÁ FOI QUITADO 
    PERANTE A VENDEDORA EM <b>{ultimo_receb_str}</b>.
    """
    elements.append(Paragraph(preco.upper(), corpo_style))
    
    # DA VALIDADE
    elements.append(Paragraph("DA VALIDADE", secao_style))
    validade = """
    A PRESENTE AUTORIZAÇÃO TERÁ VALIDADE DE 120 (CENTO E VINTE) DIAS, A CONTAR DA DATA DE SUA EMISSÃO.
    """
    elements.append(Paragraph(validade, corpo_style))
    
    # Fechamento
    elements.append(Paragraph(
        "POR SER EXPRESSÃO DA VERDADE, FIRMAMOS A PRESENTE EM 03 (TRÊS) VIAS DE IGUAL TEOR E FORMA.",
        corpo_style
    ))
    
    # Local e data - dd/mm/yyyy sem hora, alinhado à direita
    elements.append(Spacer(1, 10))
    data_para_usar = data_documento if data_documento else datetime.now()
    
    meses_upper = {
        1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL', 5: 'MAIO', 6: 'JUNHO',
        7: 'JULHO', 8: 'AGOSTO', 9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
    }
    
    mes_nome = meses_upper.get(data_para_usar.month, '')
    
    # CIDADE-UF, dia DE MÊS DE ano. Tudo em MAIÚSCULO
    # Normalizar o local também
    local_nome = normalize_city_name(lote.get('cidadeObra'), lote.get('cep'))
    local_data = f"{local_nome} - {lote['ufObra'].upper() if lote.get('ufObra') else 'PA'}, {data_para_usar.day} DE {mes_nome} DE {data_para_usar.year}."
    elements.append(Paragraph(local_data, label_direita_style))
    
    # Assinaturas - com espaço reduzido para aproveitar melhor o papel
    elements.append(Spacer(1, 25))
    
    # Vendedora - Linha maior
    elements.append(Paragraph("__________________________________________________________________", assinatura_style))
    elements.append(Paragraph(f"<b>{emp['razao_social'].upper()}</b>", assinatura_style))
    
    elements.append(Spacer(1, 25))
    
    elements.append(Spacer(1, 25))
    
    # Compradores - Iterar sobre todos os proponentes para as assinaturas
    for idx, cli in enumerate(todos_clientes):
        cli_nome = cli.get('nome', '').upper()
        # Calcular tamanho da linha
        len_line = max(43, int(len(cli_nome) * 1.3))
        line_str = "_" * len_line
        
        elements.append(Paragraph(line_str, assinatura_esquerda_style))
        elements.append(Paragraph(f"<b>{cli_nome}</b>", assinatura_esquerda_style))
        
        if num_clientes > 1:
            elements.append(Paragraph(f"{idx + 1}º PROPONENTE", assinatura_esquerda_style))
        
        # Cônjuge - Apenas se NÃO for PJ e se for CASADO
        # (Nota: O sistema UAU geralmente já traz o cônjuge como proponente se ele estiver na venda)
        # Se estivermos com Tipo_CVen 1 (Cônjuge), ele já foi impresso na assinatura acima
        
        elements.append(Spacer(1, 20))
    
    elements.append(Spacer(1, 20))
    
    # Testemunhas - Duas colunas com espaço no meio
    elements.append(Paragraph("<b>TESTEMUNHAS:</b>", label_style))
    elements.append(Spacer(1, 60))
    
    # Tabela com 3 colunas: Testemunha 1 | Espaço | Testemunha 2
    testemunhas_data = [
        ["_____________________________", "", "_____________________________"],
        ["NOME:", "", "NOME:"],
        ["CPF:", "", "CPF:"]
    ]
    
    # Ajustando larguras: 7cm texto, 2cm espaço, 7cm texto
    test_table = Table(testemunhas_data, colWidths=[7*cm, 3*cm, 7*cm], hAlign='LEFT')
    test_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Testemunha 1 esquerda
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),  # Testemunha 2 esquerda (no bloco dela)
        ('LEFTPADDING', (0, 0), (-1, -1), 0), # Remove padding da esquerda
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(test_table)
    
    # Usar o mesmo header/footer da Carta que está funcionando
    doc.build(elements, onFirstPage=make_header_footer, onLaterPages=make_header_footer)
    buffer.seek(0)
    
    if formato == 'docx':
        from routes.docx_builder import gerar_docx_termo_quitacao
        docx_buffer = gerar_docx_termo_quitacao(
            dados=dados, 
            empresa=emp, 
            form_data=vars(Query) if hasattr(Query, 'data') else {'data': data_documento.strftime('%Y-%m-%d') if data_documento else None}, 
            lote=lote
        )
        
        filename = f"termo_quitacao_Q{lote.get('quadra', '')}_L{lote.get('lote', '')}_{datetime.now().strftime('%Y%m%d')}.docx"
        return StreamingResponse(
            docx_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
        )
    else:
        filename = f"termo_quitacao_Q{lote.get('quadra', '')}_L{lote.get('lote', '')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
