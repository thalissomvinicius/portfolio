# Documentação Técnica: Sistema de Geração de Propostas "Pixel-Perfect"

Este documento descreve o funcionamento interno do motor de geração de propostas em PDF, projetado para sobrepor dados dinâmicos a um template visual fixo (`PROPOSTA LIMPA.jpg`) com precisão milimétrica.

## 1. Arquitetura do Sistema

O sistema opera através da integração de três componentes fundamentais localizados no diretório raiz:

1.  **Motor de Renderização (`generate_proposal_reportlab.py`)**: Script Python que utiliza a biblioteca `ReportLab` para construir o PDF.
2.  **Mapa de Coordenadas (`posicoes_campos.json`)**: Dicionário que traduz nomes de campos para coordenadas `(x, y)` em milímetros.
3.  **Template Visual (`PROPOSTA LIMPA.jpg`)**: Imagem de fundo A4 que define o layout visual da proposta.

---

## 2. Fluxo de Execução

O coração da lógica reside na função `generate_pdf_reportlab` dentro de [generate_proposal_reportlab.py](file:///c:/Users/thalissom.cruz/Desktop/PROPOSTA/generate_proposal_reportlab.py).

### 2.1. Inicialização e Fundo
- **Local**: Linhas 13-17.
- O script cria um `canvas` ReportLab configurado para o tamanho `A4`.
- A imagem de fundo é desenhada preenchendo toda a página: `c.drawImage(background_image_path, 0, 0, width=width, height=height)`.

### 2.2. Sistema de Coordenadas e Conversão
- **Conceito**: O JSON usa origem no **Canto Superior Esquerdo** (comum em design). O ReportLab usa o **Canto Inferior Esquerdo** (padrão PDF).
- **Cálculo de Conversão** (Linhas 163-164):
  ```python
  x_pt = (x_mm + x_offset_correction) * mm
  y_pt = height - ((y_mm + y_offset_correction) * mm)
  ```
  *(Onde `mm` é o fator de conversão de milímetros para pontos do ReportLab).*

### 2.3. Agrupamento e Alinhamento de Colunas (Centelização)
Para tabelas de pagamento, os campos não usam o `x` exato do JSON, mas sim um `x` calculado para garantir alinhamento vertical perfeito.
- **Definição de Grupos**: Linhas 23-51. Campos são agrupados por tipo (`qtd`, `valor`, `dia`, etc).
- **Média de Alinhamento**: Linhas 54-66 calculam o `x` médio de cada grupo.
- **Offsets de Ajuste Fino**: Linhas 142-156 aplicam correções visuais específicas para cada tipo de dado para centralizar o texto no espaço da coluna.

---

## 3. Lógica Específica e Ajustes (Hardcoded)

Existem correções manuais no código para compensar variações do template ou da fonte:

- **Offsets Globais**: Linhas 99-100 (Ajustam a posição de todo o texto simultaneamente).
- **Checkboxes**: Linhas 105-108. Converte valores `True/False` em `"X"` e aplica um offset específico (`x: -1.5mm, y: 1.3mm`) para "mirar" no centro do quadrado da imagem.
- **Rodapé**: Linhas 111-114. Ajuste adicional para os campos de cidade e data final.
- **Linhas de Pagamento**: Linhas 118-130. Eleva os campos de parcelas em `-1.0mm` para alinhar com as linhas horizontais da tabela.
- **Cabeçalhos de Valor**: Linhas 133-135. Ajuste fino para os totais de seção.

---

## 4. Guia de Manutenção

### Alterar a Posição de um Campo
1. Localize a chave do campo em [posicoes_campos.json](file:///c:/Users/thalissom.cruz/Desktop/PROPOSTA/posicoes_campos.json).
2. Ajuste os valores de `x` e `y` (em milímetros).
3. Nota: Se o campo pertencer a uma coluna de pagamento (`tipo`, `qtd`, `valor`, etc), o `x` será sobrescrito pelo alinhamento de coluna.

### Alterar o Alinhamento de uma Coluna
1. No arquivo [generate_proposal_reportlab.py](file:///c:/Users/thalissom.cruz/Desktop/PROPOSTA/generate_proposal_reportlab.py), localize o dicionário `column_groups` (Linha 23).
2. Para ajustar a centralização visual, altere os valores dentro de `draw_text` nas condicionais `if centering_active:` (Linhas 143-156).

### Adicionar Novo Campo
1. Adicione a nova chave com coordenadas no JSON.
2. Passe o dado correspondente no dicionário `data` ao chamar a função.
3. Se for um campo booleano (checkbox), o código já tratará automaticamente como um "X".

---

## 5. Como Integrar

O sistema foi desenhado para ser chamado como um módulo:

```python
from generate_proposal_reportlab import generate_pdf_reportlab

# Os nomes das chaves devem ser IDÊNTICOS aos do posicoes_campos.json
meus_dados = {
    "nome_proponente": "NOME DO CLIENTE",
    "sexo_masc_proponente": True, # Marcará o checkbox
    "valor_sinal": "10.000,00",
    # ... outros campos
}

generate_pdf_reportlab(
    data=meus_dados,
    background_image_path="PROPOSTA LIMPA.jpg",
    positions_path="posicoes_campos.json",
    output_filename="saida.pdf"
)
```

---
> **Nota para IAs**: Ao realizar ajustes, priorize sempre a alteração no JSON primeiro. Use os offsets no Python apenas se a correção for sistemática (ex: para toda uma categoria de campos) ou se o JSON não for suficiente para atingir o "Pixel-Perfect".

