"""
Calculadora Matemática e Financeira Completa
Desenvolvido por: Vinicius Dev

Sistema completo com múltiplas calculadoras:
- Regra de Três
- Cálculo de Desconto/Markup
- Juros Simples e Compostos
- Porcentagem
- Conversões
- Calculadora Básica

Versão: 2.0
Data: 2025
"""

import streamlit as st
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import math
from datetime import datetime, timedelta
import locale

# Configuração da página
st.set_page_config(
    page_title="Calculadora Completa",
    page_icon="🧮",
    layout="wide"
)

# Configurar locale para Brasil (se disponível)
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

# CSS customizado
st.markdown("""
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
    }
    
    .main-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .calc-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .result-box {
        background: linear-gradient(135deg, #FF6B6B 0%, #ee5a52 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3em;
        font-weight: bold;
        margin: 15px 0;
    }
    
    .formula-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
    }
    
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .success-box {
        background-color: #e8f5e8;
        border-left: 4px solid #4CAF50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    /* Estilo para inputs com formatação brasileira */
    .stNumberInput input {
        text-align: right;
        font-family: monospace;
    }
    </style>
    
    <div class="dev-signature">
        💻 Desenvolvido por: Vinicius Dev
    </div>
""", unsafe_allow_html=True)

def formatar_numero_brasileiro(numero):
    """Formata número para padrão brasileiro com vírgula decimal"""
    if numero is None:
        return "0"
    
    try:
        decimal_num = Decimal(str(numero))
        
        if decimal_num == decimal_num.to_integral_value():
            # Número inteiro
            return f"{int(decimal_num):,}".replace(",", ".")
        else:
            # Número decimal - usar vírgula como separador decimal
            rounded = decimal_num.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            formatted = f"{float(rounded):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return formatted
    except:
        return str(numero)

def formatar_moeda_brasileira(numero):
    """Formata número como moeda brasileira"""
    if numero is None:
        return "R$ 0,00"
    
    try:
        formatted = formatar_numero_brasileiro(numero)
        return f"R$ {formatted}"
    except:
        return f"R$ {numero}"

def formatar_porcentagem(numero):
    """Formata porcentagem com vírgula decimal"""
    try:
        return f"{float(numero):,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00%"

def converter_input_brasileiro(valor_str):
    """Converte string de entrada brasileira para float"""
    if not valor_str:
        return 0.0
    
    try:
        # Remove espaços e substitui vírgula por ponto
        valor_limpo = str(valor_str).replace(" ", "").replace(".", "").replace(",", ".")
        return float(valor_limpo)
    except:
        return 0.0

# =============== CALCULADORA DE DESCONTO/MARKUP ===============
def calcular_desconto_reverso(valor_inicial, valor_final):
    """Calcula qual desconto aplicar no valor inicial para chegar no final"""
    try:
        if valor_inicial == 0:
            return None, "❌ Valor inicial não pode ser zero!"
        
        desconto_percentual = ((valor_inicial - valor_final) / valor_inicial) * 100
        valor_desconto = valor_inicial - valor_final
        
        return {
            'desconto_percentual': desconto_percentual,
            'valor_desconto': valor_desconto,
            'tipo': 'desconto' if desconto_percentual > 0 else 'acréscimo'
        }, None
        
    except Exception as e:
        return None, f"❌ Erro no cálculo: {str(e)}"

def calcular_markup(custo, margem_percentual):
    """Calcula preço de venda com base no custo e margem"""
    try:
        preco_venda = custo * (1 + margem_percentual / 100)
        lucro = preco_venda - custo
        return preco_venda, lucro, None
    except Exception as e:
        return None, None, f"❌ Erro no cálculo: {str(e)}"

# =============== CALCULADORAS DE JUROS ===============
def calcular_juros_simples(capital, taxa, tempo):
    """Calcula juros simples"""
    try:
        juros = capital * (taxa / 100) * tempo
        montante = capital + juros
        
        return {
            'juros': juros,
            'montante': montante,
            'capital': capital,
            'taxa': taxa,
            'tempo': tempo
        }, None
        
    except Exception as e:
        return None, f"❌ Erro no cálculo: {str(e)}"

def calcular_juros_compostos(capital, taxa, tempo):
    """Calcula juros compostos"""
    try:
        montante = capital * ((1 + taxa / 100) ** tempo)
        juros = montante - capital
        
        return {
            'juros': juros,
            'montante': montante,
            'capital': capital,
            'taxa': taxa,
            'tempo': tempo
        }, None
        
    except Exception as e:
        return None, f"❌ Erro no cálculo: {str(e)}"

# =============== CALCULADORA DE PORCENTAGEM ===============
def calcular_porcentagem(valor, percentual):
    """Calcula x% de um valor"""
    try:
        resultado = valor * (percentual / 100)
        return resultado, None
    except Exception as e:
        return None, f"❌ Erro no cálculo: {str(e)}"

def calcular_variacao_percentual(valor_inicial, valor_final):
    """Calcula variação percentual entre dois valores"""
    try:
        if valor_inicial == 0:
            return None, "❌ Valor inicial não pode ser zero!"
        
        variacao = ((valor_final - valor_inicial) / valor_inicial) * 100
        return variacao, None
        
    except Exception as e:
        return None, f"❌ Erro no cálculo: {str(e)}"

# =============== REGRA DE TRÊS ===============
def calcular_regra_tres_simples(a, b, c):
    """Calcula regra de três simples"""
    try:
        if a == 0:
            return None, "❌ O primeiro valor não pode ser zero!"
        
        x = (b * c) / a
        return x, None
    except Exception as e:
        return None, f"❌ Erro no cálculo: {str(e)}"

# =============== CONVERSÕES ===============
def converter_temperatura(valor, de_unidade, para_unidade):
    """Converte temperaturas"""
    try:
        # Converter tudo para Celsius primeiro
        if de_unidade == "Fahrenheit":
            celsius = (valor - 32) * 5/9
        elif de_unidade == "Kelvin":
            celsius = valor - 273.15
        else:
            celsius = valor
        
        # Converter de Celsius para a unidade desejada
        if para_unidade == "Fahrenheit":
            resultado = celsius * 9/5 + 32
        elif para_unidade == "Kelvin":
            resultado = celsius + 273.15
        else:
            resultado = celsius
            
        return resultado, None
        
    except Exception as e:
        return None, f"❌ Erro na conversão: {str(e)}"

def main():
    # Cabeçalho principal
    st.title("🧮 Calculadora Matemática e Financeira")
    st.markdown("##### 🔧 *Desenvolvido por: Vinicius Dev*")
    
    # Card principal
    st.markdown("""
        <div class="main-card">
            <h3>🎯 Centro de Cálculos Completo</h3>
            <p>Todas as calculadoras que você precisa em um só lugar<br>
            <strong>Matemática • Financeira • Conversões • Utilitários</strong></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Menu principal em abas
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🧮 Regra de Três", 
        "💰 Desconto/Markup", 
        "📈 Juros", 
        "📊 Porcentagem",
        "🌡️ Conversões",
        "🔢 Calculadora",
        "📋 Histórico",
        "📚 Ajuda"
    ])
    
    # =============== ABA REGRA DE TRÊS ===============
    with tab1:
        st.markdown("""
            <div class="calc-card">
                <h3>📐 Regra de Três</h3>
                <p>Resolva problemas de proporcionalidade</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Tipo de proporção
        tipo_proporcao = st.radio(
            "📊 Tipo de Proporção:",
            ("Direta", "Inversa"),
            help="Direta: quando uma aumenta, a outra aumenta. Inversa: quando uma aumenta, a outra diminui."
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            a = st.number_input("Primeiro valor (A):", value=0.0, key="regra_a", format="%.2f")
        with col2:
            b = st.number_input("Segundo valor (B):", value=0.0, key="regra_b", format="%.2f")
        with col3:
            c = st.number_input("Terceiro valor (C):", value=0.0, key="regra_c", format="%.2f")
        
        # Representação visual
        if tipo_proporcao == "Direta":
            st.markdown(f"""
                <div class="formula-box">
                    <strong>Proporção Direta:</strong><br>
                    {formatar_numero_brasileiro(a)} está para {formatar_numero_brasileiro(b)}<br>
                    assim como {formatar_numero_brasileiro(c)} está para <strong>X</strong><br>
                    <em>X = (B × C) ÷ A = ({formatar_numero_brasileiro(b)} × {formatar_numero_brasileiro(c)}) ÷ {formatar_numero_brasileiro(a)}</em>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="formula-box">
                    <strong>Proporção Inversa:</strong><br>
                    {formatar_numero_brasileiro(a)} está para {formatar_numero_brasileiro(b)}<br>
                    assim como {formatar_numero_brasileiro(c)} está para <strong>X</strong> (inverso)<br>
                    <em>X = (A × B) ÷ C = ({formatar_numero_brasileiro(a)} × {formatar_numero_brasileiro(b)}) ÷ {formatar_numero_brasileiro(c)}</em>
                </div>
            """, unsafe_allow_html=True)
        
        if st.button("🧮 Calcular Regra de Três", type="primary"):
            if a == 0 or c == 0:
                st.error("❌ Os valores A e C não podem ser zero!")
            else:
                if tipo_proporcao == "Direta":
                    resultado, erro = calcular_regra_tres_simples(a, b, c)
                else:
                    resultado = (a * b) / c if c != 0 else None
                    erro = None if resultado else "Erro no cálculo"
                
                if erro:
                    st.error(erro)
                else:
                    st.markdown(f"""
                        <div class="result-box">
                            🎉 <strong>X = {formatar_numero_brasileiro(resultado)}</strong>
                        </div>
                    """, unsafe_allow_html=True)
    
    # =============== ABA DESCONTO/MARKUP ===============
    with tab2:
        st.markdown("""
            <div class="calc-card">
                <h3>💰 Desconto e Markup</h3>
                <p>Calcule descontos, acréscimos e margens de lucro</p>
            </div>
        """, unsafe_allow_html=True)
        
        subtab1, subtab2, subtab3 = st.tabs(["🔄 Desconto Reverso", "📈 Markup/Margem", "💸 Desconto Direto"])
        
        # Desconto Reverso (solicitado)
        with subtab1:
            st.markdown("### 🎯 Calcular Desconto Necessário")
            st.markdown("""
                <div class="info-box">
                    <strong>Cenário:</strong> Você tem um valor inicial e quer chegar a um valor final.<br>
                    <strong>Pergunta:</strong> "Qual desconto (%) devo aplicar?"
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Input com formato brasileiro
                valor_inicial_input = st.text_input(
                    "💵 Valor Inicial (R$):",
                    value="0,00",
                    help="Digite o valor usando vírgula para decimais (ex: 1.500,90)",
                    key="desc_inicial_br"
                )
                # Converter para float
                valor_inicial = converter_input_brasileiro(valor_inicial_input)
                st.caption(f"Valor convertido: {formatar_moeda_brasileira(valor_inicial)}")
            
            with col2:
                # Input com formato brasileiro
                valor_final_input = st.text_input(
                    "🎯 Valor Desejado (R$):",
                    value="0,00",
                    help="Digite o valor usando vírgula para decimais (ex: 1.200,00)",
                    key="desc_final_br"
                )
                # Converter para float
                valor_final = converter_input_brasileiro(valor_final_input)
                st.caption(f"Valor convertido: {formatar_moeda_brasileira(valor_final)}")
            
            if st.button("🔍 Calcular Desconto Necessário", type="primary"):
                resultado, erro = calcular_desconto_reverso(valor_inicial, valor_final)
                
                if erro:
                    st.error(erro)
                else:
                    tipo = resultado['tipo']
                    perc = abs(resultado['desconto_percentual'])
                    valor_desc = abs(resultado['valor_desconto'])
                    
                    if tipo == 'desconto':
                        st.markdown(f"""
                            <div class="result-box">
                                📉 <strong>Desconto de {formatar_porcentagem(perc)}</strong><br>
                                Valor do desconto: {formatar_moeda_brasileira(valor_desc)}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                            <div class="success-box">
                                <strong>✅ Resumo:</strong><br>
                                • Valor inicial: {formatar_moeda_brasileira(valor_inicial)}<br>
                                • Desconto: {formatar_porcentagem(perc)} ({formatar_moeda_brasileira(valor_desc)})<br>
                                • <strong>Valor final: {formatar_moeda_brasileira(valor_final)}</strong>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="result-box">
                                📈 <strong>Acréscimo de {formatar_porcentagem(perc)}</strong><br>
                                Valor do acréscimo: {formatar_moeda_brasileira(valor_desc)}
                            </div>
                        """, unsafe_allow_html=True)
        
        # Markup/Margem
        with subtab2:
            st.markdown("### 📈 Cálculo de Markup e Margem")
            
            col1, col2 = st.columns(2)
            
            with col1:
                custo_input = st.text_input(
                    "💰 Custo (R$):",
                    value="0,00",
                    help="Digite o custo usando vírgula para decimais",
                    key="markup_custo_br"
                )
                custo = converter_input_brasileiro(custo_input)
                st.caption(f"Custo convertido: {formatar_moeda_brasileira(custo)}")
                
            with col2:
                margem_input = st.text_input(
                    "📊 Margem desejada (%):",
                    value="0,00",
                    help="Digite a margem usando vírgula para decimais (ex: 25,50)",
                    key="markup_margem_br"
                )
                margem = converter_input_brasileiro(margem_input)
                st.caption(f"Margem convertida: {formatar_porcentagem(margem)}")
            
            if st.button("📈 Calcular Preço de Venda", type="primary"):
                preco_venda, lucro, erro = calcular_markup(custo, margem)
                
                if erro:
                    st.error(erro)
                else:
                    st.markdown(f"""
                        <div class="result-box">
                            💰 <strong>Preço de Venda: {formatar_moeda_brasileira(preco_venda)}</strong><br>
                            Lucro: {formatar_moeda_brasileira(lucro)}
                        </div>
                    """, unsafe_allow_html=True)
        
        # Desconto Direto
        with subtab3:
            st.markdown("### 💸 Aplicar Desconto")
            
            col1, col2 = st.columns(2)
            
            with col1:
                valor_original_input = st.text_input(
                    "💵 Valor Original (R$):",
                    value="0,00",
                    help="Digite o valor usando vírgula para decimais",
                    key="desc_direto_valor_br"
                )
                valor_original = converter_input_brasileiro(valor_original_input)
                st.caption(f"Valor convertido: {formatar_moeda_brasileira(valor_original)}")
                
            with col2:
                desc_percentual_input = st.text_input(
                    "📉 Desconto (%):",
                    value="0,00",
                    help="Digite a porcentagem usando vírgula para decimais",
                    key="desc_direto_perc_br"
                )
                desc_percentual = converter_input_brasileiro(desc_percentual_input)
                st.caption(f"Desconto convertido: {formatar_porcentagem(desc_percentual)}")
            
            if st.button("💸 Aplicar Desconto", type="primary"):
                desconto_valor = valor_original * (desc_percentual / 100)
                valor_com_desconto = valor_original - desconto_valor
                
                st.markdown(f"""
                    <div class="result-box">
                        🎯 <strong>Valor Final: {formatar_moeda_brasileira(valor_com_desconto)}</strong><br>
                        Desconto aplicado: {formatar_moeda_brasileira(desconto_valor)}
                    </div>
                """, unsafe_allow_html=True)
    
    # =============== ABA JUROS ===============
    with tab3:
        st.markdown("""
            <div class="calc-card">
                <h3>📈 Calculadora de Juros</h3>
                <p>Juros simples e compostos</p>
            </div>
        """, unsafe_allow_html=True)
        
        subtab1, subtab2, subtab3 = st.tabs(["📊 Juros Simples", "📈 Juros Compostos", "⚖️ Comparação"])
        
        # Juros Simples
        with subtab1:
            st.markdown("### 📊 Juros Simples")
            st.markdown("""
                <div class="formula-box">
                    <strong>Fórmula:</strong> J = C × i × t<br>
                    <strong>Montante:</strong> M = C + J<br>
                    <em>Onde: C=Capital, i=Taxa, t=Tempo, J=Juros, M=Montante</em>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                capital_s = st.number_input("💰 Capital (R$):", value=0.0, key="juros_s_capital", format="%.2f")
            with col2:
                taxa_s = st.number_input("📊 Taxa (% ao período):", value=0.0, key="juros_s_taxa", format="%.2f")
            with col3:
                tempo_s = st.number_input("⏱️ Tempo (períodos):", value=0.0, key="juros_s_tempo", format="%.2f")
            
            if st.button("📊 Calcular Juros Simples", type="primary"):
                resultado, erro = calcular_juros_simples(capital_s, taxa_s, tempo_s)
                
                if erro:
                    st.error(erro)
                else:
                    st.markdown(f"""
                        <div class="result-box">
                            💰 <strong>Montante: {formatar_moeda_brasileira(resultado['montante'])}</strong><br>
                            Juros: {formatar_moeda_brasileira(resultado['juros'])}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Detalhamento
                    st.markdown(f"""
                        <div class="success-box">
                            <strong>📋 Detalhamento:</strong><br>
                            • Capital inicial: {formatar_moeda_brasileira(resultado['capital'])}<br>
                            • Taxa: {formatar_porcentagem(resultado['taxa'])} ao período<br>
                            • Tempo: {formatar_numero_brasileiro(resultado['tempo'])} períodos<br>
                            • Juros acumulados: {formatar_moeda_brasileira(resultado['juros'])}<br>
                            • <strong>Montante final: {formatar_moeda_brasileira(resultado['montante'])}</strong>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Juros Compostos
        with subtab2:
            st.markdown("### 📈 Juros Compostos")
            st.markdown("""
                <div class="formula-box">
                    <strong>Fórmula:</strong> M = C × (1 + i)^t<br>
                    <strong>Juros:</strong> J = M - C<br>
                    <em>Onde: C=Capital, i=Taxa, t=Tempo, J=Juros, M=Montante</em>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                capital_c = st.number_input("💰 Capital (R$):", value=0.0, key="juros_c_capital", format="%.2f")
            with col2:
                taxa_c = st.number_input("📊 Taxa (% ao período):", value=0.0, key="juros_c_taxa", format="%.2f")
            with col3:
                tempo_c = st.number_input("⏱️ Tempo (períodos):", value=0.0, key="juros_c_tempo", format="%.2f")
            
            if st.button("📈 Calcular Juros Compostos", type="primary"):
                resultado, erro = calcular_juros_compostos(capital_c, taxa_c, tempo_c)
                
                if erro:
                    st.error(erro)
                else:
                    st.markdown(f"""
                        <div class="result-box">
                            💰 <strong>Montante: {formatar_moeda_brasileira(resultado['montante'])}</strong><br>
                            Juros: {formatar_moeda_brasileira(resultado['juros'])}
                        </div>
                    """, unsafe_allow_html=True)
        
        # Comparação
        with subtab3:
            st.markdown("### ⚖️ Comparação: Simples vs Compostos")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                capital_comp = st.number_input("💰 Capital (R$):", value=1000.0, key="comp_capital", format="%.2f")
            with col2:
                taxa_comp = st.number_input("📊 Taxa (% ao período):", value=10.0, key="comp_taxa", format="%.2f")
            with col3:
                tempo_comp = st.number_input("⏱️ Tempo (períodos):", value=12.0, key="comp_tempo", format="%.2f")
            
            if st.button("⚖️ Comparar", type="primary"):
                simples, _ = calcular_juros_simples(capital_comp, taxa_comp, tempo_comp)
                compostos, _ = calcular_juros_compostos(capital_comp, taxa_comp, tempo_comp)
                
                if simples and compostos:
                    diferenca = compostos['montante'] - simples['montante']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                            <div class="info-box">
                                <h4>📊 Juros Simples</h4>
                                • Montante: {formatar_moeda_brasileira(simples['montante'])}<br>
                                • Juros: {formatar_moeda_brasileira(simples['juros'])}
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="success-box">
                                <h4>📈 Juros Compostos</h4>
                                • Montante: {formatar_moeda_brasileira(compostos['montante'])}<br>
                                • Juros: {formatar_moeda_brasileira(compostos['juros'])}
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class="result-box">
                            💎 <strong>Diferença: {formatar_moeda_brasileira(diferenca)}</strong><br>
                            Os juros compostos rendem {formatar_moeda_brasileira(diferenca)} a mais!
                        </div>
                    """, unsafe_allow_html=True)
    
    # =============== ABA PORCENTAGEM ===============
    with tab4:
        st.markdown("""
            <div class="calc-card">
                <h3>📊 Calculadora de Porcentagem</h3>
                <p>Cálculos percentuais diversos</p>
            </div>
        """, unsafe_allow_html=True)
        
        subtab1, subtab2, subtab3 = st.tabs(["🔢 X% de Y", "📈 Variação %", "🎯 Encontrar %"])
        
        # X% de Y
        with subtab1:
            st.markdown("### 🔢 Calcular X% de um valor")
            
            col1, col2 = st.columns(2)
            
            with col1:
                valor_perc_input = st.text_input(
                    "💰 Valor (R$):",
                    value="0,00",
                    help="Digite o valor usando vírgula para decimais",
                    key="perc_valor_br"
                )
                valor_perc = converter_input_brasileiro(valor_perc_input)
                st.caption(f"Valor convertido: {formatar_moeda_brasileira(valor_perc)}")
                
            with col2:
                percentual_input = st.text_input(
                    "📊 Porcentagem (%):",
                    value="0,00",
                    help="Digite a porcentagem usando vírgula para decimais",
                    key="perc_percent_br"
                )
                percentual = converter_input_brasileiro(percentual_input)
                st.caption(f"Porcentagem convertida: {formatar_porcentagem(percentual)}")
            
            if st.button("🔢 Calcular", type="primary"):
                resultado, erro = calcular_porcentagem(valor_perc, percentual)
                
                if erro:
                    st.error(erro)
                else:
                    st.markdown(f"""
                        <div class="result-box">
                            🎯 <strong>{formatar_porcentagem(percentual)} de {formatar_moeda_brasileira(valor_perc)} = {formatar_moeda_brasileira(resultado)}</strong>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Variação Percentual
        with subtab2:
            st.markdown("### 📈 Calcular Variação Percentual")
            
            col1, col2 = st.columns(2)
            
            with col1:
                valor_inicial_var_input = st.text_input(
                    "📊 Valor Inicial:",
                    value="0,00",
                    help="Digite o valor inicial usando vírgula para decimais",
                    key="var_inicial_br"
                )
                valor_inicial_var = converter_input_brasileiro(valor_inicial_var_input)
                st.caption(f"Valor convertido: {formatar_numero_brasileiro(valor_inicial_var)}")
                
            with col2:
                valor_final_var_input = st.text_input(
                    "🎯 Valor Final:",
                    value="0,00",
                    help="Digite o valor final usando vírgula para decimais",
                    key="var_final_br"
                )
                valor_final_var = converter_input_brasileiro(valor_final_var_input)
                st.caption(f"Valor convertido: {formatar_numero_brasileiro(valor_final_var)}")
            
            if st.button("📈 Calcular Variação", type="primary"):
                variacao, erro = calcular_variacao_percentual(valor_inicial_var, valor_final_var)
                
                if erro:
                    st.error(erro)
                else:
                    tipo_var = "aumento" if variacao > 0 else "diminuição" if variacao < 0 else "sem alteração"
                    cor = "success-box" if variacao > 0 else "warning-box" if variacao < 0 else "info-box"
                    
                    st.markdown(f"""
                        <div class="{cor}">
                            📈 <strong>Variação: {formatar_porcentagem(abs(variacao))}</strong><br>
                            Tipo: {tipo_var.upper()}
                        </div>
                    """, unsafe_allow_html=True)
    
    # =============== ABA CONVERSÕES ===============
    with tab5:
        st.markdown("""
            <div class="calc-card">
                <h3>🌡️ Conversões</h3>
                <p>Converta unidades de medida</p>
            </div>
        """, unsafe_allow_html=True)
        
        subtab1, subtab2, subtab3 = st.tabs(["🌡️ Temperatura", "📏 Comprimento", "⚖️ Peso"])
        
        # Temperatura
        with subtab1:
            st.markdown("### 🌡️ Conversão de Temperatura")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                temp_valor = st.number_input("🌡️ Valor:", value=0.0, key="temp_valor", format="%.2f")
            with col2:
                temp_de = st.selectbox("De:", ["Celsius", "Fahrenheit", "Kelvin"], key="temp_de")
            with col3:
                temp_para = st.selectbox("Para:", ["Celsius", "Fahrenheit", "Kelvin"], key="temp_para")
            
            if st.button("🌡️ Converter", type="primary"):
                resultado, erro = converter_temperatura(temp_valor, temp_de, temp_para)
                
                if erro:
                    st.error(erro)
                else:
                    st.markdown(f"""
                        <div class="result-box">
                            🌡️ <strong>{formatar_numero_brasileiro(temp_valor)}° {temp_de} = {formatar_numero_brasileiro(resultado)}° {temp_para}</strong>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Comprimento
        with subtab2:
            st.markdown("### 📏 Conversão de Comprimento")
            
            conversoes_comprimento = {
                "Metros": 1,
                "Centímetros": 100,
                "Milímetros": 1000,
                "Quilômetros": 0.001,
                "Polegadas": 39.3701,
                "Pés": 3.28084
            }
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                comp_valor = st.number_input("📏 Valor:", value=0.0, key="comp_valor", format="%.2f")
            with col2:
                comp_de = st.selectbox("De:", list(conversoes_comprimento.keys()), key="comp_de")
            with col3:
                comp_para = st.selectbox("Para:", list(conversoes_comprimento.keys()), key="comp_para")
            
            if st.button("📏 Converter", type="primary"):
                # Converter para metros primeiro
                metros = comp_valor / conversoes_comprimento[comp_de]
                # Converter de metros para unidade desejada
                resultado = metros * conversoes_comprimento[comp_para]
                
                st.markdown(f"""
                    <div class="result-box">
                        📏 <strong>{formatar_numero_brasileiro(comp_valor)} {comp_de} = {formatar_numero_brasileiro(resultado)} {comp_para}</strong>
                    </div>
                """, unsafe_allow_html=True)
        
        # Peso
        with subtab3:
            st.markdown("### ⚖️ Conversão de Peso")
            
            conversoes_peso = {
                "Quilogramas": 1,
                "Gramas": 1000,
                "Toneladas": 0.001,
                "Libras": 2.20462,
                "Onças": 35.274
            }
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                peso_valor = st.number_input("⚖️ Valor:", value=0.0, key="peso_valor", format="%.2f")
            with col2:
                peso_de = st.selectbox("De:", list(conversoes_peso.keys()), key="peso_de")
            with col3:
                peso_para = st.selectbox("Para:", list(conversoes_peso.keys()), key="peso_para")
            
            if st.button("⚖️ Converter", type="primary"):
                # Converter para kg primeiro
                kg = peso_valor / conversoes_peso[peso_de]
                # Converter de kg para unidade desejada
                resultado = kg * conversoes_peso[peso_para]
                
                st.markdown(f"""
                    <div class="result-box">
                        ⚖️ <strong>{formatar_numero_brasileiro(peso_valor)} {peso_de} = {formatar_numero_brasileiro(resultado)} {peso_para}</strong>
                    </div>
                """, unsafe_allow_html=True)
    
    # =============== ABA CALCULADORA BÁSICA ===============
    with tab6:
        st.markdown("""
            <div class="calc-card">
                <h3>🔢 Calculadora Básica</h3>
                <p>Operações matemáticas básicas</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Inicializar estado da calculadora
        if 'calc_display' not in st.session_state:
            st.session_state.calc_display = "0"
        if 'calc_memory' not in st.session_state:
            st.session_state.calc_memory = 0
        if 'calc_operator' not in st.session_state:
            st.session_state.calc_operator = None
        
        # Display com formatação brasileira
        display_formatado = st.session_state.calc_display.replace(".", ",")
        st.markdown(f"""
            <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; text-align: right; font-size: 2em; font-family: monospace; margin-bottom: 20px;">
                {display_formatado}
            </div>
        """, unsafe_allow_html=True)
        
        # Funções da calculadora
        def calc_append_number(num):
            if st.session_state.calc_display == "0":
                st.session_state.calc_display = str(num)
            else:
                st.session_state.calc_display += str(num)
        
        def calc_clear():
            st.session_state.calc_display = "0"
            st.session_state.calc_memory = 0
            st.session_state.calc_operator = None
        
        def calc_operation(op):
            try:
                current = float(st.session_state.calc_display.replace(",", "."))
                if st.session_state.calc_operator and st.session_state.calc_memory != 0:
                    # Executar operação anterior
                    if st.session_state.calc_operator == "+":
                        result = st.session_state.calc_memory + current
                    elif st.session_state.calc_operator == "-":
                        result = st.session_state.calc_memory - current
                    elif st.session_state.calc_operator == "*":
                        result = st.session_state.calc_memory * current
                    elif st.session_state.calc_operator == "/":
                        result = st.session_state.calc_memory / current if current != 0 else 0
                    
                    st.session_state.calc_display = str(result).replace(".", ",")
                    st.session_state.calc_memory = result
                else:
                    st.session_state.calc_memory = current
                
                st.session_state.calc_operator = op
                st.session_state.calc_display = "0"
            except:
                st.session_state.calc_display = "Erro"
        
        # Botões da calculadora
        col1, col2, col3, col4 = st.columns(4)
        
        # Linha 1
        with col1:
            if st.button("C", key="calc_clear", use_container_width=True):
                calc_clear()
        with col2:
            if st.button("±", key="calc_sign", use_container_width=True):
                try:
                    current = float(st.session_state.calc_display.replace(",", "."))
                    st.session_state.calc_display = str(-current).replace(".", ",")
                except:
                    pass
        with col3:
            if st.button("%", key="calc_percent", use_container_width=True):
                try:
                    current = float(st.session_state.calc_display.replace(",", "."))
                    st.session_state.calc_display = str(current / 100).replace(".", ",")
                except:
                    pass
        with col4:
            if st.button("÷", key="calc_div", use_container_width=True):
                calc_operation("/")
        
        # Linha 2
        with col1:
            if st.button("7", key="calc_7", use_container_width=True):
                calc_append_number(7)
        with col2:
            if st.button("8", key="calc_8", use_container_width=True):
                calc_append_number(8)
        with col3:
            if st.button("9", key="calc_9", use_container_width=True):
                calc_append_number(9)
        with col4:
            if st.button("×", key="calc_mult", use_container_width=True):
                calc_operation("*")
        
        # Linha 3
        with col1:
            if st.button("4", key="calc_4", use_container_width=True):
                calc_append_number(4)
        with col2:
            if st.button("5", key="calc_5", use_container_width=True):
                calc_append_number(5)
        with col3:
            if st.button("6", key="calc_6", use_container_width=True):
                calc_append_number(6)
        with col4:
            if st.button("−", key="calc_sub", use_container_width=True):
                calc_operation("-")
        
        # Linha 4
        with col1:
            if st.button("1", key="calc_1", use_container_width=True):
                calc_append_number(1)
        with col2:
            if st.button("2", key="calc_2", use_container_width=True):
                calc_append_number(2)
        with col3:
            if st.button("3", key="calc_3", use_container_width=True):
                calc_append_number(3)
        with col4:
            if st.button("+", key="calc_add", use_container_width=True):
                calc_operation("+")
        
        # Linha 5
        col1_wide, col2_single, col3_single = st.columns([2, 1, 1])
        with col1_wide:
            if st.button("0", key="calc_0", use_container_width=True):
                calc_append_number(0)
        with col2_single:
            if st.button(",", key="calc_dot", use_container_width=True):
                if "," not in st.session_state.calc_display:
                    st.session_state.calc_display += ","
        with col3_single:
            if st.button("=", key="calc_equals", use_container_width=True):
                calc_operation("=")
    
    # =============== ABA HISTÓRICO ===============
    with tab7:
        st.markdown("""
            <div class="calc-card">
                <h3>📋 Histórico de Cálculos</h3>
                <p>Todos os seus cálculos salvos</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Inicializar histórico se não existir
        if 'historico_geral' not in st.session_state:
            st.session_state.historico_geral = []
        
        if st.session_state.historico_geral:
            # Mostrar histórico
            df_historico = pd.DataFrame(st.session_state.historico_geral)
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                tipos_filtro = st.multiselect(
                    "🔍 Filtrar por tipo:",
                    options=df_historico['tipo'].unique(),
                    default=df_historico['tipo'].unique()
                )
            
            with col2:
                if st.button("🗑️ Limpar Histórico"):
                    st.session_state.historico_geral = []
                    st.rerun()
            
            # Aplicar filtros
            df_filtrado = df_historico[df_historico['tipo'].isin(tipos_filtro)]
            
            # Mostrar tabela
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                hide_index=True
            )
            
            # Estatísticas
            st.markdown("### 📊 Estatísticas:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Cálculos", len(df_historico))
            
            with col2:
                tipo_mais_usado = df_historico['tipo'].mode().iloc[0] if not df_historico.empty else "N/A"
                st.metric("Tipo Mais Usado", tipo_mais_usado)
            
            with col3:
                st.metric("Tipos Diferentes", df_historico['tipo'].nunique())
        
        else:
            st.info("📝 Nenhum cálculo realizado ainda. Use as calculadoras para ver o histórico aqui!")
    
    # =============== ABA AJUDA ===============
    with tab8:
        st.markdown("""
            <div class="calc-card">
                <h3>📚 Central de Ajuda</h3>
                <p>Guias e tutoriais de uso</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Guias rápidos
        with st.expander("🧮 Como usar a Regra de Três", expanded=True):
            st.markdown("""
            **1. Escolha o tipo:**
            - **Direta:** Quando uma grandeza aumenta, a outra também aumenta
            - **Inversa:** Quando uma aumenta, a outra diminui
            
            **2. Insira os valores:**
            - A, B, C são os valores conhecidos
            - X é o valor que queremos encontrar
            
            **3. Exemplo prático:**
            - Se 5 produtos custam R$ 100, quanto custam 8 produtos?
            - 5 → 100 | 8 → X
            - X = (100 × 8) ÷ 5 = R$ 160
            """)
        
        with st.expander("💰 Como calcular Desconto Reverso"):
            st.markdown("""
            **Cenário:** Você tem um preço inicial e quer chegar a um preço final específico.
            
            **Exemplo:**
            - Produto custa R$ 200,00
            - Você quer vender por R$ 150,00
            - Qual desconto aplicar?
            
            **Resposta:** 25% de desconto
            - Cálculo: ((200 - 150) ÷ 200) × 100 = 25%
            
            **💡 Dica de formatação:**
            - Use vírgula para decimais: 1.500,90
            - Não use pontos nos milhares nos campos de texto
            - Exemplo correto: 32746,90 (não 32.746,90)
            """)
        
        with st.expander("📈 Diferença entre Juros Simples e Compostos"):
            st.markdown("""
            **Juros Simples:**
            - Incidem sempre sobre o capital inicial
            - Fórmula: J = C × i × t
            - Crescimento linear
            
            **Juros Compostos:**
            - Incidem sobre o montante acumulado
            - Fórmula: M = C × (1 + i)^t
            - Crescimento exponencial
            
            **Dica:** Juros compostos sempre rendem mais a longo prazo!
            """)
        
        with st.expander("🔢 Atalhos da Calculadora"):
            st.markdown("""
            **Botões especiais:**
            - **C:** Limpa tudo
            - **±:** Inverte o sinal (positivo/negativo)
            - **%:** Converte para porcentagem (divide por 100)
            
            **Dica:** Use a vírgula (,) para números decimais
            """)
        
        with st.expander("💡 Formatação de Números Brasileira"):
            st.markdown("""
            **Como digitar valores:**
            - ✅ **Correto:** 1500,90 (vírgula para decimais)
            - ✅ **Correto:** 32746,90
            - ❌ **Incorreto:** 1.500,90 (não use pontos nos campos de texto)
            - ❌ **Incorreto:** 1500.90 (ponto para decimais é padrão americano)
            
            **Exemplos práticos:**
            - Mil e quinhentos reais e noventa centavos: **1500,90**
            - Trinta e dois mil reais: **32000,00** ou **32000**
            - Vinte e cinco por cento: **25,00** ou **25**
            
            **⚠️ Importante:**
            - Os campos de texto aceitam vírgula como separador decimal
            - A conversão é feita automaticamente pelo sistema
            - Os resultados são sempre mostrados no padrão brasileiro
            """)
        
        # Contato do desenvolvedor
        st.markdown("""
        ---
        ### 👨‍💻 Desenvolvedor
        
        **Vinicius Dev**
        - 📧 Entre em contato para sugestões ou melhorias
        - 🐛 Reporte bugs ou problemas
        - 💡 Sugira novas funcionalidades
        
        ---
        **Versão:** 2.1 | **Data:** 2025 | **Formatação:** Padrão Brasileiro
        """)

# Função para salvar no histórico
def salvar_historico(tipo, operacao, resultado):
    """Salva cálculo no histórico geral"""
    if 'historico_geral' not in st.session_state:
        st.session_state.historico_geral = []
    
    st.session_state.historico_geral.append({
        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'tipo': tipo,
        'operacao': operacao,
        'resultado': resultado
    })

if __name__ == "__main__":
    main()