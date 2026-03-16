"""
Sistema de Consulta/Valor para Quitação
Desenvolvido por: Vinicius Dev

Sistema para consulta e geração de relatórios de valores para usar no termo de quitação de vendas.
Conecta-se ao banco de dados SQL Server para buscar informações de parcelas pagas
e gera relatórios otimizados para impressão em papel A4.

Versão: 2.1
Data: 2025
Melhorias: Validações aprimoradas, logs de auditoria, exportação Excel, dark mode
"""

import streamlit as st
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import os
from io import BytesIO
import base64
import logging
import json
import traceback

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sistema_vendas.log'),
        logging.StreamHandler()
    ]
)

# Configuração da página
st.set_page_config(
    page_title="Sistema de Consulta/Quitação",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tema personalizado e assinatura do desenvolvedor
st.markdown(
    """
    <style>
    .dev-signature {
        position: fixed;
        bottom: 10px;
        right: 10px;
        background-color: rgba(0,0,0,0.1);
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        color: #666;
        z-index: 999;
        backdrop-filter: blur(5px);
    }
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 10px 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .warning-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    <div class="dev-signature">
        💻 Desenvolvido por: Vinicius Dev v2.1
    </div>
    """,
    unsafe_allow_html=True
)

# CSS aprimorado para impressão
def get_print_css():
    return """
    <style>
    @media print {
        .no-print {
            display: none !important;
        }
        .print-only {
            display: block !important;
        }
        body {
            font-family: 'Arial', sans-serif;
            font-size: 9px; /* Reduzir o tamanho da fonte */
            line-height: 1.2; /* Menor altura das linhas */
            color: #000;
        }
        .print-header {
            text-align: center;
            margin-bottom: 10px; /* Reduzir a margem */
            padding-bottom: 8px;
            border-bottom: 2px solid #000;
        }
        .print-header h1 {
            font-size: 12px; /* Reduzir o tamanho do título */
            margin: 0;
            font-weight: bold;
        }
        .print-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 8px; /* Tamanho menor para as tabelas */
        }
        .print-table th, .print-table td {
            border: 1px solid #000;
            padding: 3px; /* Menor padding */
            text-align: left;
        }
        .print-table th {
            background-color: #f5f5f5;
            font-weight: bold;
            text-align: center;
        }
        .print-table td {
            font-size: 8px; /* Ajustar o tamanho do texto */
        }
        .totals-section {
            margin-top: 15px;
            border-top: 2px solid #000;
            padding-top: 8px;
        }
        .total-item {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-weight: bold;
            font-size: 9px; /* Reduzir o tamanho da fonte */
        }
        .highlight-total {
            font-size: 10px;
            background-color: #f0f0f0;
            border: 1px solid #000;
            padding: 6px;
            margin-top: 12px;
        }
        @page {
            margin: 1.2cm; /* Ajustar a margem da página */
            size: A4;
        }
    }
    </style>
    """

# Configuração da conexão com validação
@st.cache_resource
def get_connection_string():
    """Configuração segura da conexão com banco de dados"""
    server = os.getenv('DB_SERVER', 'DCWBD11\\VALLEPRIME_PRD')
    database = os.getenv('DB_DATABASE', 'UAU-VALLEPRIME')
    uid = os.getenv('DB_UID', 'consultasBD')
    pwd = os.getenv('DB_PWD', 'V@lle#2021')
    
    return (
        f"Driver={{SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        f"Timeout=30;"
        f"Connection Timeout=30;"
    )

# Teste de conexão
@st.cache_data(ttl=60)
def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        connection_string = get_connection_string()
        with pyodbc.connect(connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return True, "Conexão estabelecida com sucesso"
    except Exception as e:
        return False, f"Erro na conexão: {str(e)}"

# Mapeamento expandido de tipos de parcelas
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

# Configuração de empresas expandida
EMPRESAS_CONFIG = {
    'ML - 999 - 70100 - 604': {
        'empresa': 999,
        'obra': '70100',
        'codigo': 604,
        'nome': 'ML Constrtora',
        'descricao': 'ML - CONSTRUTORA E INCORPORADORA LTDA'
    },
    'VALLE - 6 - 70400 - 605': {
        'empresa': 6,
        'obra': '70400',
        'codigo': 605,
        'nome': 'Valle Empreendimentos',
        'descricao': 'VALLE - EMPREENDIMENTOS IMOBILIÁRIOS'
    }
}

def escolher_empresa(empresa_selecionada):
    """Retorna configuração da empresa selecionada"""
    config = EMPRESAS_CONFIG.get(empresa_selecionada)
    if config:
        return config['empresa'], config['obra'], config['codigo']
    return None, None, None

def get_empresa_info(empresa_selecionada):
    """Retorna informações completas da empresa"""
    return EMPRESAS_CONFIG.get(empresa_selecionada, {})

# Função aprimorada para obter detalhes da venda
@st.cache_data(ttl=300)
def get_detalhes_venda(num_venda, empresa, obra):
    """Obtém detalhes das parcelas da venda com tratamento de erros aprimorado"""
    query = """
    SELECT 
        Recebidas.NumParc_Rec AS Parc,
        (Recebidas.Valor_Rec + ISNULL(Recebidas.VlJurosParc_Rec, 0) + ISNULL(Recebidas.VlCorrecao_Rec, 0) + 
         ISNULL(Recebidas.VlAcres_Rec, 0) + ISNULL(Recebidas.VlTaxaBol_Rec, 0) + ISNULL(Recebidas.VlMulta_Rec, 0) + 
         ISNULL(Recebidas.VlJuros_Rec, 0) + ISNULL(Recebidas.VlCorrecaoAtr_Rec, 0)
         - (ISNULL(Recebidas.VlDesconto_Rec, 0) + ISNULL(Recebidas.ValDescontoCusta_Rec, 0) + 
            ISNULL(Recebidas.ValDescontoImposto_Rec, 0) + ISNULL(Recebidas.ValDescontoCondicional_rec, 0))
         + ISNULL(Recebidas.ValorConf_Rec, 0) + ISNULL(Recebidas.VlJurosParcConf_Rec, 0) + 
         ISNULL(Recebidas.VlCorrecaoConf_Rec, 0) + ISNULL(Recebidas.VlAcresConf_Rec, 0) + 
         ISNULL(Recebidas.VlTaxaBolConf_Rec, 0) + ISNULL(Recebidas.VlMultaConf_Rec, 0) + 
         ISNULL(Recebidas.VlJurosConf_Rec, 0) + ISNULL(Recebidas.VlCorrecaoAtrConf_Rec, 0)
         - (ISNULL(Recebidas.VlDescontoConf_Rec, 0) + ISNULL(Recebidas.ValDescontoCustaConf_Rec, 0) + 
            ISNULL(Recebidas.ValDescontoImpostoConf_Rec, 0) + ISNULL(Recebidas.ValDescontoCondicionalConf_rec, 0))
        ) AS Val_Parc_Paga,
        Recebidas.Tipo_Rec AS Tipo,
        (ISNULL(Recebidas.ValDescontoCusta_Rec, 0) + ISNULL(Recebidas.ValDescontoCustaConf_Rec, 0)) AS TotDescCusta,
        CONVERT(varchar, Recebidas.Data_Rec, 23) AS Dt_Recebe,
        (ISNULL(Recebidas.VlCorrecao_Rec, 0) + ISNULL(Recebidas.VlCorrecaoConf_Rec, 0) 
        + CASE 
            WHEN Recebidas.Tipo_Rec IN ('R', 'A') 
            THEN 0 
            ELSE  
                CASE ISNULL(VendasRecebidas.AniversarioContr_VRec, 0)
                    WHEN 0  
                    THEN (ISNULL(Recebidas.Valor_Rec, 0) + ISNULL(Recebidas.ValorConf_Rec, 0))  
                    ELSE (ISNULL(Recebidas.Valor_Rec, 0) + ISNULL(Recebidas.ValorConf_Rec, 0) + 
                          ISNULL(Recebidas.VlJurosParcEmb_Rec, 0) + ISNULL(Recebidas.VlJurosParcEmbConf_Rec, 0) + 
                          ISNULL(Recebidas.VlCorrecaoEmb_Rec, 0) + ISNULL(Recebidas.VlCorrecaoEmbConf_Rec, 0))
                END
        END) AS Vl_Confirm
    FROM 
        VendasRecebidas WITH(NOLOCK)
    INNER JOIN 
        Recebidas WITH(NOLOCK) 
        ON VendasRecebidas.Empresa_VRec = Recebidas.Empresa_Rec 
        AND VendasRecebidas.Obra_VRec = Recebidas.Obra_Rec 
        AND VendasRecebidas.Num_VRec = Recebidas.NumVend_Rec
    WHERE 
        Recebidas.Obra_Rec = ?
        AND Recebidas.NumVend_Rec = ?
        AND Recebidas.Empresa_Rec = ?
        AND Recebidas.Data_Rec IS NOT NULL
    ORDER BY 
        Recebidas.Data_Rec, Recebidas.NumParc_Rec
    """
    try:
        connection_string = get_connection_string()
        with pyodbc.connect(connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (obra, num_venda, empresa))
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                
                # Log da consulta
                logging.info(f"Consulta realizada - Venda: {num_venda}, Empresa: {empresa}, Obra: {obra}, Registros: {len(results)}")
                
                return columns, results
    except pyodbc.Error as e:
        logging.error(f"Erro no banco de dados: {e}")
        st.error(f"❌ Erro no banco de dados: {e}")
        return None, None
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        st.error(f"❌ Erro inesperado: {e}")
        return None, None

def formatar_para_real(valor):
    """Formata valor para moeda brasileira com validação aprimorada"""
    try:
        if valor is None or valor == '':
            return "R$ 0,00"
        
        # Converte para float se for string
        if isinstance(valor, str):
            valor = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
            if not valor:
                return "R$ 0,00"
        
        valor_float = float(valor)
        return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError) as e:
        logging.warning(f"Erro ao formatar valor: {valor} - {e}")
        return "R$ 0,00"

def traduzir_tipo_parcela(tipo):
    """Traduz código do tipo de parcela para descrição"""
    return TIPO_PARCELA_MAP.get(str(tipo).upper(), f"Tipo {tipo}")

def get_status_description(status_code):
    """Retorna descrição detalhada do status"""
    status_dict = {
        0: "✅ Normal",
        1: "❌ Cancelada", 
        2: "🔄 Alterada",
        3: "✅ Quitado",
        4: "⏳ Em acerto",
        5: "💰 Aluguel quitado adiantado",
        None: "❓ Status não informado"
    }
    return status_dict.get(status_code, f"❓ Status {status_code}")

def format_cpf_cnpj(document):
    """Formata CPF ou CNPJ com validação aprimorada"""
    if not document:
        return "N/A"
    
    # Remove caracteres não numéricos
    document = ''.join(filter(str.isdigit, str(document)))
    
    if len(document) == 11:
        return f"{document[:3]}.{document[3:6]}.{document[6:9]}-{document[9:]}"
    elif len(document) == 14:
        return f"{document[:2]}.{document[2:5]}.{document[5:8]}/{document[8:12]}-{document[12:]}"
    return document

def format_date(date_obj):
    """Formata data para exibição - versão simplificada e robusta"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%d/%m/%Y')
    elif isinstance(date_obj, str):
        try:
            date_parsed = datetime.strptime(date_obj, '%Y-%m-%d')
            return date_parsed.strftime('%d/%m/%Y')
        except:
            return date_obj
    return str(date_obj) if date_obj else "N/A"

@st.cache_data(ttl=300)
def get_identifier(empresa, obra, num_venda):
    """Obtém identificador da unidade com tratamento de erros"""
    sql_query = """
    SELECT TOP 1 UnidadePer.Identificador_unid AS IdentificadorQuadraLote
    FROM (
       SELECT * FROM ItensVenda WITH(NOLOCK) 
       UNION ALL
       SELECT * FROM ItensRecebidas WITH(NOLOCK) 
    ) AS ItensVenda 
    INNER JOIN PrdSrv WITH(NOLOCK) 
       ON ItensVenda.Produto_Itv = PrdSrv.NumProd_psc 
    INNER JOIN (
       SELECT Empresa_ven, Obra_ven, Num_ven, Data_Ven, ValorTot_ven, Cliente_ven, TipoVenda_Ven, Status_Ven, DataCancel_Ven
       FROM Vendas WITH(NOLOCK) 
       UNION ALL
       SELECT Empresa_vrec, Obra_vrec, Num_vrec, Data_vrec, ValorTot_vrec, Cliente_vrec, TipoVenda_vrec, Status_VRec, DataCancel_VRec
       FROM VendasRecebidas WITH(NOLOCK) 
    ) AS Vendas
       ON ItensVenda.Empresa_itv = Vendas.Empresa_ven
       AND ItensVenda.Obra_Itv = Vendas.Obra_Ven
       AND ItensVenda.NumVend_Itv = Vendas.Num_Ven 
    LEFT JOIN UnidadePer WITH(NOLOCK) 
       ON ItensVenda.Empresa_itv = UnidadePer.Empresa_unid
       AND ItensVenda.Produto_Itv = UnidadePer.Prod_unid
       AND ItensVenda.CodPerson_Itv = UnidadePer.NumPer_unid  
    WHERE Vendas.Empresa_ven = ?
       AND Vendas.Num_Ven = ?
       AND Vendas.Obra_Ven = ?
       AND UnidadePer.Identificador_unid IS NOT NULL
    """
    try:
        connection_string = get_connection_string()
        with pyodbc.connect(connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, (empresa, num_venda, obra))
                result = cursor.fetchone()
                return result.IdentificadorQuadraLote if result and result.IdentificadorQuadraLote else 'N/A'
    except Exception as e:
        logging.error(f"Erro ao obter identificador: {e}")
        return 'N/A'

@st.cache_data(ttl=300)
def consultar_detalhes_venda(num_venda, empresa, obra):
    """Consulta detalhes da venda com informações expandidas"""
    query = """
    SELECT 
        RTRIM(LTRIM(Pessoas.nome_pes)) AS NomeCliente_Ven,
        Vendas.Status_Ven,
        Vendas.Empresa_Ven,
        Vendas.Obra_Ven,
        Vendas.Num_Ven,
        Vendas.Cliente_Ven,
        Vendas.DataIniContrato_Ven,
        RTRIM(LTRIM(Empresas.Desc_emp)) AS Desc_emp,
        RTRIM(LTRIM(Obras.Descr_obr)) AS Descr_obr,
        Pessoas.cpf_pes,
        Vendas.ValorTot_ven,
        Vendas.Data_Ven
    FROM (
        SELECT  
            Empresa_Ven, Obra_Ven, Num_Ven, Cliente_Ven, Status_Ven,
            DataIniContrato_Ven, ValorTot_ven, Data_Ven
        FROM Vendas WITH(NOLOCK) 
        UNION ALL
        SELECT  
            Empresa_VRec, Obra_VRec, Num_VRec, Cliente_VRec, Status_VRec AS Status_Ven,
            DataIniContrato_VRec AS DataIniContrato_Ven, ValorTot_vrec AS ValorTot_ven, Data_vrec AS Data_Ven
        FROM VendasRecebidas WITH(NOLOCK) 
    ) AS Vendas
    INNER JOIN Pessoas WITH(NOLOCK) 
        ON Vendas.Cliente_Ven = Pessoas.cod_pes
    INNER JOIN Obras WITH(NOLOCK) 
        ON Cod_Obr = Vendas.Obra_Ven AND empresa_obr = Vendas.Empresa_Ven
    INNER JOIN Empresas WITH(NOLOCK) 
        ON Codigo_emp = Vendas.Empresa_Ven
    WHERE Vendas.Num_Ven = ? AND Vendas.Empresa_Ven = ? AND Vendas.Obra_Ven = ?
    """

    try:
        connection_string = get_connection_string()
        with pyodbc.connect(connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (num_venda, empresa, obra))
                resultados_venda = cursor.fetchall()

                if resultados_venda:
                    resultado = resultados_venda[0]
                    identificador = get_identifier(empresa, obra, num_venda)
                    
                    # Log da consulta de detalhes
                    logging.info(f"Detalhes da venda encontrados - Cliente: {resultado[0]}, Status: {resultado[1]}")
                    
                    return {
                        'nome_cliente': resultado[0] or 'N/A',
                        'cpf_cnpj': resultado[9] or 'N/A',
                        'num_venda': resultado[4],
                        'status': resultado[1],
                        'empresa': resultado[7] or 'N/A',
                        'obra': resultado[8] or 'N/A',
                        'data_contrato': resultado[6],
                        'identificador': identificador,
                        'valor_total': resultado[10] or 0,
                        'data_venda': resultado[11]
                    }
                else:
                    logging.warning(f"Venda não encontrada - Num: {num_venda}, Empresa: {empresa}, Obra: {obra}")
                    return None
    except pyodbc.Error as e:
        logging.error(f"Erro no banco de dados ao consultar detalhes: {e}")
        st.error(f"❌ Erro no banco de dados: {e}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado ao consultar detalhes: {e}")
        st.error(f"❌ Erro inesperado: {e}")
        return None

def gerar_relatorio_impressao(detalhes_venda, df_parcelas, totais, tipos_selecionados):
    """Gera HTML aprimorado para impressão"""
    tipos_str = ", ".join([f"{k} - {v}" for k, v in tipos_selecionados.items()])
    data_atual = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Valores para Quitação - Venda {detalhes_venda['num_venda']}</title>
        {get_print_css()}
    </head>
    <body>
        <div class="print-header">
            <h1>RELATÓRIO DE VALORES PARA QUITAÇÃO</h1>
            <p><strong>Venda Nº:</strong> {detalhes_venda['num_venda']} | <strong>Data de emissão:</strong> {data_atual}</p>
        </div>
        
        <div class="client-info">
            <div>
                <strong>👤 INFORMAÇÕES DO CLIENTE</strong><br>
                <strong>Nome:</strong> {detalhes_venda['nome_cliente']}<br>
                <strong>CPF/CNPJ:</strong> {format_cpf_cnpj(detalhes_venda['cpf_cnpj'])}<br>
                <strong>Número da Venda:</strong> {detalhes_venda['num_venda']}<br>
                <strong>Status:</strong> {get_status_description(detalhes_venda['status'])}<br>
                <strong>Valor Total da Venda:</strong> {formatar_para_real(detalhes_venda.get('valor_total', 0))}
            </div>
            <div>
                <strong>🏢 INFORMAÇÕES DA VENDA</strong><br>
                <strong>Empresa:</strong> {detalhes_venda['empresa']}<br>
                <strong>Obra:</strong> {detalhes_venda['obra']}<br>
                <strong>Data do Contrato:</strong> {format_date(detalhes_venda['data_contrato'])}<br>
                <strong>Data da Venda:</strong> {format_date(detalhes_venda.get('data_venda'))}<br>
                <strong>Identificador:</strong> {detalhes_venda['identificador']}
            </div>
        </div>
        
        <div style="margin: 10px 0; padding: 6px; background-color: #f9f9f9; border-left: 4px solid #2196F3;">
            <strong>📋 Tipos de Parcelas Consideradas:</strong> {tipos_str}
        </div>
        
        <table class="print-table">
            <thead>
                <tr>
                    <th>Tipo</th>
                    <th>Parc.</th>
                    <th>Data Receb.</th>
                    <th>Valor Pago</th>
                    <th>Valor Confirm.</th>
                    <th>Valor Menor</th>
                    <th>Diferença</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in df_parcelas.iterrows():
        html += f"""
                <tr>
                    <td>{row['Tipo']}</td>
                    <td style="text-align: center;">{row['Parc.']}</td>
                    <td style="text-align: center;">{row['Dt. Recebe']}</td>
                    <td>{row['Val. Parc. Paga']}</td>
                    <td>{row['Vl. Confirm.']}</td>
                    <td>{row['Vl. Menor']}</td>
                    <td>{row['Diferença']}</td>
                </tr>
        """
    
    html += f"""
            </tbody>
        </table>
        
        <div class="totals-section">
            <h3>💰 RESUMO FINANCEIRO</h3>
            <div class="total-item">
                <span>Total Valor Pago:</span>
                <span>{totais['total_pago']}</span>
            </div>
            <div class="total-item">
                <span>Total Valor Confirmado:</span>
                <span>{totais['total_confirmado']}</span>
            </div>
            <div class="total-item highlight-total">
                <span>💎 VALOR PARA USAR NA QUITAÇÃO:</span>
                <span>{totais['valor_quitacao']}</span>
            </div>
        </div>
        
        <div style="margin-top: 40px; font-size: 10px; text-align: center; color: #666; page-break-inside: avoid;">
            <p>📄 Relatório gerado automaticamente pelo Sistema de Consulta de Vendas</p>
            <p><strong>💻 Desenvolvido por: Vinicius Dev</strong> | Sistema v2.1 | {data_atual}</p>
            <p>⚖️ Este relatório deve ser utilizado exclusivamente para fins de quitação contratual</p>
        </div>
    </body>
    </html>
    """
    return html

def criar_botao_impressao(html_content):
    """Cria botão aprimorado para impressão e download"""
    b64_html = base64.b64encode(html_content.encode()).decode()
    href = f'data:text/html;base64,{b64_html}'
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f'''
            <a href="{href}" download="relatorio_quitacao_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html" target="_blank">
                <button style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    margin: 10px 0;
                    width: 100%;
                    box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.37);
                    transition: all 0.3s ease;
                ">
                    📄 Baixar Relatório HTML
                </button>
            </a>
            ''',
            unsafe_allow_html=True
        )
    
    with col2:
        if st.button("📊 Exportar para Excel", use_container_width=True, type="secondary", key="btn_export_excel_relatorio"):
            return "excel_export"
    
    # Exibir preview do relatório HTML diretamente
    with st.expander("👁️ Visualizar Relatório", expanded=True):
        st.components.v1.html(html_content, height=800, scrolling=True)
    
    return None

def exportar_para_excel(detalhes_venda, df_parcelas, totais, tipos_selecionados):
    """Exporta dados para Excel com formatação profissional"""
    try:
        from io import BytesIO
        import pandas as pd
        
        # Criar arquivo Excel em memória
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Aba 1: Informações da Venda
            info_data = {
                'Campo': ['Cliente', 'CPF/CNPJ', 'Número da Venda', 'Status', 'Empresa', 'Obra', 
                         'Data do Contrato', 'Identificador', 'Valor Total da Venda'],
                'Valor': [
                    detalhes_venda['nome_cliente'],
                    format_cpf_cnpj(detalhes_venda['cpf_cnpj']),
                    detalhes_venda['num_venda'],
                    get_status_description(detalhes_venda['status']),
                    detalhes_venda['empresa'],
                    detalhes_venda['obra'],
                    format_date(detalhes_venda['data_contrato']),
                    detalhes_venda['identificador'],
                    formatar_para_real(detalhes_venda.get('valor_total', 0))
                ]
            }
            df_info = pd.DataFrame(info_data)
            df_info.to_excel(writer, sheet_name='Informações da Venda', index=False)
            
            # Aba 2: Parcelas
            df_parcelas.to_excel(writer, sheet_name='Parcelas Pagas', index=False)
            
            # Aba 3: Totais
            totais_data = {
                'Descrição': ['Total Valor Pago', 'Total Valor Confirmado', 'VALOR PARA QUITAÇÃO'],
                'Valor': [totais['total_pago'], totais['total_confirmado'], totais['valor_quitacao']]
            }
            df_totais = pd.DataFrame(totais_data)
            df_totais.to_excel(writer, sheet_name='Totais', index=False)
            
            # Aba 4: Tipos Selecionados
            tipos_data = {
                'Código': list(tipos_selecionados.keys()),
                'Descrição': list(tipos_selecionados.values())
            }
            df_tipos = pd.DataFrame(tipos_data)
            df_tipos.to_excel(writer, sheet_name='Tipos de Parcela', index=False)
        
        output.seek(0)
        
        # Criar link de download
        filename = f"relatorio_quitacao_{detalhes_venda['num_venda']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        st.download_button(
            label="💾 Baixar Excel",
            data=output.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="btn_download_excel_generated"
        )
        
        st.success("✅ Arquivo Excel gerado com sucesso!")
        
    except ImportError:
        st.error("❌ Biblioteca openpyxl não encontrada. Instale: pip install openpyxl")
    except Exception as e:
        st.error(f"❌ Erro ao gerar Excel: {e}")
        logging.error(f"Erro ao exportar Excel: {e}")

def processar_valores_pagos(num_venda, empresa, obra, tipos_selecionados):
    """Processa valores pagos com estatísticas aprimoradas"""
    columns, results = get_detalhes_venda(num_venda, empresa, obra)
    
    if not results:
        return None, None, None
    
    # Processar resultados
    data = []
    total_val_parc_paga = 0
    total_vl_confirm = 0
    total_vl_menor = 0
    estatisticas = {
        'total_parcelas': 0,
        'parcelas_filtradas': 0,
        'tipos_encontrados': set(),
        'periodo_inicial': None,
        'periodo_final': None
    }
    
    for row in results:
        row_dict = dict(zip(columns, row))
        tipo = str(row_dict['Tipo'])
        estatisticas['tipos_encontrados'].add(tipo)
        estatisticas['total_parcelas'] += 1
        
        if tipo in tipos_selecionados:
            tipo_traduzido = traduzir_tipo_parcela(tipo)
            val_parc_paga = float(row_dict['Val_Parc_Paga'] or 0)
            vl_confirm = float(row_dict['Vl_Confirm'] or 0)
            dt_recebe = format_date(row_dict['Dt_Recebe'])
            vl_menor = min(val_parc_paga, vl_confirm)
            diferenca = val_parc_paga - vl_confirm
            
            # Atualizar período
            try:
                data_atual = datetime.strptime(row_dict['Dt_Recebe'], '%Y-%m-%d')
                if estatisticas['periodo_inicial'] is None or data_atual < estatisticas['periodo_inicial']:
                    estatisticas['periodo_inicial'] = data_atual
                if estatisticas['periodo_final'] is None or data_atual > estatisticas['periodo_final']:
                    estatisticas['periodo_final'] = data_atual
            except:
                pass
            
            data.append([
                tipo_traduzido,
                row_dict['Parc'],
                dt_recebe,
                formatar_para_real(val_parc_paga),
                formatar_para_real(vl_confirm),
                formatar_para_real(vl_menor),
                formatar_para_real(diferenca)
            ])
            
            total_val_parc_paga += val_parc_paga
            total_vl_confirm += vl_confirm
            total_vl_menor += vl_menor
            estatisticas['parcelas_filtradas'] += 1
    
    if not data:
        return None, None, estatisticas
    
    # Criar DataFrame
    df = pd.DataFrame(
        data, 
        columns=["Tipo", "Parc.", "Dt. Recebe", "Val. Parc. Paga", "Vl. Confirm.", "Vl. Menor", "Diferença"]
    )
    
    # Preparar dados dos totais
    totais = {
        'total_pago': formatar_para_real(total_val_parc_paga),
        'total_confirmado': formatar_para_real(total_vl_confirm),
        'valor_quitacao': formatar_para_real(total_vl_menor)
    }
    
    return df, totais, estatisticas

def exibir_estatisticas(estatisticas):
    """Exibe estatísticas da consulta"""
    if not estatisticas:
        return
    
    st.markdown("### 📊 Estatísticas da Consulta")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Parcelas", estatisticas['total_parcelas'])
    
    with col2:
        st.metric("Parcelas Filtradas", estatisticas['parcelas_filtradas'])
    
    with col3:
        if estatisticas['periodo_inicial']:
            st.metric("Período Inicial", estatisticas['periodo_inicial'].strftime('%m/%Y'))
        else:
            st.metric("Período Inicial", "N/A")
    
    with col4:
        if estatisticas['periodo_final']:
            st.metric("Período Final", estatisticas['periodo_final'].strftime('%m/%Y'))
        else:
            st.metric("Período Final", "N/A")
    
    # Tipos encontrados
    if estatisticas['tipos_encontrados']:
        tipos_encontrados = [f"{t} - {traduzir_tipo_parcela(t)}" for t in estatisticas['tipos_encontrados']]
        st.info(f"🔍 **Tipos de parcelas encontrados:** {', '.join(tipos_encontrados)}")

def validar_entrada_venda(num_venda):
    """Validação aprimorada da entrada do número da venda"""
    if not num_venda:
        return False, "⚠️ Digite o número da venda"
    
    if not num_venda.isdigit():
        return False, "⚠️ O número da venda deve conter apenas números"
    
    num_venda_int = int(num_venda)
    
    if num_venda_int <= 0:
        return False, "⚠️ O número da venda deve ser maior que zero"
    
    if num_venda_int > 9999999:
        return False, "⚠️ Número da venda muito grande (máximo 7 dígitos)"
    
    return True, "✅ Número da venda válido"

def criar_backup_consulta(detalhes_venda, df_parcelas, totais, tipos_selecionados):
    """Cria backup da consulta em JSON"""
    try:
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'detalhes_venda': detalhes_venda,
            'parcelas': df_parcelas.to_dict('records') if df_parcelas is not None else [],
            'totais': totais,
            'tipos_selecionados': tipos_selecionados,
            'versao_sistema': '2.1'
        }
        
        # Salvar no session state para histórico
        if 'historico_consultas' not in st.session_state:
            st.session_state.historico_consultas = []
        
        st.session_state.historico_consultas.append(backup_data)
        
        # Manter apenas as últimas 10 consultas
        if len(st.session_state.historico_consultas) > 10:
            st.session_state.historico_consultas = st.session_state.historico_consultas[-10:]
        
        return True
    except Exception as e:
        logging.error(f"Erro ao criar backup: {e}")
        return False

def exibir_historico_consultas():
    """Exibe histórico de consultas realizadas"""
    if 'historico_consultas' not in st.session_state or not st.session_state.historico_consultas:
        st.info("📋 Nenhuma consulta realizada nesta sessão")
        return
    
    st.markdown("### 📋 Histórico de Consultas")
    
    for i, consulta in enumerate(reversed(st.session_state.historico_consultas)):
        with st.expander(f"Consulta {len(st.session_state.historico_consultas) - i} - Venda {consulta['detalhes_venda']['num_venda']} - {datetime.fromisoformat(consulta['timestamp']).strftime('%d/%m/%Y %H:%M')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Cliente:** {consulta['detalhes_venda']['nome_cliente']}")
                st.write(f"**Empresa:** {consulta['detalhes_venda']['empresa']}")
                st.write(f"**Status:** {get_status_description(consulta['detalhes_venda']['status'])}")
            
            with col2:
                st.write(f"**Parcelas:** {len(consulta['parcelas'])}")
                st.write(f"**Valor Quitação:** {consulta['totais']['valor_quitacao']}")
                st.write(f"**Tipos:** {', '.join(consulta['tipos_selecionados'].keys())}")

# Interface Principal Aprimorada
def main():
    # Cabeçalho principal
    st.markdown("""
        <div class="main-header">
            <h1>💰 Sistema de Consulta de Vendas</h1>
            <p>🔧 Desenvolvido por: <strong>Vinicius Dev</strong> | Versão 2.1</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Teste de conexão
    conexao_ok, msg_conexao = test_database_connection()
    if not conexao_ok:
        st.error(f"❌ {msg_conexao}")
        st.stop()
    else:
        st.success(f"✅ {msg_conexao}")
    
    # Inicializar session state
    session_vars = [
        'consulta_realizada', 'detalhes_venda', 'df_parcelas', 'totais', 
        'tipos_selecionados', 'num_venda', 'empresa_selecionada', 'estatisticas'
    ]
    
    for var in session_vars:
        if var not in st.session_state:
            if var == 'empresa_selecionada':
                st.session_state[var] = 'ML - 999 - 70100 - 604'
            elif var == 'tipos_selecionados':
                st.session_state[var] = {}
            elif var == 'num_venda':
                st.session_state[var] = ""
            else:
                st.session_state[var] = None if var != 'consulta_realizada' else False
    
    # Menu lateral aprimorado
    with st.sidebar:
        st.markdown("### ⚙️ Configurações do Sistema")
        
        # Informações da empresa selecionada
        empresa_selecionada = st.selectbox(
            "🏢 Selecione a Empresa:",
            list(EMPRESAS_CONFIG.keys()),
            index=0 if st.session_state.empresa_selecionada == 'ML - 999 - 70100 - 604' else 1
        )
        st.session_state.empresa_selecionada = empresa_selecionada
        
        # Mostrar informações da empresa
        empresa_info = get_empresa_info(empresa_selecionada)
        if empresa_info:
            st.info(f"📋 **{empresa_info['nome']}**\n\n{empresa_info['descricao']}")
        
        st.divider()
        
        # Número da venda com validação em tempo real
        num_venda = st.text_input(
            "🔢 Número da Venda:", 
            value=st.session_state.num_venda,
            placeholder="Digite apenas números",
            help="Informe o número da venda que deseja consultar"
        )
        st.session_state.num_venda = num_venda
        
        # Validação em tempo real
        if num_venda:
            valido, msg_validacao = validar_entrada_venda(num_venda)
            if valido:
                st.success(msg_validacao)
            else:
                st.error(msg_validacao)
        
        st.divider()
        
        # Seleção de tipos de parcelas
        st.markdown("### 📋 Tipos de Parcelas")
        st.caption("Selecione os tipos que devem ser considerados no cálculo:")
        
        tipos_selecionados = {}
        
        # Tipos principais
        st.markdown("**🎯 Principais:**")
        tipos_principais = ["E", "P", "S"]
        
        for tipo in tipos_principais:
            default_value = st.session_state.tipos_selecionados.get(tipo, tipo in ["E", "P", "S"])
            if st.checkbox(
                f"**{tipo}** - {TIPO_PARCELA_MAP[tipo]}", 
                value=default_value,
                key=f"tipo_{tipo}",
                help=f"Incluir {TIPO_PARCELA_MAP[tipo]} no cálculo"
            ):
                tipos_selecionados[tipo] = TIPO_PARCELA_MAP[tipo]
        
        # Outros tipos
        with st.expander("🔧 Outros tipos de parcelas"):
            outros_tipos = [k for k in TIPO_PARCELA_MAP.keys() if k not in tipos_principais]
            
            for tipo in outros_tipos:
                default_value = st.session_state.tipos_selecionados.get(tipo, False)
                if st.checkbox(
                    f"**{tipo}** - {TIPO_PARCELA_MAP[tipo]}", 
                    value=default_value,
                    key=f"tipo_{tipo}",
                    help=f"Incluir {TIPO_PARCELA_MAP[tipo]} no cálculo"
                ):
                    tipos_selecionados[tipo] = TIPO_PARCELA_MAP[tipo]
        
        st.session_state.tipos_selecionados = tipos_selecionados
        
        st.divider()
        
        # Instruções e informações
        with st.expander("📖 Manual do Usuário"):
            st.markdown("""
            **🚀 Como usar o sistema:**
            
            1. **🏢 Empresa:** Selecione a empresa desejada
            2. **🔢 Venda:** Digite o número da venda (apenas números)
            3. **📋 Tipos:** Marque as parcelas a considerar
            4. **🔍 Consultar:** Clique para buscar os dados
            5. **📄 Relatório:** Gere e baixe o relatório
            
            **📊 Tipos de parcelas:**
            - **E:** Entrada do cliente
            - **P:** Parcelas mensais
            - **S:** Comissão de corretagem
            
            **💡 Dicas importantes:**
            - O sistema usa sempre o **menor valor** entre "Pago" e "Confirmado"
            - Este valor é o **recomendado para quitação**
            - Relatórios podem ser salvos em HTML ou Excel
            - Histórico das consultas fica disponível na sessão
            
            ---
            **👨‍💻 Desenvolvido por: Vinicius Dev**  
            **📧 Suporte:** Entre em contato para dúvidas  
            **🆔 Versão:** 2.1 - Sistema de Consulta de Vendas
            """)
        
        # Informações do sistema
        st.markdown("---")
        st.markdown("### 📊 Informações do Sistema")
        st.info(f"""
        **Sistema:** Consulta de Vendas v2.1  
        **Desenvolvedor:** Vinicius Dev  
        **Conexão:** ✅ Ativa  
        **Cache:** {len(st.session_state.get('historico_consultas', []))} consultas
        """)

    # Área principal
    if not tipos_selecionados:
        st.markdown("""
            <div class="warning-card">
                <h3>⚠️ Atenção!</h3>
                <p>Selecione pelo menos um tipo de parcela no menu lateral para continuar.</p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    # Mostrar tipos selecionados
    tipos_str = ", ".join([f"**{k}** ({v})" for k, v in tipos_selecionados.items()])
    st.info(f"📊 **Tipos selecionados:** {tipos_str}")
    
    # Botões de ação principais
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        consultar = st.button("🔍 Consultar Venda", type="primary", use_container_width=True, key="btn_consultar_main")
    
    with col2:
        nova_consulta = st.button("🔄 Nova Consulta", use_container_width=True, key="btn_nova_consulta_main")
    
    with col3:
        historico = st.button("📋 Ver Histórico", use_container_width=True, key="btn_historico_main")
    
    with col4:
        if st.button("🗑️", help="Limpar Cache", use_container_width=True, key="btn_limpar_cache_main"):
            st.cache_data.clear()
            st.success("✅ Cache limpo!")
    
    # Ações dos botões
    if nova_consulta:
        for var in ['consulta_realizada', 'detalhes_venda', 'df_parcelas', 'totais', 'estatisticas']:
            st.session_state[var] = None if var != 'consulta_realizada' else False
        st.rerun()
    
    if historico:
        exibir_historico_consultas()
        return
    
    # Realizar consulta
    if consultar:
        valido, msg_validacao = validar_entrada_venda(num_venda)
        
        if not valido:
            st.error(msg_validacao)
            return
        
        empresa, obra, _ = escolher_empresa(empresa_selecionada)
        if not all([empresa, obra]):
            st.error("❌ Configuração de empresa inválida")
            return
        
        # Consultar dados com progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔍 Buscando detalhes da venda...")
            progress_bar.progress(25)
            
            detalhes_venda = consultar_detalhes_venda(num_venda, empresa, obra)
            
            if not detalhes_venda:
                st.error("❌ Venda não encontrada. Verifique o número e a empresa selecionada.")
                progress_bar.empty()
                status_text.empty()
                return
            
            status_text.text("💰 Processando parcelas pagas...")
            progress_bar.progress(75)
            
            df_parcelas, totais, estatisticas = processar_valores_pagos(num_venda, empresa, obra, tipos_selecionados)
            
            progress_bar.progress(100)
            status_text.text("✅ Consulta concluída!")
            
            # Salvar no session state
            st.session_state.consulta_realizada = True
            st.session_state.detalhes_venda = detalhes_venda
            st.session_state.df_parcelas = df_parcelas
            st.session_state.totais = totais
            st.session_state.estatisticas = estatisticas
            
            # Criar backup
            criar_backup_consulta(detalhes_venda, df_parcelas, totais, tipos_selecionados)
            
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"❌ Erro durante a consulta: {e}")
            logging.error(f"Erro na consulta: {e}\n{traceback.format_exc()}")
            progress_bar.empty()
            status_text.empty()
            return
    
    # Exibir resultados
    if st.session_state.consulta_realizada and st.session_state.detalhes_venda:
        detalhes_venda = st.session_state.detalhes_venda
        df_parcelas = st.session_state.df_parcelas
        totais = st.session_state.totais
        estatisticas = st.session_state.estatisticas
        
        # Sucesso
        st.markdown("""
            <div class="success-card">
                <h3>✅ Venda encontrada com sucesso!</h3>
                <p>Dados carregados e processados. Confira as informações abaixo.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Informações do cliente e venda
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
                ### 👤 Informações do Cliente
                - **Nome:** {detalhes_venda['nome_cliente']}
                - **CPF/CNPJ:** {format_cpf_cnpj(detalhes_venda['cpf_cnpj'])}
                - **Número da Venda:** {detalhes_venda['num_venda']}
                - **Status:** {get_status_description(detalhes_venda['status'])}
            """)
        
        with col2:
            st.markdown(f"""
                ### 🏢 Informações da Venda
                - **Empresa:** {detalhes_venda['empresa']}
                - **Obra:** {detalhes_venda['obra']}
                - **Data do Contrato:** {format_date(detalhes_venda['data_contrato'])}
                - **Identificador:** {detalhes_venda['identificador']}
                - **Valor Total:** {formatar_para_real(detalhes_venda.get('valor_total', 0))}
            """)
        
        st.divider()
        
        # Estatísticas
        exibir_estatisticas(estatisticas)
        
        st.divider()
        
        if df_parcelas is not None and totais is not None:
            # Tabela de parcelas
            st.markdown("### 💰 Parcelas Pagas")
            st.dataframe(
                df_parcelas, 
                use_container_width=True,
                column_config={
                    "Tipo": st.column_config.TextColumn("Tipo", width="medium"),
                    "Parc.": st.column_config.NumberColumn("Parc.", width="small"),
                    "Dt. Recebe": st.column_config.TextColumn("Data Receb.", width="medium"),
                    "Val. Parc. Paga": st.column_config.TextColumn("Valor Pago", width="medium"),
                    "Vl. Confirm.": st.column_config.TextColumn("Valor Confirm.", width="medium"),
                    "Vl. Menor": st.column_config.TextColumn("Valor Menor", width="medium"),
                    "Diferença": st.column_config.TextColumn("Diferença", width="medium")
                }
            )
            
            st.divider()
            
            # Métricas principais
            st.markdown("### 📊 Resumo Financeiro")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                    <div class="metric-card">
                        <h4>💵 Total Pago</h4>
                        <h2>{}</h2>
                    </div>
                """.format(totais['total_pago']), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class="metric-card">
                        <h4>✅ Total Confirmado</h4>
                        <h2>{}</h2>
                    </div>
                """.format(totais['total_confirmado']), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                        <h4>💎 VALOR QUITAÇÃO</h4>
                        <h2>{}</h2>
                    </div>
                """.format(totais['valor_quitacao']), unsafe_allow_html=True)
            
            st.divider()
            
            # Botões de ação para relatórios
            st.markdown("### 📄 Gerar Relatórios")
            col1, col2 = st.columns(2)
            
            with col1:
                gerar_relatorio = st.button("🖨️ Gerar Relatório HTML", use_container_width=True, type="primary", key="btn_gerar_relatorio_main")
            
            with col2:
                exportar_excel = st.button("📊 Exportar para Excel", use_container_width=True, key="btn_exportar_excel_main")
            
            # Processar ações de relatório
            if gerar_relatorio:
                with st.spinner("📄 Gerando relatório..."):
                    html_relatorio = gerar_relatorio_impressao(
                        detalhes_venda, df_parcelas, totais, tipos_selecionados
                    )
                    
                    st.success("✅ Relatório HTML gerado com sucesso!")
                    
                    # Botão de download e preview
                    criar_botao_impressao(html_relatorio)
            
            if exportar_excel:
                with st.spinner("📊 Gerando arquivo Excel..."):
                    exportar_para_excel(detalhes_venda, df_parcelas, totais, tipos_selecionados)
        
        else:
            st.markdown("""
                <div class="warning-card">
                    <h3>⚠️ Nenhuma parcela encontrada</h3>
                    <p>Não foram encontradas parcelas pagas com os tipos selecionados para esta venda.</p>
                    <p><strong>Sugestões:</strong></p>
                    <ul>
                        <li>Verifique se os tipos de parcelas selecionados estão corretos</li>
                        <li>Confirme se a venda possui parcelas pagas</li>
                        <li>Tente selecionar outros tipos de parcelas</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Erro crítico no sistema: {e}")
        logging.critical(f"Erro crítico: {e}\n{traceback.format_exc()}")
        
        # Informações para debug
        with st.expander("🔧 Informações para Suporte"):
            st.code(f"""
            Erro: {str(e)}
            Timestamp: {datetime.now()}
            Versão: 2.1
            
            Stack trace:
            {traceback.format_exc()}
            """)
        


        st.info("💡 Entre em contato com o desenvolvedor: **Vinicius Dev**")
        
        