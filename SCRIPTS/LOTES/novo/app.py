import streamlit as st
import pyodbc
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="VallePrime - Dashboard de Vendas",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado para design moderno
st.markdown("""
<style>
    /* Tema escuro moderno */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Header estilizado */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Cards de métricas */
    .metric-card {
        background: linear-gradient(145deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.7);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sidebar estilizada */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #667eea;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    /* Tabs estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(30, 58, 95, 0.5);
        padding: 10px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 10px;
        color: white;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Dataframe estilizado */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        border: none;
        border-radius: 10px;
    }
    
    /* Alertas e info */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Divisor */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: rgba(255,255,255,0.5);
        font-size: 0.9rem;
    }
    
    /* Animação de fade-in */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out forwards;
    }
</style>
""", unsafe_allow_html=True)

def conectar_banco_dados():
    """Conecta ao banco de dados"""
    try:
        connection_string = (
            "Driver={SQL Server};"
            "Server=" + os.getenv('DB_SERVER', 'DCWBD11\\VALLEPRIME_PRD') + ";"
            "Database=" + os.getenv('DB_DATABASE', 'UAU-VALLEPRIME') + ";"
            "UID=" + os.getenv('DB_UID', 'consultasBD') + ";"
            "PWD=" + os.getenv('DB_PWD', 'V@lle#2021') + ";"
            "Timeout=30;"
        )
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        st.error(f"❌ Erro ao conectar: {e}")
        return None

@st.cache_data(ttl=300)
def buscar_vendas(empresa, obra):
    """Busca todas as vendas da obra"""
    conn = conectar_banco_dados()
    if not conn:
        return None
    
    query = """
    SELECT 
        Vendas.Empresa_Ven,
        Vendas.Obra_Ven,
        Vendas.Num_Ven AS Venda,
        Vendas.Cliente_Ven,
        Pessoas.nome_pes AS Cliente,
        Vendas.Vendedor_Ven,
        PessoasVendedor.nome_pes AS Corretor,
        FORMAT(Vendas.Data_Ven, 'dd/MM/yyyy') AS [Data Venda],
        FORMAT(Vendas.DataCad_Ven, 'dd/MM/yyyy') AS [Data Cadastro],
        (Vendas.ValorTot_Ven + Vendas.Acrescimo_Ven - Vendas.Desconto_Ven) AS [Valor Total],
        Vendas.Obra_Ven + ' - Q' + ISNULL(u.C1_unid, '') + ' L' + ISNULL(u.C2_unid, '') AS Identificador,
        Vendas.Status_Ven
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
    
    try:
        df = pd.read_sql(query, conn, params=[empresa, obra])
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao buscar vendas: {e}")
        conn.close()
        return None

@st.cache_data(ttl=300)
def buscar_sinais_corretagem(empresa, obra, data_vencimento_str):
    """Busca sinais de corretagem a receber"""
    conn = conectar_banco_dados()
    if not conn:
        return None
    
    query = f"""
    SELECT 
        c.nome_pes as [Corretor],
        p.nome_pes as Cliente,
        r.Empresa_prc as Emp,
        r.NumVend_prc as Venda,
        r.Obra_Prc as Obra,
        u.C1_unid as Quadra,
        u.C2_unid as Lote,
        FORMAT(vendas.Data_Ven,'dd/MM/yyyy') as [Data Venda],
        FORMAT(vendas.DataCad_Ven,'dd/MM/yyyy') as [Data Cad.],
        vendas.[Vlr. Venda] as [Vlr. Venda],
        r.NumParc_Prc as Parcela,
        r.TotParc_Prc as [Qtd Parc.],
        FORMAT(r.Data_Prc,'dd/MM/yyyy') as Vencimento,
        FORMAT(r.DataPror_Prc,'dd/MM/yyyy') as [Prorrogação],
        r.Valor_Prc as [Valor Parcela]
    FROM ContasReceber r WITH(NOLOCK)
    INNER JOIN pessoas p WITH(NOLOCK) ON p.cod_pes = r.Cliente_Prc
    INNER JOIN (
        SELECT v.empresa_ven, v.num_ven, v.obra_ven, v.vendedor_ven, v.cliente_ven,
               (v.ValorTot_Ven + v.Acrescimo_Ven - v.Desconto_Ven) AS 'Vlr. Venda',
               v.Data_ven, v.datacad_ven
        FROM vendas v WITH(NOLOCK)
        UNION
        SELECT vr.empresa_vrec, vr.num_vrec, vr.obra_vrec, vr.vendedor_vrec, vr.cliente_vrec,
               (vr.ValorTot_VRec + vr.Acrescimo_VRec - vr.Desconto_VRec) AS 'Vlr. Venda',
               vr.Data_VRec, vr.DataCad_VRec
        FROM VendasRecebidas vr WITH(NOLOCK)
    ) as vendas ON vendas.Empresa_ven = r.Empresa_prc 
                AND vendas.Obra_Ven = r.Obra_Prc 
                AND vendas.Num_Ven = r.NumVend_prc
    INNER JOIN pessoas c WITH(NOLOCK) ON c.cod_pes = vendas.Vendedor_Ven
    INNER JOIN (
        SELECT Empresa_itv, NumVend_Itv, Obra_Itv, Produto_Itv, CodPerson_Itv 
        FROM ItensVenda WITH(NOLOCK)
        UNION
        SELECT Empresa_itr, NumVend_Itr, Obra_Itr, Produto_Itr, CodPerson_Itr 
        FROM ItensRecebidas WITH(NOLOCK)
    ) as ItensVendas ON ItensVendas.Empresa_itv = r.Empresa_prc 
                     AND ItensVendas.Obra_Itv = r.Obra_Prc 
                     AND ItensVendas.NumVend_Itv = r.NumVend_prc
    LEFT JOIN UnidadePer u WITH(NOLOCK) ON ItensVendas.Empresa_itv = u.Empresa_unid 
                                        AND ItensVendas.Produto_Itv = u.Prod_unid 
                                        AND ItensVendas.CodPerson_Itv = u.NumPer_unid
    WHERE vendas.Empresa_ven = {empresa} 
      AND r.Empresa_prc = {empresa} 
      AND r.Tipo_Prc IN ('S') 
      AND r.Obra_Prc = '{obra}' 
      AND r.Data_Prc <= CONVERT(date, '{data_vencimento_str}', 23)
    ORDER BY r.NumVend_prc, r.NumParc_Prc
    """
    
    try:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao buscar sinais de corretagem: {e}")
        conn.close()
        return None

@st.cache_data(ttl=300)
def buscar_sinais_pagos(empresa, obra, num_venda):
    """Busca sinais pagos de uma venda específica"""
    conn = conectar_banco_dados()
    if not conn:
        return None
    
    query = """
    SELECT 
        Recebidas.Empresa_Rec,
        Recebidas.Obra_Rec,
        Recebidas.NumVend_Rec AS Venda,
        Recebidas.NumParc_Rec AS Parcela,
        Recebidas.Tipo_Rec,
        FORMAT(Recebidas.Data_Rec, 'dd/MM/yyyy') AS [Data Recebimento],
        FORMAT(Recebidas.DataVenci_Rec, 'dd/MM/yyyy') AS [Data Vencimento],
        Recebidas.Valor_Rec + Recebidas.ValorConf_Rec AS [Valor Pago],
        Pessoas.nome_pes AS Cliente
    FROM Recebidas WITH(NOLOCK)
    INNER JOIN VendasRecebidas WITH(NOLOCK) 
        ON VendasRecebidas.Empresa_VRec = Recebidas.Empresa_Rec
        AND VendasRecebidas.Obra_VRec = Recebidas.Obra_Rec
        AND VendasRecebidas.Num_VRec = Recebidas.NumVend_Rec
    INNER JOIN Pessoas WITH(NOLOCK) ON Pessoas.Cod_pes = Recebidas.Cliente_Rec
    WHERE Recebidas.Obra_Rec = ?
      AND Recebidas.NumVend_Rec = ?
      AND Recebidas.Empresa_Rec = ?
      AND Recebidas.Tipo_Rec = 'S'
      AND Recebidas.Status_Rec = 1
    ORDER BY Recebidas.NumParc_Rec
    """
    
    try:
        df = pd.read_sql(query, conn, params=[obra, num_venda, empresa])
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao buscar sinais pagos: {e}")
        conn.close()
        return None

@st.cache_data(ttl=300)
def buscar_sinais_abertos_por_venda(empresa, obra):
    """Busca contagem de sinais em aberto por venda (sem filtro de data)"""
    conn = conectar_banco_dados()
    if not conn:
        return None
    
    query = f"""
    SELECT 
        r.NumVend_prc as Venda,
        COUNT(*) as QtdSinaisAberto
    FROM ContasReceber r WITH(NOLOCK)
    WHERE r.Empresa_prc = {empresa}
      AND r.Obra_Prc = '{obra}'
      AND r.Tipo_Prc = 'S'
      AND r.Status_Prc = 0
    GROUP BY r.NumVend_prc
    """
    
    try:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao buscar sinais em aberto: {e}")
        conn.close()
        return None

@st.cache_data(ttl=300)
def buscar_boletos_gerados(empresa):
    """Busca todos os boletos gerados"""
    conn = conectar_banco_dados()
    if not conn:
        return None
    
    query = """
    SELECT 
        RecebAuto.Empresa_rea AS Empresa,
        RecebAuto.ObraPrc_Rea AS Obra,
        RecebAuto.NumVendPrc_Rea AS Venda,
        RecebAuto.NumParcPrc_Rea AS Parcela,
        RecebAuto.TipoPrc_Rea AS Tipo,
        Pessoas.nome_pes AS Cliente,
        Boleto.SeuNum_Bol AS [Nosso Número],
        Boleto.NossoNum_Bol AS [Número Boleto],
        FORMAT(Boleto.DataEmis_Bol, 'dd/MM/yyyy') AS [Data Emissão],
        FORMAT(Boleto.DataVenc_Bol, 'dd/MM/yyyy') AS [Data Vencimento],
        Boleto.ValDoc_Bol AS [Valor Documento],
        CASE 
            WHEN Boleto.DataEnvioPorEmail_bol IS NOT NULL THEN 'Sim'
            ELSE 'Não'
        END AS [Enviado Email]
    FROM RecebAuto WITH(NOLOCK)
    INNER JOIN Boleto WITH(NOLOCK) 
        ON RecebAuto.SeuNum_Rea = Boleto.SeuNum_Bol
        AND RecebAuto.Banco_Rea = Boleto.Banco_Bol
    INNER JOIN Pessoas WITH(NOLOCK) ON Boleto.ClienteVen_bol = Pessoas.cod_pes
    WHERE RecebAuto.Empresa_rea = ?
    ORDER BY RecebAuto.NumVendPrc_Rea, RecebAuto.NumParcPrc_Rea
    """
    
    try:
        df = pd.read_sql(query, conn, params=[empresa])
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao buscar boletos: {e}")
        conn.close()
        return None

def criar_resumo_vendas(vendas_df, boletos_df, sinais_abertos_df):
    """Cria um resumo consolidado das vendas"""
    if vendas_df is None or vendas_df.empty:
        return None
    
    resumo = []
    
    for _, venda in vendas_df.iterrows():
        num_venda = venda['Venda']
        
        # Verifica se tem boleto gerado
        tem_boleto = False
        if boletos_df is not None and not boletos_df.empty:
            tem_boleto = len(boletos_df[boletos_df['Venda'] == num_venda]) > 0
        
        # Conta sinais em aberto (usando a nova consulta direta)
        sinais_aberto = 0
        if sinais_abertos_df is not None and not sinais_abertos_df.empty:
            sinais_venda = sinais_abertos_df[sinais_abertos_df['Venda'] == num_venda]
            if not sinais_venda.empty:
                sinais_aberto = int(sinais_venda['QtdSinaisAberto'].values[0])
        
        resumo.append({
            'Venda': num_venda,
            'Cliente': venda['Cliente'],
            'Identificador': venda['Identificador'],
            'Corretor': venda['Corretor'],
            'Data Venda': venda['Data Venda'],
            'Valor Total': venda['Valor Total'],
            'Boleto Gerado?': '✅ Sim' if tem_boleto else '❌ Não',
            'Sinais em Aberto': sinais_aberto
        })
    
    return pd.DataFrame(resumo)

def gerar_pdf_relatorio(resumo_df, empresa, obra, data_geracao):
    """Gera relatório em PDF"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                                leftMargin=1*cm, rightMargin=1*cm,
                                topMargin=1*cm, bottomMargin=1*cm)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=20,
            alignment=1  # Center
        )
        elements.append(Paragraph("🏘️ VallePrime - Relatório de Vendas", title_style))
        
        # Subtítulo com informações
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=1
        )
        elements.append(Paragraph(f"Empresa: {empresa} | Obra: {obra} | Gerado em: {data_geracao}", subtitle_style))
        elements.append(Spacer(1, 20))
        
        # Resumo estatístico
        total_vendas = len(resumo_df)
        vendas_com_boleto = len(resumo_df[resumo_df['Boleto Gerado?'] == '✅ Sim'])
        vendas_sem_boleto = len(resumo_df[resumo_df['Boleto Gerado?'] == '❌ Não'])
        total_sinais = resumo_df['Sinais em Aberto'].sum()
        valor_total = resumo_df['Valor Total'].sum()
        
        stats_data = [
            ['Total de Vendas', 'Com Boleto', 'Sem Boleto', 'Sinais em Aberto', 'Valor Total'],
            [str(total_vendas), str(vendas_com_boleto), str(vendas_sem_boleto), 
             str(int(total_sinais)), f'R$ {valor_total:,.2f}']
        ]
        
        stats_table = Table(stats_data, colWidths=[4*cm, 3*cm, 3*cm, 4*cm, 5*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0f4ff')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 30))
        
        # Tabela de vendas
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10
        )
        elements.append(Paragraph("📋 Detalhamento das Vendas", section_style))
        
        # Converter DataFrame para tabela
        table_data = [resumo_df.columns.tolist()]
        for _, row in resumo_df.iterrows():
            table_data.append([
                str(row['Venda']),
                str(row['Cliente'])[:30],  # Limitar tamanho
                str(row['Identificador']),
                str(row['Corretor'])[:25],
                str(row['Data Venda']),
                f"R$ {row['Valor Total']:,.2f}",
                str(row['Boleto Gerado?']),
                str(row['Sinais em Aberto'])
            ])
        
        # Criar tabela com larguras ajustadas
        data_table = Table(table_data, colWidths=[1.5*cm, 5*cm, 3*cm, 4*cm, 2.5*cm, 3*cm, 2*cm, 2*cm])
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        elements.append(data_table)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=1
        )
        elements.append(Paragraph("Sistema de Controle de Vendas e Boletos - VallePrime © 2024", footer_style))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
        
    except ImportError:
        st.error("❌ Biblioteca reportlab não instalada. Execute: pip install reportlab")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao gerar PDF: {e}")
        return None

# ======================== INTERFACE PRINCIPAL ========================

# Header
st.markdown("""
<div class="main-header">
    <h1>🏘️ VallePrime - Dashboard de Vendas</h1>
    <p>Sistema de Controle de Vendas, Boletos e Sinais de Corretagem</p>
</div>
""", unsafe_allow_html=True)

# Sidebar com filtros
with st.sidebar:
    st.markdown("## ⚙️ Filtros")
    
    empresa = st.number_input("🏢 Empresa", value=28, min_value=1)
    obra = st.text_input("🏗️ Obra", value="70100")
    data_vencimento = st.date_input("📅 Data Vencimento", value=datetime(2025, 12, 31))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Informações")
    st.info(f"**Empresa:** {empresa}\n\n**Obra:** {obra}")

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Resumo Geral", 
    "💰 Sinais de Corretagem", 
    "📄 Boletos Gerados",
    "📊 Detalhes por Venda"
])

# ======================== TAB 1: RESUMO GERAL ========================
with tab1:
    with st.spinner("🔄 Carregando dados..."):
        vendas_df = buscar_vendas(empresa, obra)
        boletos_df = buscar_boletos_gerados(empresa)
        sinais_abertos_df = buscar_sinais_abertos_por_venda(empresa, obra)
        
        if vendas_df is not None and not vendas_df.empty:
            resumo_df = criar_resumo_vendas(vendas_df, boletos_df, sinais_abertos_df)
            
            if resumo_df is not None:
                # Métricas em cards
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Total de Vendas", len(resumo_df))
                
                with col2:
                    vendas_com_boleto = len(resumo_df[resumo_df['Boleto Gerado?'] == '✅ Sim'])
                    st.metric("✅ Com Boleto", vendas_com_boleto)
                
                with col3:
                    vendas_sem_boleto = len(resumo_df[resumo_df['Boleto Gerado?'] == '❌ Não'])
                    st.metric("❌ Sem Boleto", vendas_sem_boleto)
                
                with col4:
                    total_sinais = resumo_df['Sinais em Aberto'].sum()
                    st.metric("⚠️ Sinais em Aberto", int(total_sinais))
                
                st.markdown("---")
                
                # Valor total
                valor_total = resumo_df['Valor Total'].sum()
                st.markdown(f"### 💰 Valor Total das Vendas: **R$ {valor_total:,.2f}**")
                
                st.markdown("---")
                
                # Tabela de resumo
                st.markdown("### 📋 Lista de Vendas")
                st.dataframe(
                    resumo_df,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
                st.markdown("---")
                
                # Botões de download
                st.markdown("### 📥 Exportar Relatório")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download CSV
                    csv = resumo_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv,
                        file_name=f"relatorio_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # Download PDF
                    pdf_buffer = gerar_pdf_relatorio(
                        resumo_df, 
                        empresa, 
                        obra, 
                        datetime.now().strftime('%d/%m/%Y %H:%M')
                    )
                    if pdf_buffer:
                        st.download_button(
                            label="📑 Download PDF",
                            data=pdf_buffer,
                            file_name=f"relatorio_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
        else:
            st.warning("⚠️ Nenhuma venda encontrada para os filtros selecionados.")

# ======================== TAB 2: SINAIS DE CORRETAGEM ========================
with tab2:
    st.markdown("### 💰 Sinais de Corretagem a Receber")
    
    # Buscar sinais aqui para esta tab
    sinais_df = buscar_sinais_corretagem(empresa, obra, data_vencimento.strftime('%Y-%m-%d'))
    
    if sinais_df is not None and not sinais_df.empty:
        # Métricas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Total de Parcelas", len(sinais_df))
        
        with col2:
            total_valor = sinais_df['Valor Parcela'].sum()
            st.metric("💰 Valor Total", f"R$ {total_valor:,.2f}")
        
        with col3:
            vendas_unicas = sinais_df['Venda'].nunique()
            st.metric("🏠 Vendas Distintas", vendas_unicas)
        
        st.markdown("---")
        
        # Tabela
        st.dataframe(
            sinais_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        st.markdown("---")
        
        # Download
        col1, col2 = st.columns(2)
        with col1:
            csv = sinais_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"sinais_corretagem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("ℹ️ Nenhum sinal de corretagem encontrado para o período selecionado.")

# ======================== TAB 3: BOLETOS GERADOS ========================
with tab3:
    st.markdown("### 📄 Boletos Gerados")
    
    if boletos_df is not None and not boletos_df.empty:
        # Filtro por venda
        vendas_disponiveis = ['Todas'] + sorted(boletos_df['Venda'].unique().tolist())
        venda_filtro = st.selectbox("🔍 Filtrar por Venda", vendas_disponiveis)
        
        df_filtrado = boletos_df if venda_filtro == 'Todas' else boletos_df[boletos_df['Venda'] == venda_filtro]
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Total de Boletos", len(df_filtrado))
        
        with col2:
            enviados = len(df_filtrado[df_filtrado['Enviado Email'] == 'Sim'])
            st.metric("📧 Enviados por Email", enviados)
        
        with col3:
            total_valor = df_filtrado['Valor Documento'].sum()
            st.metric("💰 Valor Total", f"R$ {total_valor:,.2f}")
        
        st.markdown("---")
        
        # Tabela
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        st.markdown("---")
        
        # Download
        col1, col2 = st.columns(2)
        with col1:
            csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"boletos_gerados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("ℹ️ Nenhum boleto encontrado.")

# ======================== TAB 4: DETALHES POR VENDA ========================
with tab4:
    st.markdown("### 📊 Consulta Detalhada por Venda")
    
    if vendas_df is not None and not vendas_df.empty:
        venda_selecionada = st.selectbox(
            "🔍 Selecione a Venda",
            vendas_df['Venda'].unique()
        )
        
        if venda_selecionada:
            # Informações da venda
            venda_info = vendas_df[vendas_df['Venda'] == venda_selecionada].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📋 Informações da Venda")
                st.markdown(f"""
                - **Venda:** {venda_info['Venda']}
                - **Cliente:** {venda_info['Cliente']}
                - **Corretor:** {venda_info['Corretor']}
                - **Identificador:** {venda_info['Identificador']}
                """)
            
            with col2:
                st.markdown("#### 💰 Valores")
                st.markdown(f"""
                - **Data Venda:** {venda_info['Data Venda']}
                - **Valor Total:** R$ {venda_info['Valor Total']:,.2f}
                """)
            
            st.markdown("---")
            
            # Sinais pagos
            st.markdown("#### ✅ Sinais Pagos")
            sinais_pagos_df = buscar_sinais_pagos(empresa, obra, venda_selecionada)
            
            if sinais_pagos_df is not None and not sinais_pagos_df.empty:
                st.dataframe(sinais_pagos_df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum sinal pago encontrado.")
            
            st.markdown("---")
            
            # Boletos da venda
            st.markdown("#### 📄 Boletos da Venda")
            if boletos_df is not None and not boletos_df.empty:
                boletos_venda = boletos_df[boletos_df['Venda'] == venda_selecionada]
                if not boletos_venda.empty:
                    st.dataframe(boletos_venda, use_container_width=True, hide_index=True)
                else:
                    st.warning("⚠️ Nenhum boleto gerado para esta venda.")
            else:
                st.warning("⚠️ Nenhum boleto gerado para esta venda.")
    else:
        st.warning("⚠️ Nenhuma venda disponível.")

# ======================== FOOTER ========================
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>🏘️ <strong>VallePrime</strong> - Sistema de Controle de Vendas e Boletos</p>
    <p>© 2024 - Todos os direitos reservados</p>
</div>
""", unsafe_allow_html=True)
