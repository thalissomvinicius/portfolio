import streamlit as st
import pandas as pd
import pyodbc
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import re

# CONFIGURAÇÃO DA PÁGINA - DEVE SER O PRIMEIRO COMANDO
st.set_page_config(
    page_title="Sistema de Gestão de Lotes",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

def buscar_lotes(conn):
    """Executa a query principal para buscar lotes"""
    try:
        query = """
        SELECT up.Empresa_unid as Emp,
               ps.NumProd_psc,
               ps.Descricao_psc as Empreendimento,
               Identificador_unid as Identificador,
               c4_unid as Endereco,
               up.Qtde_unid as AreaM2,
               ROUND(
                   up.Qtde_unid *
                   ROUND(
                       (up.PorcentPr_Unid / 100) * (
                           SELECT SUM(cpp.Valor_cpp)
                           FROM   CategoriasPrecoProd cpp
                           WHERE  cpp.Data_cpp = (
                                      SELECT MAX(cp1.Data_cpp)
                                      FROM   CategoriasPrecoProd cp1
                                      WHERE  cp1.NumProd_cpp = cpp.NumProd_cpp
                                             AND cp1.Codigo_cpp = cpp.Codigo_cpp
                                             AND cp1.Empresa_cpp = cpp.Empresa_cpp
                                  )
                                  AND cpp.NumProd_cpp = up.Prod_unid
                                  AND cpp.Codigo_cpp = up.Codigo_Unid
                                  AND cpp.Empresa_cpp = up.Empresa_unid
                           GROUP BY
                                  cpp.NumProd_cpp,
                                  cpp.Codigo_cpp
                       ),
                       2
                   ),
                   2
               ) AS ValorTerreno,
               up.Vendido_unid,
               CASE up.Vendido_unid
                    WHEN 0 THEN 'Disponível'
                    WHEN 1 THEN 'Vendido'
                    WHEN 2 THEN 'Reservado'
                    WHEN 3 THEN 'Proposta'
                    WHEN 4 THEN 'Quitado'
                    WHEN 5 THEN 'Escriturado'
                    WHEN 6 THEN 'Em venda'
                    WHEN 7 THEN 'Suspenso'
                    WHEN 8 THEN 'Fora de venda'
                    WHEN 9 THEN 'Em Acerto'
                    WHEN 10 THEN 'Dação'
               END AS Status_terreno,
               GETDATE() AS Data_atualizacao
        FROM   UnidadePer up
               INNER JOIN PrdSrv ps ON ps.NumProd_psc = up.Prod_unid
               INNER JOIN Empresas e ON e.Codigo_emp = up.Empresa_unid
        WHERE  up.Empresa_unid IN (6) 
               AND NumProd_psc = 605 
               AND Identificador_unid IS NOT NULL
        ORDER BY up.Prod_unid, up.Identificador_unid
        """
        
        df = pd.read_sql(query, conn)
        
        # Tratar valores nulos
        df['ValorTerreno'] = df['ValorTerreno'].fillna(0)
        df['AreaM2'] = df['AreaM2'].fillna(0)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao buscar lotes: {e}")
        return pd.DataFrame()

def formatar_moeda(valor):
    """Formata valor em moeda brasileira"""
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def calcular_simulacao(valor_terreno, parcelas, sinal_percent=5):
    """Calcula simulação de venda baseada no número de parcelas"""
    sinal = valor_terreno * (sinal_percent / 100)
    saldo = valor_terreno - sinal  # Valor restante após o sinal
    
    simulacoes = []
    
    if 2 <= parcelas <= 36:
        # Plano Fixo - sem reajustes
        valor_parcela = saldo / parcelas
        simulacoes.append({
            'Plano': f'{parcelas}x Fixas',
            'Sinal': sinal,
            'Parcelas': parcelas,
            'Valor_Parcela': valor_parcela,
            'Total_Financiado': saldo,  # Apenas o saldo, sem reajustes
            'Total_Geral': valor_terreno,  # Sinal + saldo = valor original
            'Tipo': 'Fixo'
        })
    
    elif 37 <= parcelas <= 200:
        # Planos Reajustáveis - mostrar valor inicial da parcela (sem reajuste visível)
        valor_parcela_inicial = saldo / parcelas  # Valor limpo da parcela
        simulacoes.append({
            'Plano': f'{parcelas}x Reajustáveis',
            'Sinal': sinal,
            'Parcelas': parcelas,
            'Valor_Parcela': valor_parcela_inicial,  # Valor inicial sem reajuste
            'Total_Financiado': saldo,  # Valor limpo, reajuste será aplicado depois
            'Total_Geral': valor_terreno,  # Valor original do terreno
            'Tipo': 'Reajustável'
        })
    
    return simulacoes

def calcular_avista(valor_terreno, sinal_percent=5):
    """Calcula opção de compra à vista com 20% de desconto no saldo"""
    sinal = valor_terreno * (sinal_percent / 100)
    saldo = valor_terreno - sinal
    desconto_saldo = saldo * 0.20  # 20% de desconto no saldo
    saldo_com_desconto = saldo - desconto_saldo
    valor_final = sinal + saldo_com_desconto
    
    return {
        'Sinal': sinal,
        'Saldo_Original': saldo,
        'Desconto': desconto_saldo,
        'Saldo_Final': saldo_com_desconto,
        'Valor_Final': valor_final,
        'Economia': valor_terreno - valor_final
    }

def criar_dashboard_vendas(df):
    """Cria dashboard visual das vendas"""
    # Gráfico de pizza - Status
    status_counts = df['Status_terreno'].value_counts()
    
    fig_pizza = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="📊 Distribuição por Status",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Gráfico de barras - Valores por Status
    status_valores = df.groupby('Status_terreno')['ValorTerreno'].sum().reset_index()
    
    fig_barras = px.bar(
        status_valores,
        x='Status_terreno',
        y='ValorTerreno',
        title="💰 Valor Total por Status",
        color='Status_terreno',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Corrigir formatação do eixo Y
    fig_barras.update_layout(
        yaxis=dict(tickformat=',.0f'),
        xaxis_title="Status",
        yaxis_title="Valor (R$)"
    )
    
    return fig_pizza, fig_barras

def gerar_proposta_simples(lote, simulacoes, avista, parcelas_sinal, tipo_simulacao):
    """Gera proposta comercial simples"""
    data_atual = datetime.now().strftime('%d/%m/%Y')
    
    if parcelas_sinal == 1:
        texto_sinal = f"Sinal (5%): {formatar_moeda(simulacoes[0]['Sinal'])} - À vista"
    else:
        valor_parcela_sinal = simulacoes[0]['Sinal'] / parcelas_sinal
        texto_sinal = f"Sinal (5%): {formatar_moeda(simulacoes[0]['Sinal'])} - {parcelas_sinal}x de {formatar_moeda(valor_parcela_sinal)}"
    
    if tipo_simulacao == 'avista' and avista:
        proposta = f"""
PROPOSTA COMERCIAL - OPÇÃO À VISTA
==================================

Data: {data_atual}

DADOS DO LOTE:
- Identificador: {lote['Identificador']}
- Endereço: {lote['Endereco']}
- Área: {lote['AreaM2']:.2f} m²
- Valor Original: {formatar_moeda(lote['ValorTerreno'])}

CONDIÇÕES À VISTA (20% DESCONTO NO SALDO):
- {texto_sinal}
- Saldo Original: {formatar_moeda(avista['Saldo_Original'])}
- Desconto (20%): -{formatar_moeda(avista['Desconto'])}
- VALOR FINAL: {formatar_moeda(avista['Valor_Final'])}
- ECONOMIA: {formatar_moeda(avista['Economia'])}

LIBERAÇÃO PARA CONSTRUÇÃO:
- Após pagamento completo do sinal

Esta proposta é válida por 15 dias.
        """
    else:
        proposta = f"""
PROPOSTA COMERCIAL - PARCELADO
==============================

Data: {data_atual}

DADOS DO LOTE:
- Identificador: {lote['Identificador']}
- Endereço: {lote['Endereco']}
- Área: {lote['AreaM2']:.2f} m²
- Valor: {formatar_moeda(lote['ValorTerreno'])}

CONDIÇÕES DE PAGAMENTO:
- Plano: {simulacoes[0]['Plano']}
- {texto_sinal}
- Parcelas: {simulacoes[0]['Parcelas']}x de {formatar_moeda(simulacoes[0]['Valor_Parcela'])}
- Total: {formatar_moeda(simulacoes[0]['Total_Geral'])}

LIBERAÇÃO PARA CONSTRUÇÃO:
- Após pagamento completo do sinal

OBSERVAÇÕES:
- Reajustes conforme contrato
- Esta proposta é válida por 15 dias.
        """
    
    return proposta

def gerar_orcamento_completo(lote, simulacoes, avista, parcelas_sinal, tipo_simulacao):
    """Gera orçamento completo estruturado para o cliente"""
    data_atual = datetime.now().strftime('%d/%m/%Y')
    
    if parcelas_sinal == 1:
        texto_sinal = f"À vista: {formatar_moeda(simulacoes[0]['Sinal'])}"
        parcelas_sinal_texto = "1x (à vista)"
    else:
        valor_parcela_sinal = simulacoes[0]['Sinal'] / parcelas_sinal
        texto_sinal = f"{parcelas_sinal}x de {formatar_moeda(valor_parcela_sinal)}"
        parcelas_sinal_texto = f"{parcelas_sinal}x de {formatar_moeda(valor_parcela_sinal)}"
    
    orcamento = f"""
╔══════════════════════════════════════════════════════════════════╗
║                     ORÇAMENTO COMPLETO - LOTE                   ║
╚══════════════════════════════════════════════════════════════════╝

📅 Data: {data_atual}
🏢 Empreendimento: {lote.get('Empreendimento', 'Loteamento Valle Prime')}

╔══════════════════════════════════════════════════════════════════╗
║                        DADOS DO LOTE                            ║
╚══════════════════════════════════════════════════════════════════╝

🏠 Identificador: {lote['Identificador']}
📍 Endereço: {lote['Endereco']}
📏 Área Total: {lote['AreaM2']:.2f} m²
💰 Valor do Lote: {formatar_moeda(lote['ValorTerreno'])}

╔══════════════════════════════════════════════════════════════════╗
║                    OPÇÕES DE PAGAMENTO                          ║
╚══════════════════════════════════════════════════════════════════╝

┌─ OPÇÃO 1: À VISTA COM DESCONTO ─────────────────────────────────┐
│                                                                 │
│ 💵 Sinal (5%): {formatar_moeda(avista['Sinal']):<20} │
│    Parcelamento: {parcelas_sinal_texto:<35} │
│                                                                 │
│ 💸 Saldo Original: {formatar_moeda(avista['Saldo_Original']):<28} │
│ 🎯 Desconto (20%): -{formatar_moeda(avista['Desconto']):<27} │
│ ═══════════════════════════════════════════════════════════════ │
│ 🏆 VALOR FINAL À VISTA: {formatar_moeda(avista['Valor_Final']):<23} │
│ 💰 ECONOMIA TOTAL: {formatar_moeda(avista['Economia']):<28} │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─ OPÇÃO 2: PARCELADO ────────────────────────────────────────────┐
│                                                                 │
│ 📋 Plano Escolhido: {simulacoes[0]['Plano']:<30} │
│ 📈 Tipo: {simulacoes[0]['Tipo']:<42} │
│                                                                 │
│ 💵 Sinal (5%): {formatar_moeda(simulacoes[0]['Sinal']):<32} │
│    Parcelamento: {parcelas_sinal_texto:<35} │
│                                                                 │
│ 📊 Parcelas do Terreno: {simulacoes[0]['Parcelas']}x de {formatar_moeda(simulacoes[0]['Valor_Parcela']):<15} │
│ 🎯 Total Financiado: {formatar_moeda(simulacoes[0]['Total_Financiado']):<27} │
│ ═══════════════════════════════════════════════════════════════ │
│ 🏆 TOTAL GERAL: {formatar_moeda(simulacoes[0]['Total_Geral']):<32} │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════╗
║                   DOCUMENTAÇÃO NECESSÁRIA                       ║
╚══════════════════════════════════════════════════════════════════╝

📋 DOCUMENTOS OBRIGATÓRIOS:
   • Documento de Identificação (RG, CNH, etc.)
   • Comprovante de Residência
   • Certidão de Nascimento ou Casamento

👫 CASO SEJA CASADO(A) LEGALMENTE:
   • Documentação completa do cônjuge também

╔══════════════════════════════════════════════════════════════════╗
║                    INFORMAÇÕES IMPORTANTES                      ║
╚══════════════════════════════════════════════════════════════════╝

🏗️ LIBERAÇÃO PARA CONSTRUÇÃO:
   • Após pagamento completo do sinal

📈 REAJUSTES (OPÇÃO PARCELADA):
   • Parcelas com reajuste anual conforme índices
   • Valores mostrados são iniciais
   • Detalhes serão explicados no contrato

⏰ VALIDADE:
   • Esta proposta é válida por 15 dias

╔══════════════════════════════════════════════════════════════════╗
║                         CONTATO                                 ║
╚══════════════════════════════════════════════════════════════════╝

📞 Para mais informações, entre em contato conosco!
🤝 Estamos à disposição para esclarecer dúvidas.

═══════════════════════════════════════════════════════════════════
    """
    
    return orcamento

def main():
    # Usar uma chave única baseada na inicialização da sessão
    if 'app_instance_id' not in st.session_state:
        st.session_state.app_instance_id = str(int(datetime.now().timestamp() * 1000000))
    
    # Gerar timestamp único baseado na instância
    timestamp = st.session_state.app_instance_id
    
    # CSS customizado
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏡 Sistema de Gestão de Lotes</h1>
        <h3>Gerenciamento Completo de Empreendimentos</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Conectar ao banco
    conn = conectar_banco_dados()
    if not conn:
        st.stop()
    
    # Buscar dados (sem cache para evitar duplicação)
    with st.spinner("🔄 Carregando dados do sistema..."):
        df = buscar_lotes(conn)
    
    if df.empty:
        st.error("❌ Nenhum dado encontrado")
        return
    
    # Sidebar - apenas informações básicas
    st.sidebar.header("ℹ️ Informações do Sistema")
    st.sidebar.info(f"📊 Total de Lotes: {len(df)}")
    st.sidebar.info(f"💰 Valor Total: {formatar_moeda(df['ValorTerreno'].sum())}")
    
    # Estatísticas rápidas na sidebar
    st.sidebar.markdown("**📈 Resumo por Status:**")
    for status, count in df['Status_terreno'].value_counts().items():
        st.sidebar.write(f"• {status}: {count}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🏢 Sistema de Gestão de Lotes**")
    st.sidebar.markdown("*Versão 1.0*")
    
    # Usar todos os dados
    df_filtrado = df.copy()
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_lotes = len(df_filtrado)
        st.metric("🏗️ Total de Lotes", total_lotes)
    
    with col2:
        valor_total = df_filtrado['ValorTerreno'].sum()
        st.metric("💰 Valor Total", formatar_moeda(valor_total))
    
    with col3:
        disponiveis = len(df_filtrado[df_filtrado['Status_terreno'] == 'Disponível'])
        st.metric("✅ Disponíveis", disponiveis)
    
    with col4:
        vendidos = len(df_filtrado[df_filtrado['Status_terreno'].isin(['Vendido', 'Quitado'])])
        st.metric("🏆 Vendidos/Quitados", vendidos)
    
    st.markdown("---")
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🏠 Dashboard", "✅ Disponíveis", "🏆 Vendidos", "💎 Quitados", 
        "🔶 Reservados", "❌ Fora de Venda", "⏸️ Suspensos", "🧮 Simulador"
    ])
    
    # TAB 1: Dashboard
    with tab1:
        st.subheader("📊 Visão Geral do Empreendimento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pizza, fig_barras = criar_dashboard_vendas(df_filtrado)
            # Usar hash dos dados para garantir uniqueness
            data_hash = hash(str(df_filtrado.shape) + timestamp)
            st.plotly_chart(fig_pizza, use_container_width=True, key=f"pizza_{abs(data_hash)}")
        
        with col2:
            data_hash2 = hash(str(df_filtrado.shape) + timestamp + "barras")
            st.plotly_chart(fig_barras, use_container_width=True, key=f"barras_{abs(data_hash2)}")
        
        # Estatísticas detalhadas
        st.subheader("📈 Estatísticas Detalhadas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**📊 Por Status:**")
            status_stats = df_filtrado['Status_terreno'].value_counts()
            for status, count in status_stats.items():
                percent = (count / len(df_filtrado)) * 100
                st.write(f"• {status}: {count} ({percent:.1f}%)")
        
        with col2:
            st.write("**💰 Valores:**")
            st.write(f"• Maior Valor: {formatar_moeda(df_filtrado['ValorTerreno'].max())}")
            st.write(f"• Menor Valor: {formatar_moeda(df_filtrado['ValorTerreno'].min())}")
            st.write(f"• Valor Médio: {formatar_moeda(df_filtrado['ValorTerreno'].mean())}")
            st.write(f"• Mediana: {formatar_moeda(df_filtrado['ValorTerreno'].median())}")
        
        with col3:
            st.write("**📏 Áreas:**")
            st.write(f"• Maior Área: {df_filtrado['AreaM2'].max():.2f} m²")
            st.write(f"• Menor Área: {df_filtrado['AreaM2'].min():.2f} m²")
            st.write(f"• Área Média: {df_filtrado['AreaM2'].mean():.2f} m²")
            st.write(f"• Área Total: {df_filtrado['AreaM2'].sum():.2f} m²")
    
    # TAB 2: Disponíveis
    with tab2:
        disponiveis_df = df_filtrado[df_filtrado['Status_terreno'] == 'Disponível']
        
        st.subheader(f"✅ Lotes Disponíveis ({len(disponiveis_df)} unidades)")
        
        if not disponiveis_df.empty:
            # Ordenar por valor
            disponiveis_df = disponiveis_df.sort_values('ValorTerreno')
            
            # Adicionar colunas formatadas
            disponiveis_display = disponiveis_df.copy()
            disponiveis_display['Valor_Formatado'] = disponiveis_display['ValorTerreno'].apply(formatar_moeda)
            disponiveis_display['Area_Formatada'] = disponiveis_display['AreaM2'].apply(lambda x: f"{x:.2f} m²")
            
            # Selecionar colunas para exibição
            cols_display = ['Identificador', 'Endereco', 'Area_Formatada', 'Valor_Formatado', 'Status_terreno']
            st.dataframe(
                disponiveis_display[cols_display],
                use_container_width=True,
                height=400
            )
            
            # Estatísticas dos disponíveis
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💰 Valor Total Disponível", formatar_moeda(disponiveis_df['ValorTerreno'].sum()))
            
            with col2:
                st.metric("📊 Valor Médio", formatar_moeda(disponiveis_df['ValorTerreno'].mean()))
            
            with col3:
                st.metric("📏 Área Total", f"{disponiveis_df['AreaM2'].sum():.2f} m²")
            
            # Download
            csv = disponiveis_df.to_csv(index=False)
            st.download_button(
                "📥 Baixar Disponíveis (CSV)",
                csv,
                "lotes_disponiveis.csv",
                "text/csv",
                key=f"download_csv_{timestamp}"
            )
        else:
            st.info("📋 Nenhum lote disponível")
    
    # TAB 3: Vendidos
    with tab3:
        vendidos_df = df_filtrado[df_filtrado['Status_terreno'] == 'Vendido']
        
        st.subheader(f"🏆 Lotes Vendidos ({len(vendidos_df)} unidades)")
        
        if not vendidos_df.empty:
            vendidos_display = vendidos_df.copy()
            vendidos_display['Valor_Formatado'] = vendidos_display['ValorTerreno'].apply(formatar_moeda)
            vendidos_display['Area_Formatada'] = vendidos_display['AreaM2'].apply(lambda x: f"{x:.2f} m²")
            
            cols_display = ['Identificador', 'Endereco', 'Area_Formatada', 'Valor_Formatado', 'Status_terreno']
            st.dataframe(vendidos_display[cols_display], use_container_width=True, height=400)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Receita Vendas", formatar_moeda(vendidos_df['ValorTerreno'].sum()))
            with col2:
                st.metric("📊 Ticket Médio", formatar_moeda(vendidos_df['ValorTerreno'].mean()))
            with col3:
                percent_vendido = (len(vendidos_df) / len(df)) * 100
                st.metric("📈 % Vendido", f"{percent_vendido:.1f}%")
        else:
            st.info("📋 Nenhum lote vendido")
    
    # TAB 4: Quitados
    with tab4:
        quitados_df = df_filtrado[df_filtrado['Status_terreno'] == 'Quitado']
        
        st.subheader(f"💎 Lotes Quitados ({len(quitados_df)} unidades)")
        
        if not quitados_df.empty:
            quitados_display = quitados_df.copy()
            quitados_display['Valor_Formatado'] = quitados_display['ValorTerreno'].apply(formatar_moeda)
            quitados_display['Area_Formatada'] = quitados_display['AreaM2'].apply(lambda x: f"{x:.2f} m²")
            
            cols_display = ['Identificador', 'Endereco', 'Area_Formatada', 'Valor_Formatado', 'Status_terreno']
            st.dataframe(quitados_display[cols_display], use_container_width=True, height=400)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Receita Quitada", formatar_moeda(quitados_df['ValorTerreno'].sum()))
            with col2:
                st.metric("📊 Ticket Médio", formatar_moeda(quitados_df['ValorTerreno'].mean()))
            with col3:
                percent_quitado = (len(quitados_df) / len(df)) * 100
                st.metric("💎 % Quitado", f"{percent_quitado:.1f}%")
        else:
            st.info("📋 Nenhum lote quitado")
    
    # TAB 5: Reservados
    with tab5:
        reservados_df = df_filtrado[df_filtrado['Status_terreno'] == 'Reservado']
        
        st.subheader(f"🔶 Lotes Reservados ({len(reservados_df)} unidades)")
        
        if not reservados_df.empty:
            reservados_display = reservados_df.copy()
            reservados_display['Valor_Formatado'] = reservados_display['ValorTerreno'].apply(formatar_moeda)
            reservados_display['Area_Formatada'] = reservados_display['AreaM2'].apply(lambda x: f"{x:.2f} m²")
            
            cols_display = ['Identificador', 'Endereco', 'Area_Formatada', 'Valor_Formatado', 'Status_terreno']
            st.dataframe(reservados_display[cols_display], use_container_width=True, height=400)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Valor Reservado", formatar_moeda(reservados_df['ValorTerreno'].sum()))
            with col2:
                st.metric("📊 Ticket Médio", formatar_moeda(reservados_df['ValorTerreno'].mean()))
            with col3:
                percent_reservado = (len(reservados_df) / len(df)) * 100
                st.metric("📈 % Reservado", f"{percent_reservado:.1f}%")
        else:
            st.info("📋 Nenhum lote reservado")
    
    # TAB 6: Fora de Venda
    with tab6:
        fora_venda_df = df_filtrado[df_filtrado['Status_terreno'] == 'Fora de venda']
        
        st.subheader(f"❌ Lotes Fora de Venda ({len(fora_venda_df)} unidades)")
        
        if not fora_venda_df.empty:
            fora_venda_display = fora_venda_df.copy()
            fora_venda_display['Valor_Formatado'] = fora_venda_display['ValorTerreno'].apply(formatar_moeda)
            fora_venda_display['Area_Formatada'] = fora_venda_display['AreaM2'].apply(lambda x: f"{x:.2f} m²")
            
            cols_display = ['Identificador', 'Endereco', 'Area_Formatada', 'Valor_Formatado', 'Status_terreno']
            st.dataframe(fora_venda_display[cols_display], use_container_width=True, height=400)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Valor Fora de Venda", formatar_moeda(fora_venda_df['ValorTerreno'].sum()))
            with col2:
                st.metric("📊 Ticket Médio", formatar_moeda(fora_venda_df['ValorTerreno'].mean()))
            with col3:
                percent_fora_venda = (len(fora_venda_df) / len(df)) * 100
                st.metric("📈 % Fora de Venda", f"{percent_fora_venda:.1f}%")
        else:
            st.info("📋 Nenhum lote fora de venda")
    
    # TAB 7: Suspensos
    with tab7:
        suspensos_df = df_filtrado[df_filtrado['Status_terreno'] == 'Suspenso']
        
        st.subheader(f"⏸️ Lotes Suspensos ({len(suspensos_df)} unidades)")
        
        if not suspensos_df.empty:
            suspensos_display = suspensos_df.copy()
            suspensos_display['Valor_Formatado'] = suspensos_display['ValorTerreno'].apply(formatar_moeda)
            suspensos_display['Area_Formatada'] = suspensos_display['AreaM2'].apply(lambda x: f"{x:.2f} m²")
            
            cols_display = ['Identificador', 'Endereco', 'Area_Formatada', 'Valor_Formatado', 'Status_terreno']
            st.dataframe(suspensos_display[cols_display], use_container_width=True, height=400)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Valor Suspenso", formatar_moeda(suspensos_df['ValorTerreno'].sum()))
            with col2:
                st.metric("📊 Ticket Médio", formatar_moeda(suspensos_df['ValorTerreno'].mean()))
            with col3:
                percent_suspenso = (len(suspensos_df) / len(df)) * 100
                st.metric("📈 % Suspenso", f"{percent_suspenso:.1f}%")
        else:
            st.info("📋 Nenhum lote suspenso")
    
    # TAB 8: Simulador
    with tab8:
        st.subheader("🧮 Simulador de Vendas")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Selecione um lote disponível:**")
            
            lotes_disponiveis = df[df['Status_terreno'] == 'Disponível']
            
            if not lotes_disponiveis.empty:
                lote_opcoes = {}
                for _, row in lotes_disponiveis.iterrows():
                    key = f"{row['Identificador']} - {formatar_moeda(row['ValorTerreno'])}"
                    lote_opcoes[key] = row
                
                lote_selecionado_key = st.selectbox("🏠 Lote", list(lote_opcoes.keys()), key=f"lote_select_{timestamp}")
                lote_selecionado = lote_opcoes[lote_selecionado_key]
                
                # Parâmetros da simulação
                st.markdown("**Parâmetros:**")
                st.info("💰 Sinal fixo: 5%")
                
                # Escolha das parcelas do sinal
                parcelas_sinal = st.selectbox(
                    "💳 Parcelas do Sinal",
                    options=[1, 2, 3, 4, 5],
                    index=0,
                    help="Escolha em quantas vezes dividir o sinal",
                    key=f"parcelas_sinal_{timestamp}"
                )
                
                # Barra de parcelas
                parcelas = st.slider(
                    "📊 Quantidade de Parcelas",
                    min_value=2,
                    max_value=200,
                    value=36,
                    step=1,
                    key=f"parcelas_slider_{timestamp}"
                )
                
                # Mostrar tipo de plano automaticamente
                if 2 <= parcelas <= 36:
                    tipo_plano = "Fixo (sem reajustes)"
                    cor_plano = "🟢"
                elif 37 <= parcelas <= 200:
                    tipo_plano = "Reajustável"
                    cor_plano = "🟡"
                
                st.markdown(f"**{cor_plano} Tipo de Plano:** {tipo_plano}")
                
                # Informações importantes sobre o sinal
                st.markdown("---")
                st.markdown("**ℹ️ Informações Importantes:**")
                if parcelas_sinal == 1:
                    st.info("💰 **Sinal:** À vista")
                else:
                    st.info(f"💰 **Sinal:** Dividido em {parcelas_sinal}x")
                st.success("🏗️ **Liberação para Construção:** Após pagamento completo do sinal")
                
                # Botão para calcular simulação parcelada
                if st.button("🧮 Calcular Simulação Parcelada", type="primary", key=f"btn_parcelada_{timestamp}"):
                    valor_terreno = lote_selecionado['ValorTerreno']
                    simulacoes = calcular_simulacao(valor_terreno, parcelas)
                    avista = calcular_avista(valor_terreno)
                    
                    st.session_state['simulacao_atual'] = {
                        'lote': lote_selecionado,
                        'simulacoes': simulacoes,
                        'avista': avista,
                        'parcelas': parcelas,
                        'parcelas_sinal': parcelas_sinal,
                        'tipo_simulacao': 'parcelada'
                    }
                
                # Botão separado para opção à vista
                st.markdown("---")
                if st.button("💰 Ver Opção À Vista (20% Desconto)", type="secondary", key=f"btn_avista_{timestamp}"):
                    valor_terreno = lote_selecionado['ValorTerreno']
                    simulacoes = calcular_simulacao(valor_terreno, parcelas)
                    avista = calcular_avista(valor_terreno)
                    
                    st.session_state['simulacao_atual'] = {
                        'lote': lote_selecionado,
                        'simulacoes': simulacoes,
                        'avista': avista,
                        'parcelas': parcelas,
                        'parcelas_sinal': parcelas_sinal,
                        'tipo_simulacao': 'avista'
                    }
            else:
                st.warning("Nenhum lote disponível para simulação")
        
        with col2:
            if 'simulacao_atual' in st.session_state:
                sim_data = st.session_state['simulacao_atual']
                lote = sim_data['lote']
                simulacoes = sim_data['simulacoes']
                avista = sim_data.get('avista', {})
                parcelas_sinal = sim_data.get('parcelas_sinal', 1)
                tipo_simulacao = sim_data.get('tipo_simulacao', 'parcelada')
                
                st.success(f"📊 Simulação para: {lote['Identificador']}")
                
                # Mostrar apenas a simulação selecionada
                if tipo_simulacao == 'avista' and avista:
                    # Opção À Vista
                    st.markdown("""
                    ### 💰 Opção À Vista (20% Desconto no Saldo)
                    
                    **Detalhes do Lote:**
                    - 🏠 Identificador: {Identificador}
                    - 📏 Área: {Area:.2f} m²
                    - 🏡 Endereço: {Endereco}
                    - 💰 Valor Original: {Valor_Original}
                    
                    **Condições À Vista:**
                    - 💵 Sinal (5%): {Sinal}
                    - 💸 Saldo Original: {Saldo_Original}
                    - 🎯 Desconto (20%): -{Desconto}
                    - 💚 Saldo Final: {Saldo_Final}
                    - 🏆 **VALOR FINAL: {Valor_Final}**
                    - 💰 **ECONOMIA: {Economia}**
                    """.format(
                        Identificador=lote['Identificador'],
                        Area=lote['AreaM2'],
                        Endereco=lote['Endereco'],
                        Valor_Original=formatar_moeda(lote['ValorTerreno']),
                        Sinal=formatar_moeda(avista['Sinal']),
                        Saldo_Original=formatar_moeda(avista['Saldo_Original']),
                        Desconto=formatar_moeda(avista['Desconto']),
                        Saldo_Final=formatar_moeda(avista['Saldo_Final']),
                        Valor_Final=formatar_moeda(avista['Valor_Final']),
                        Economia=formatar_moeda(avista['Economia'])
                    ))
                    
                    # Informações sobre pagamento à vista
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if parcelas_sinal == 1:
                            st.info(f"💰 **Sinal:** À vista - {formatar_moeda(avista['Sinal'])}")
                        else:
                            valor_parcela_sinal = avista['Sinal'] / parcelas_sinal
                            st.info(f"💰 **Entrada:** {parcelas_sinal}x de {formatar_moeda(valor_parcela_sinal)}")
                    with col_b:
                        st.success("🏗️ **Liberação:** Construção após sinal quitado")
                    
                    st.success("🎉 **Pagamento à vista do saldo com 20% de desconto!**")
                
                else:
                    # Simulação Parcelada
                    for sim in simulacoes:
                        st.markdown(f"""
                        ### 📋 {sim['Plano']}
                        
                        **Detalhes do Lote:**
                        - 🏠 Identificador: {lote['Identificador']}
                        - 📏 Área: {lote['AreaM2']:.2f} m²
                        - 🏡 Endereço: {lote['Endereco']}
                        - 💰 Valor Total: {formatar_moeda(lote['ValorTerreno'])}
                        
                        **Condições de Pagamento:**
                        - 💵 Sinal (5%): {formatar_moeda(sim['Sinal'])}
                        - 📊 Parcelas do Terreno: {sim['Parcelas']}x
                        - 💳 Valor da Parcela: {formatar_moeda(sim['Valor_Parcela'])}
                        - 🎯 Total Financiado: {formatar_moeda(sim['Total_Financiado'])}
                        - 🏆 **Total Geral: {formatar_moeda(sim['Total_Geral'])}**
                        - 📈 **Tipo: {sim['Tipo']}**
                        """)
                        
                        # Informações adicionais sobre pagamento
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if parcelas_sinal == 1:
                                st.info(f"💰 **Sinal:** À vista - {formatar_moeda(sim['Sinal'])}")
                            else:
                                valor_parcela_sinal = sim['Sinal'] / parcelas_sinal
                                st.info(f"💰 **Sinal:** {parcelas_sinal}x de {formatar_moeda(valor_parcela_sinal)}")
                        with col_b:
                            st.success("🏗️ **Liberação:** Construção após sinal quitado")
                        
                        if sim['Tipo'] != 'Fixo':
                            st.warning("📈 *Parcelas com reajuste anual aplicado durante o pagamento (detalhes a serem explicados)")
                            st.info("💡 *Valores das parcelas mostrados são iniciais, sem reajuste já aplicado")
                
                # Seção de Documentação Necessária
                st.markdown("---")
                st.markdown("### 📄 Documentação Necessária")
                st.info("""
                **Para adquirir o lote, será necessário apresentar:**
                
                📋 **Documentos Obrigatórios:**
                • Documento de Identificação (RG, CNH, etc.)
                • Comprovante de Residência
                • Certidão de Nascimento ou Casamento
                
                👫 **Caso seja casado(a) legalmente:**
                • Documentação completa do cônjuge também
                """)
                
                st.markdown("---")
                
                # Botões de ação
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("📄 Gerar Proposta Simples", key=f"btn_proposta_{timestamp}"):
                        proposta_simples = gerar_proposta_simples(lote, simulacoes, avista, parcelas_sinal, tipo_simulacao)
                        st.download_button(
                            "📥 Baixar Proposta",
                            proposta_simples,
                            f"proposta_{lote['Identificador'].replace(' ', '_')}.txt",
                            "text/plain",
                            key=f"download_proposta_{timestamp}"
                        )
                
                with col_btn2:
                    if st.button("📊 Gerar Orçamento Completo", key=f"btn_orcamento_{timestamp}"):
                        orcamento_completo = gerar_orcamento_completo(lote, simulacoes, avista, parcelas_sinal, tipo_simulacao)
                        
                        # Mostrar o orçamento na tela
                        st.markdown("### 📋 Orçamento Completo")
                        st.text_area(
                            "Copie o texto abaixo:",
                            orcamento_completo,
                            height=400,
                            help="Selecione todo o texto e copie para enviar ao cliente",
                            key=f"textarea_{timestamp}"
                        )
                        
                        # Botão de download
                        st.download_button(
                            "📥 Baixar Orçamento Completo",
                            orcamento_completo,
                            f"orcamento_completo_{lote['Identificador'].replace(' ', '_')}.txt",
                            "text/plain",
                            key=f"download_orcamento_{timestamp}"
                        )
            else:
                st.info("👆 Selecione um lote e calcule a simulação")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()