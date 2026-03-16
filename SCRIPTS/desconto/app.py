import streamlit as st

# Função para calcular o percentual de desconto
def calcular_desconto(valor_original, valor_desejado):
    if valor_original <= 0:
        raise ValueError("O valor original deve ser maior que zero.")
    if valor_desejado > valor_original:
        raise ValueError("O valor desejado deve ser menor ou igual ao valor original.")
    
    desconto = ((valor_original - valor_desejado) / valor_original) * 100
    return desconto

# Função principal
def main():
    st.title("Calculadora de Desconto para Quitação de Lote")

    # Entrada de dados
    st.header("Insira os Valores")
    valor_original = st.number_input("Valor original do lote (R$):", min_value=0.0, format="%.2f")
    valor_desejado = st.number_input("Valor desejado após desconto (R$):", min_value=0.0, format="%.2f")

    # Botão para calcular o desconto
    if st.button("Calcular Desconto"):
        try:
            # Calcular o desconto
            desconto = calcular_desconto(valor_original, valor_desejado)

            # Exibir o resultado
            st.success(f"**Percentual de Desconto Necessário:** {desconto:.2f}%")
        except ValueError as e:
            st.error(f"Erro: {e}")

# Executar o script
if __name__ == "__main__":
    main()