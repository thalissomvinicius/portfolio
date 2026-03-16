# 🚀 Guia Rápido de Uso

## ✅ Sistema Executando!

O sistema está rodando em: **http://localhost:8501**

## 📊 O que o sistema faz?

### 1️⃣ **Resumo Geral** (Tab Principal)
Mostra uma visão consolidada de todas as vendas com:
- ✅ Quais vendas TÊM boletos gerados
- ❌ Quais vendas NÃO TÊM boletos gerados
- 📊 Quantidade de sinais em aberto por venda
- 💰 Valor total de cada venda
- 👤 Cliente e Corretor
- 🏘️ Identificador (Quadra e Lote)

**Métricas exibidas:**
- Total de Vendas
- Vendas com Boleto
- Vendas sem Boleto
- Total de Sinais em Aberto

### 2️⃣ **Sinais de Corretagem**
Lista TODAS as parcelas de sinal de corretagem a receber:
- Corretor responsável
- Cliente
- Quadra e Lote
- Vencimento
- Valor da parcela
- Status (em aberto)

### 3️⃣ **Boletos Gerados**
Mostra TODOS os boletos que foram gerados no sistema:
- Número do boleto
- Cliente
- Data de emissão e vencimento
- Valor
- Status (Pendente, Registrado, Liquidado, Cancelado)
- Se foi enviado por email

**Filtro disponível:** Você pode filtrar por venda específica

### 4️⃣ **Detalhes por Venda**
Consulta DETALHADA de uma venda específica:
- Informações completas da venda
- Sinais que já foram PAGOS
- Boletos gerados para aquela venda

## ⚙️ Como usar os filtros?

Na **barra lateral esquerda** você encontra:

1. **Empresa**: Código da empresa (padrão: 28)
2. **Obra**: Código da obra (padrão: 70100)
3. **Data Vencimento**: Limite para buscar sinais de corretagem

**Depois de alterar os filtros, clique em "🔄 Atualizar Dados"**

## 📥 Exportar Dados

Cada tab tem um botão **"📥 Download CSV"** para exportar os dados em Excel/CSV

## 🎯 Principais Indicadores

### ✅ Venda com Boleto Gerado
Significa que a venda já tem pelo menos 1 boleto gerado no sistema

### ❌ Venda sem Boleto Gerado
Significa que a venda ainda NÃO tem nenhum boleto gerado - **ATENÇÃO NECESSÁRIA!**

### Sinais em Aberto
Quantidade de parcelas de sinal de corretagem que ainda não foram pagas

## 🔍 Exemplo de Uso

**Cenário:** Verificar quais vendas precisam gerar boletos

1. Vá na tab **"Resumo Geral"**
2. Procure por vendas com **"❌ Não"** na coluna "Boleto Gerado?"
3. Anote os números das vendas
4. Vá na tab **"Detalhes por Venda"**
5. Selecione cada venda para ver os detalhes

## 💡 Dicas

- Os dados são atualizados a cada 5 minutos automaticamente
- Use o botão "Atualizar Dados" para forçar atualização imediata
- Todas as datas estão no formato brasileiro (dd/MM/yyyy)
- Valores monetários estão formatados em Reais (R$)

## 🐛 Problemas?

### Não aparece nenhum dado
- Verifique se a **Empresa** e **Obra** estão corretas
- Confirme se existem vendas no banco de dados para esses filtros
- Clique em "Atualizar Dados"

### Erro de conexão
- Verifique se o servidor SQL está acessível
- Confirme as credenciais no código

---

**Desenvolvido para VallePrime** 🏘️
**Foco: Controle de Vendas e Boletos**
