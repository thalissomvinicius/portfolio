# 📚 Documentação do Banco de Dados UAU-VALLEPRIME

> **Gerado em:** 22/12/2025  
> **Servidor:** DCWBD11\VALLEPRIME_PRD  
> **Database:** UAU-VALLEPRIME  
> **Total de Tabelas:** 2.587

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Tabelas Principais](#tabelas-principais)
3. [Módulos do Sistema](#módulos-do-sistema)
4. [Relacionamentos Chave](#relacionamentos-chave)
5. [Consultas Úteis](#consultas-úteis)

---

## Visão Geral

O sistema UAU é um ERP imobiliário completo que gerencia:
- **Vendas e Contratos** de lotes/unidades
- **Financeiro** (contas a receber, boletos, recebimentos)
- **Pessoas** (clientes, corretores, fornecedores)
- **Obras** (empreendimentos, unidades)
- **Contabilidade e Fiscal**

---

## Tabelas Principais

### 🏠 Vendas e Contratos

| Tabela | Descrição | Registros | Chaves Primárias |
|--------|-----------|-----------|------------------|
| **Vendas** | Registro de todas as vendas | 25.533 | Empresa_Ven, NumVend_Ven |
| **ItensVenda** | Itens de cada venda (unidades) | 25.533 | Empresa_itv, NumVend_Itv, Obra_Itv, Produto_Itv, CodPerson_Itv |
| **ContasReceber** | Parcelas a receber | 2.084.199 | Empresa_prc, NumVend_Prc, Obra_Prc, NumParc_Prc, ParcType_Prc, Tipo_Prc, NumParcGer_Prc |
| **ContratoVenda** | Detalhes do contrato | - | Empresa, NumVend, Obra |
| **Adquirentes** | Compradores da venda | - | Empresa, NumVend, Obra, CodPerson |

### 💰 Financeiro

| Tabela | Descrição | Registros | Chaves Primárias |
|--------|-----------|-----------|------------------|
| **Recebidas** | Parcelas recebidas/pagas | 2.082.109 | Empresa_Rec, NumVend_Rec, Obra_Rec, NumParc_Rec, ParcType_Rec, Tipo_Rec, NumParcGer_Rec |
| **RecebePgto** | Detalhes do pagamento | 2.473.882 | Empresa_rpg, NumReceb_Rpg, Tipo_Rpg, NumCont_Rpg |
| **RecebePgtoDiv** | Divisão do pagamento por parcela | 2.474.523 | Múltiplas chaves compostas |
| **Boleto** | Boletos emitidos | 1.912.200 | Empresa_Bol, Banco_Bol, Conta_Bol, Numero_Bol, Parcela_bol |
| **Depositos** | Depósitos bancários | 1.670.671 | Empresa_dep, Numero_Dep, Banco_Dep, Conta_Dep |
| **Extrato** | Extrato bancário (conciliação) | 1.857.718 | Empresa_doc, Banco_doc, Conta_doc, Numero_doc, Data_doc, Tipo_doc |

### 👥 Pessoas e Corretores

| Tabela | Descrição | Registros | Chaves Primárias |
|--------|-----------|-----------|------------------|
| **Pessoas** | Cadastro de pessoas (clientes, corretores, etc) | 145.689 | Empresa_pes, Codigo_pes |
| **PessoaEmp** | Vínculo pessoa-empresa | - | Empresa, CodPerson |
| **CategoriasDePessoa** | Tipos de pessoa (cliente, corretor, etc) | - | Codigo |
| **Comissao** | Configuração de comissões | - | Empresa, NumVend, Obra |

### 🏗️ Obras e Unidades

| Tabela | Descrição | Registros | Chaves Primárias |
|--------|-----------|-----------|------------------|
| **Obras** | Empreendimentos/Loteamentos | 469 | Empresa_obr, cod_obr |
| **UnidadePer** | Unidades (lotes/apartamentos) | - | Empresa_unid, Obra_unid, Produto_unid |
| **BlocoEmpreend** | Blocos/Quadras | - | Empresa, Obra, Bloco |
| **Produtos** | Tipos de produto | - | Empresa, Produto |

### 🏢 Empresas

| Tabela | Descrição | Registros | Chaves Primárias |
|--------|-----------|-----------|------------------|
| **Empresas** | Cadastro de empresas | - | Codigo |
| **EmpUsuario** | Usuários por empresa | - | Empresa, Usuario |
| **CCorrente** | Contas correntes | - | Empresa, Banco, Conta |

---

## Módulos do Sistema

### 📊 Módulo de Vendas
```
Vendas ─┬─→ ItensVenda (produtos vendidos)
        ├─→ Adquirentes (compradores)
        ├─→ ContasReceber (parcelas)
        ├─→ Comissao (comissões corretores)
        └─→ ContratoVenda (detalhes contrato)
```

### 💳 Módulo Financeiro
```
ContasReceber ─→ Boleto ─→ BoletoConfirmado
                    │
                    ↓
              Recebidas ─→ RecebePgto ─→ RecebePgtoDiv
                              │
                              ↓
                         Depositos ─→ Extrato (conciliação)
```

### 👤 Módulo de Pessoas
```
Pessoas ─┬─→ CategoriasDePessoa (cliente, corretor, etc)
         ├─→ PessoaEmp (empresas vinculadas)
         ├─→ Dependente
         └─→ Adquirentes (vinculos com vendas)
```

---

## Relacionamentos Chave

### Venda → Parcelas → Recebimento

```sql
-- De Venda para ContasReceber
SELECT * FROM Vendas V
INNER JOIN ContasReceber CR 
  ON V.Empresa_Ven = CR.Empresa_prc 
  AND V.NumVend_Ven = CR.NumVend_Prc 
  AND V.Obra_Ven = CR.Obra_Prc

-- De ContasReceber para Recebidas (parcela paga)
SELECT * FROM ContasReceber CR
INNER JOIN Recebidas R 
  ON CR.Empresa_prc = R.Empresa_Rec 
  AND CR.NumVend_Prc = R.NumVend_Rec 
  AND CR.Obra_Prc = R.Obra_Rec
  AND CR.NumParc_Prc = R.NumParc_Rec
  AND CR.ParcType_Prc = R.ParcType_Rec
  AND CR.Tipo_Prc = R.Tipo_Rec
  AND CR.NumParcGer_Prc = R.NumParcGer_Rec
```

### Recebimento → Conciliação Bancária

```sql
-- Cadeia completa de recebimento conciliado
SELECT * FROM Recebidas R
INNER JOIN RecebePgtoDiv RPD ON (joins complexos)
INNER JOIN RecebePgto RPG ON (joins)
INNER JOIN Depositos D ON (joins)
INNER JOIN Extrato E ON D.Numero_Dep = E.Numero_Doc
WHERE E.Tipo_Doc = 1  -- Depósito
```

---

## Campos Importantes

### Status de Unidade (UnidadePer.Vendido_unid)
| Valor | Significado |
|-------|-------------|
| 0 | Disponível |
| 1 | Vendido |
| 2 | Reservado |
| 4 | Quitado |
| 7 | Suspenso |
| 8 | Fora de Venda |

### Status de Parcela (ContasReceber.Status_Prc)
| Valor | Significado |
|-------|-------------|
| 0 | Em aberto |
| 1 | Paga |
| 2 | Cancelada |

### Tipo de Parcela (ContasReceber.Tipo_Prc)
| Valor | Significado |
|-------|-------------|
| S | Sinal |
| P | Parcela Normal |
| 1 | Outros |

---

## Consultas Úteis

### Vendas do Dia
```sql
SELECT V.*, P.Nome_pes AS Cliente
FROM Vendas V WITH(NOLOCK)
INNER JOIN Pessoas P ON V.Cliente_Ven = P.Codigo_pes AND V.Empresa_Ven = P.Empresa_pes
WHERE V.Empresa_Ven = @empresa 
  AND V.Obra_Ven = @obra
  AND CONVERT(date, V.Data_Ven) = CONVERT(date, GETDATE())
```

### Parcelas em Atraso
```sql
SELECT * FROM ContasReceber WITH(NOLOCK)
WHERE Empresa_prc = @empresa 
  AND Obra_Prc = @obra
  AND Status_Prc = 0  -- Em aberto
  AND Data_Prc < CAST(GETDATE() AS DATE)
  AND Tipo_Prc != '1'
```

### Estoque de Unidades
```sql
SELECT 
    SUM(CASE WHEN Vendido_unid = 0 THEN 1 ELSE 0 END) AS disponivel,
    SUM(CASE WHEN Vendido_unid = 1 THEN 1 ELSE 0 END) AS vendido,
    SUM(CASE WHEN Vendido_unid = 2 THEN 1 ELSE 0 END) AS reservado,
    SUM(CASE WHEN Vendido_unid = 4 THEN 1 ELSE 0 END) AS quitado
FROM UnidadePer WITH(NOLOCK)
WHERE Empresa_unid = @empresa AND Obra_unid = @obra
```

### Recebimentos do Dia (com Conciliação)
```sql
SELECT 
    SUM(RecebePgtoDiv.PercentValor_Rpd) AS valor_recebido
FROM Recebidas WITH(NOLOCK)
INNER JOIN RecebePgtoDiv WITH(NOLOCK) ON (joins...)
INNER JOIN RecebePgto WITH(NOLOCK) ON (joins...)
INNER JOIN Depositos WITH(NOLOCK) ON (joins...)
INNER JOIN Extrato WITH(NOLOCK) ON (joins... Tipo_Doc = 1)
WHERE Recebidas.Empresa_Rec = @empresa 
  AND Recebidas.Obra_Rec = @obra
  AND CONVERT(date, Extrato.Data_Doc) = GETDATE()
```

---

## Arquivos Gerados

- `database_schema.json` - Schema completo em JSON (347KB)
- Este documento - Documentação legível

---

> **Nota:** Este documento foi gerado automaticamente e pode precisar de atualizações conforme o sistema evolui.
