"""
Solução final: Buscar dados de cliente via ContasReceber
"""

from database import execute_query

print("=" * 70)
print("SOLUÇÃO: BUSCAR CLIENTE VIA CONTASRECEBER")
print("=" * 70)

# O Cliente_Prc é o código do cliente na Pessoas
# O NumVend_prc é o número da venda

query = """
SELECT 
    U.C1_unid as quadra,
    U.C2_unid as lote,
    U.Identificador_Unid,
    CR.NumVend_prc as numVenda,
    CR.Cliente_Prc as codCliente,
    P.Nome_Pes as cliente
FROM UnidadePer U WITH(NOLOCK)
CROSS APPLY (
    SELECT TOP 1 NumVend_prc, Cliente_Prc
    FROM ContasReceber WITH(NOLOCK)
    WHERE Empresa_prc = U.Empresa_unid
      AND Obra_Prc = U.Obra_unid
      AND NumVend_prc IN (
          SELECT NumVend_Itv FROM ItensVenda WITH(NOLOCK)
          WHERE Empresa_itv = U.Empresa_unid
            AND Obra_Itv = U.Obra_unid
            AND Produto_Itv = U.Prod_unid
      )
      AND Tipo_Prc = 'S'
    ORDER BY NumVend_prc DESC
) CR
LEFT JOIN Pessoas P WITH(NOLOCK) ON CR.Cliente_Prc = P.cod_pes
WHERE U.Empresa_unid = 29
  AND U.Obra_unid = '70100'
  AND U.Vendido_unid = 4
"""

try:
    result = execute_query(query)
    print(f"\nResultado: {len(result)} lotes quitados com cliente")
    for r in result:
        print(f"  Q:{r['quadra']} L:{r['lote']} | Venda: {r['numVenda']} | Cliente: {r['cliente']}")
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "-" * 70)
print("TENTATIVA 2: Usando match pelo Identificador")
print("-" * 70)

query2 = """
SELECT 
    U.C1_unid as quadra,
    U.C2_unid as lote,
    U.Identificador_Unid,
    I.NumVend_Itv as numVenda,
    V.Cliente_Ven as codCliente,
    P.Nome_Pes as cliente
FROM UnidadePer U WITH(NOLOCK)
INNER JOIN ItensVenda I WITH(NOLOCK)
    ON U.Empresa_unid = I.Empresa_itv
    AND U.Obra_unid = I.Obra_Itv
    AND U.Prod_unid = I.Produto_Itv
    AND I.Item_Itv = U.Identificador_Unid
INNER JOIN Vendas V WITH(NOLOCK)
    ON I.Empresa_itv = V.Empresa_Ven AND I.NumVend_Itv = V.Num_Ven
LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
WHERE U.Empresa_unid = 29
  AND U.Obra_unid = '70100'
  AND U.Vendido_unid = 4
"""

try:
    result2 = execute_query(query2)
    print(f"Resultado via Identificador: {len(result2)}")
    for r in result2:
        print(f"  Q:{r['quadra']} L:{r['lote']} | Venda: {r['numVenda']} | Cliente: {r['cliente']}")
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "-" * 70)
print("TENTATIVA 3: Encontrar os lotes quitados nos lotes vendidos via Identificador")
print("-" * 70)

# Primeiro pegar os identificadores dos lotes quitados
query3a = """
SELECT Identificador_Unid FROM UnidadePer WITH(NOLOCK)
WHERE Empresa_unid = 29 AND Obra_unid = '70100' AND Vendido_unid = 4
"""
quitados = execute_query(query3a)
print(f"Identificadores dos quitados: {[r['Identificador_Unid'] for r in quitados]}")

# Buscar no ItensVenda por Item_Itv
for q in quitados[:3]:
    ident = q['Identificador_Unid']
    query3b = f"""
    SELECT TOP 1 Item_Itv, NumVend_Itv
    FROM ItensVenda WITH(NOLOCK)
    WHERE Empresa_itv = 29 AND Obra_Itv = '70100'
      AND Item_Itv LIKE '%{ident}%'
    """
    try:
        r = execute_query(query3b)
        print(f"  {ident}: {r if r else 'NÃO ENCONTRADO'}")
    except Exception as e:
        print(f"  {ident}: Erro - {e}")

print("\n" + "=" * 70)
print("FIM")
print("=" * 70)
