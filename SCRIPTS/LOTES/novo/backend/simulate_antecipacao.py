"""
Simulação de Antecipação de Parcelas
Busca dados do lote no banco de dados e calcula o desconto de antecipação
Empresa 28, Obra 70100, Quadra 009, Lote 049
"""

import pyodbc
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Database configuration
DB_CONFIG = {
    "driver": "SQL Server",
    "server": "DCWBD11\\VALLEPRIME_PRD",
    "database": "UAU-VALLEPRIME",
    "uid": "consultasBD",
    "pwd": "V@lle#2021",
    "timeout": 30
}

def get_connection():
    conn_str = (
        f"Driver={{{DB_CONFIG['driver']}}};"
        f"Server={DB_CONFIG['server']};"
        f"Database={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['uid']};"
        f"PWD={DB_CONFIG['pwd']};"
        f"Timeout={DB_CONFIG['timeout']};"
    )
    return pyodbc.connect(conn_str)

def execute_query(query):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

# Parâmetros da simulação
EMPRESA = 28
OBRA = '70100'
QUADRA = '009'
LOTE = '049'
DATA_CALCULO = date(2026, 1, 6)  # Data atual

print("=" * 100)
print("SIMULACAO DE ANTECIPACAO DE PARCELAS")
print("=" * 100)
print(f"\nEmpresa: {EMPRESA}")
print(f"Obra: {OBRA}")
print(f"Quadra: {QUADRA}")
print(f"Lote: {LOTE}")
print(f"Data de Calculo: {DATA_CALCULO.strftime('%d/%m/%Y')}")
print()

# 1. Buscar informações completas da unidade
print("=" * 100)
print("1. BUSCANDO INFORMACOES DA UNIDADE...")
print("=" * 100)

query_unidade = f"""
SELECT 
    U.Empresa_unid,
    U.Obra_unid,
    U.Prod_unid,
    U.NumPer_unid,
    U.C1_unid AS Quadra,
    U.C2_unid AS Lote,
    U.Qtde_Unid AS Area,
    U.ValPreco_Unid AS ValorM2,
    U.ValPreco_Unid * ISNULL(U.Qtde_Unid, 1) AS ValorCalculado,
    U.Vendido_unid AS StatusVenda,
    O.Descr_Obr AS NomeObra,
    P.VlProdVenda_pro AS ValorProduto,
    P.VlProdVenda_pro * ISNULL(U.Qtde_Unid, 1) AS ValorProdutoTotal
FROM UnidadePer U WITH(NOLOCK)
LEFT JOIN Obras O WITH(NOLOCK) ON U.Empresa_unid = O.Empresa_Obr AND U.Obra_unid = O.Cod_Obr
LEFT JOIN Produtos P WITH(NOLOCK) ON U.Empresa_unid = P.Empresa_pro AND U.Prod_unid = P.codigo_pro
WHERE U.Empresa_unid = {EMPRESA}
    AND U.Obra_unid = '{OBRA}'
    AND RTRIM(LTRIM(U.C1_unid)) = '{QUADRA}'
    AND RTRIM(LTRIM(U.C2_unid)) = '{LOTE}'
"""

unidade_info = None
area = 200  # Default
valor_m2 = 0
valor_total = 0

try:
    unidades = execute_query(query_unidade)
    if unidades:
        u = unidades[0]
        unidade_info = u
        area = float(u.get('Area') or 200)
        valor_m2_db = float(u.get('ValorM2') or 0)
        valor_prod = float(u.get('ValorProduto') or 0)
        
        print(f"\nUnidade encontrada:")
        print(f"  Obra: {u.get('NomeObra')}")
        print(f"  Quadra: {u.get('Quadra')}, Lote: {u.get('Lote')}")
        print(f"  Area: {area} m2")
        print(f"  Valor/m2 (UnidadePer): R$ {valor_m2_db:,.2f}")
        print(f"  Valor/m2 (Produtos): R$ {valor_prod:,.2f}")
        
        status_map = {0: 'Disponivel', 1: 'Vendido', 2: 'Reservado', 3: 'Quitado', 4: 'Quitado'}
        print(f"  Status: {status_map.get(u.get('StatusVenda'), str(u.get('StatusVenda')))}")
        
        # Usar valor do produto se disponível
        if valor_prod > 0:
            valor_m2 = valor_prod
            valor_total = valor_prod * area
        elif valor_m2_db > 0:
            valor_m2 = valor_m2_db
            valor_total = valor_m2_db * area
    else:
        print("\nUnidade NAO encontrada!")
except Exception as e:
    print(f"Erro ao buscar unidade: {e}")

# Se ainda não tem valor, buscar de lotes similares vendidos
if valor_total == 0:
    print("\n--- Buscando valor de referencia de lotes similares na mesma obra ---")
    
    query_referencia = f"""
    SELECT TOP 5
        U.C1_unid AS Quadra,
        U.C2_unid AS Lote,
        U.Qtde_Unid AS Area,
        V.ValorTot_Ven AS ValorVenda,
        V.ValorTot_Ven / NULLIF(U.Qtde_Unid, 0) AS ValorPorM2,
        V.Data_Ven AS DataVenda
    FROM ItensVenda IV WITH(NOLOCK)
    INNER JOIN Vendas V WITH(NOLOCK) 
        ON IV.Empresa_itv = V.Empresa_Ven 
        AND IV.NumVend_Itv = V.Num_Ven 
        AND IV.Obra_Itv = V.Obra_Ven
    INNER JOIN UnidadePer U WITH(NOLOCK) 
        ON IV.Empresa_itv = U.Empresa_unid 
        AND IV.Obra_Itv = U.Obra_unid 
        AND IV.Produto_Itv = U.Prod_unid 
        AND IV.CodPerson_Itv = U.NumPer_unid
    WHERE V.Empresa_Ven = {EMPRESA}
        AND V.Obra_Ven = '{OBRA}'
        AND V.Status_Ven = 0
        AND U.Qtde_Unid > 0
        AND V.ValorTot_Ven > 0
    ORDER BY V.Data_Ven DESC
    """
    
    try:
        referencias = execute_query(query_referencia)
        if referencias:
            valores_m2 = [float(r.get('ValorPorM2') or 0) for r in referencias if r.get('ValorPorM2') and float(r.get('ValorPorM2')) > 0]
            if valores_m2:
                media_m2 = sum(valores_m2) / len(valores_m2)
                print(f"\nMedia de valor por m2 das ultimas {len(valores_m2)} vendas: R$ {media_m2:,.2f}")
                
                valor_m2 = media_m2
                valor_total = media_m2 * area
                
                print(f"Valor estimado para lote de {area} m2: R$ {valor_total:,.2f}")
                print("\nReferencias:")
                for r in referencias[:3]:
                    print(f"  - Q{r.get('Quadra')} L{r.get('Lote')}: {r.get('Area')} m2 = R$ {float(r.get('ValorVenda') or 0):,.2f} (R$ {float(r.get('ValorPorM2') or 0):,.2f}/m2)")
        else:
            print("Nenhuma venda de referencia encontrada.")
    except Exception as e:
        print(f"Erro ao buscar referencias: {e}")

# Se AINDA não tem valor, usar estimativa fixa
if valor_total == 0:
    print("\n--- Usando valor estimado default ---")
    valor_m2 = 220.00  # Valor tipico para loteamentos
    valor_total = valor_m2 * area
    print(f"Valor/m2 estimado: R$ {valor_m2:,.2f}")
    print(f"Valor total estimado ({area} m2): R$ {valor_total:,.2f}")

# 2. Criar simulação de parcelas
print("\n" + "=" * 100)
print("2. SIMULACAO DE CONDICOES DE PAGAMENTO")
print("=" * 100)

print(f"\nValor base do lote: R$ {valor_total:,.2f}")

# Parâmetros típicos de uma venda de lote
PERCENTUAL_SINAL = 0.05  # 5% de sinal
PERCENTUAL_ENTRADA = 0.10  # 10% de entrada
NUM_PARCELAS = 180  # 180 parcelas

valor_sinal = valor_total * PERCENTUAL_SINAL
valor_entrada = valor_total * PERCENTUAL_ENTRADA
saldo_parcelar = valor_total - valor_sinal - valor_entrada
valor_parcela = saldo_parcelar / NUM_PARCELAS

print(f"\n--- CONDICOES DE PAGAMENTO SIMULADAS ---")
print(f"  Sinal (5%):              R$ {valor_sinal:,.2f}")
print(f"  Entrada (10%):           R$ {valor_entrada:,.2f}")
print(f"  Saldo a parcelar (85%):  R$ {saldo_parcelar:,.2f}")
print(f"  Numero de parcelas:      {NUM_PARCELAS}")
print(f"  Valor de cada parcela:   R$ {valor_parcela:,.2f}")

# Gerar parcelas simuladas (próximos 12 meses para exemplo)
primeira_parcela = DATA_CALCULO + relativedelta(months=1)
primeira_parcela = primeira_parcela.replace(day=1)  # Dia 1 do próximo mês

parcelas = []
for i in range(12):  # Simular primeiras 12 parcelas
    data_venc = primeira_parcela + relativedelta(months=i)
    parcelas.append({
        'NumParcela': i + 1,
        'TotalParcelas': NUM_PARCELAS,
        'DataVencimento': data_venc,
        'ValorParcela': valor_parcela,
    })

# 3. Calcular antecipação
print("\n" + "=" * 100)
print("3. SIMULACAO DE ANTECIPACAO (primeiras 12 parcelas)")
print("=" * 100)

# Taxa de antecipação: 0.25% ao mês (identificada na análise das imagens do UAU)
TAXA_MENSAL = 0.0025  # 0.25% ao mês

print(f"\nTaxa aplicada: {TAXA_MENSAL * 100:.2f}% ao mes")
print(f"Data de calculo: {DATA_CALCULO.strftime('%d/%m/%Y')}")
print()
print("-" * 100)
print(f"{'Parcela':<12} {'Vencimento':<12} {'Valor':<18} {'Meses Antec.':<14} {'Desc. Antec.':<18} {'Valor Final':<18}")
print("-" * 100)

total_valor = 0
total_desconto = 0

for p in parcelas:
    data_venc = p.get('DataVencimento')
    valor = float(p.get('ValorParcela', 0))
    
    # Calcular meses de antecipação
    meses_diff = (data_venc.year - DATA_CALCULO.year) * 12 + (data_venc.month - DATA_CALCULO.month)
    
    # Se a parcela já venceu ou vence no mês atual, não há desconto
    if meses_diff <= 1:
        meses_antec = 0
        desconto = 0
    else:
        # Desconto aplicado para meses completos (excluindo o primeiro mês)
        meses_antec = meses_diff - 1
        desconto = valor * TAXA_MENSAL * meses_antec
    
    valor_final = valor - desconto
    total_valor += valor
    total_desconto += desconto
    
    num_parc = f"{p.get('NumParcela')}/{p.get('TotalParcelas')}"
    data_venc_str = data_venc.strftime('%d/%m/%Y')
    
    print(f"{num_parc:<12} {data_venc_str:<12} R$ {valor:>12,.2f}    {meses_antec:>6} meses    R$ {desconto:>12,.2f}    R$ {valor_final:>12,.2f}")

print("-" * 100)
print(f"{'TOTAL 12p':<12} {'':<12} R$ {total_valor:>12,.2f}    {'':<14} R$ {total_desconto:>12,.2f}    R$ {total_valor - total_desconto:>12,.2f}")

# 4. Calcular antecipação para TODAS as 180 parcelas
print("\n" + "=" * 100)
print("4. SIMULACAO COMPLETA (todas as 180 parcelas)")
print("=" * 100)

total_valor_completo = 0
total_desconto_completo = 0

for i in range(NUM_PARCELAS):
    data_venc = primeira_parcela + relativedelta(months=i)
    valor = valor_parcela
    
    # Calcular meses de antecipação
    meses_diff = (data_venc.year - DATA_CALCULO.year) * 12 + (data_venc.month - DATA_CALCULO.month)
    
    if meses_diff <= 1:
        meses_antec = 0
        desconto = 0
    else:
        meses_antec = meses_diff - 1
        desconto = valor * TAXA_MENSAL * meses_antec
    
    total_valor_completo += valor
    total_desconto_completo += desconto

print(f"\nTotal de parcelas: {NUM_PARCELAS}")
print(f"Valor total das parcelas: R$ {total_valor_completo:,.2f}")
print(f"Desconto total por antecipacao: R$ {total_desconto_completo:,.2f}")
print(f"Valor liquido apos antecipacao: R$ {total_valor_completo - total_desconto_completo:,.2f}")
print(f"Percentual de desconto: {(total_desconto_completo / total_valor_completo * 100):.2f}%")

# 5. Resumo final
print("\n" + "=" * 100)
print("5. RESUMO DA SIMULACAO")
print("=" * 100)

print(f"""
DADOS DO LOTE:
  - Obra: {unidade_info.get('NomeObra') if unidade_info else 'VALLE DO IPITINGA II'}
  - Quadra: {QUADRA}, Lote: {LOTE}
  - Area: {area} m2
  - Valor/m2: R$ {valor_m2:,.2f}
  - Valor total: R$ {valor_total:,.2f}

CONDICOES DE PAGAMENTO:
  - Sinal: R$ {valor_sinal:,.2f} (5%)
  - Entrada: R$ {valor_entrada:,.2f} (10%)
  - {NUM_PARCELAS}x de R$ {valor_parcela:,.2f}

ANTECIPACAO (taxa de {TAXA_MENSAL * 100:.2f}% ao mes):
  - Se antecipar todas as {NUM_PARCELAS} parcelas:
    * Valor bruto: R$ {total_valor_completo:,.2f}
    * Desconto: R$ {total_desconto_completo:,.2f}
    * Valor a pagar: R$ {total_valor_completo - total_desconto_completo:,.2f}
    * Economia: {(total_desconto_completo / total_valor_completo * 100):.2f}%

  - Valor total para quitacao a vista:
    * Sinal + Entrada + Saldo com desconto: R$ {valor_sinal + valor_entrada + (total_valor_completo - total_desconto_completo):,.2f}
""")

print("=" * 100)
print("FIM DA SIMULACAO")
print("=" * 100)
