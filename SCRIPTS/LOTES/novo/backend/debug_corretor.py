"""Debug para verificar cálculo de recebimento do corretor RAIMUNDO CESAR"""
from database import execute_query

empresa = 28
obra = '70100'
corretor_nome = 'RAIMUNDO CESAR ALVES DO AMARAL'

print("=" * 70)
print(f"DEBUG: Recebimentos do Corretor")
print(f"Empresa: {empresa}, Obra: {obra}")
print(f"Corretor: {corretor_nome}")
print("=" * 70)

# 1. Primeiro, buscar o código do vendedor
query_vendedor = f"""
SELECT cod_pes, nome_pes
FROM Pessoas WITH(NOLOCK)
WHERE nome_pes LIKE '%RAIMUNDO CESAR%'
"""
result_vendedor = execute_query(query_vendedor)
print("\n1. BUSCANDO VENDEDOR:")
vendedor_cod = None
for v in result_vendedor:
    print(f"  Cod: {v.get('cod_pes')}, Nome: {v.get('nome_pes')}")
    if 'AMARAL' in str(v.get('nome_pes', '')).upper():
        vendedor_cod = v.get('cod_pes')

if not vendedor_cod:
    print("Vendedor não encontrado!")
else:
    print(f"\n  VENDEDOR SELECIONADO: {vendedor_cod}")

# 2. Buscar vendas deste corretor
emp_obra_param = f"{empresa}|{obra}"
print(f"\n2. VENDAS DO CORRETOR (Status=0):")
query_vendas = f"""
SELECT V.Num_Ven, V.Status_Ven, V.ValorTot_Ven, P.Nome_pes as Cliente
FROM Vendas V WITH(NOLOCK)
LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON V.Empresa_Ven = Empresa AND V.Obra_Ven = Obra
WHERE V.Vendedor_Ven = {vendedor_cod}
AND V.Status_Ven = 0
UNION ALL
SELECT VR.Num_VRec, VR.Status_VRec, VR.ValorTot_VRec, P.Nome_pes
FROM VendasRecebidas VR WITH(NOLOCK)
LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON VR.Empresa_VRec = Empresa AND VR.Obra_VRec = Obra
WHERE VR.Vendedor_VRec = {vendedor_cod}
AND VR.Status_VRec = 0
"""
result_vendas = execute_query(query_vendas)
print(f"  Total de vendas ativas: {len(result_vendas)}")
for v in result_vendas[:5]:
    print(f"    Venda {v.get('Num_Ven')}: {v.get('Cliente')}, Valor: R$ {v.get('ValorTot_Ven'):,.2f}")
if len(result_vendas) > 5:
    print(f"    ... e mais {len(result_vendas) - 5} vendas")

# 3. Buscar sinais pagos usando a query EXATA do sistema
print(f"\n3. SINAIS PAGOS (Query do Sistema):")
sinais_pagos_query = f"""
SELECT 
    v.Vendedor_Ven,
    COUNT(*) AS sinaisPagos,
    ISNULL(SUM(rec.Valor_Rec + rec.ValorConf_Rec + rec.VlCorrecao_Rec + rec.VlCorrecaoConf_Rec + 
           rec.VlMulta_Rec + rec.VlMultaConf_Rec + rec.VlJuros_Rec + rec.VlJurosConf_Rec + 
           rec.VlJurosParcConf_Rec + rec.VlJurosParcConf_Rec), 0) AS valorSinaisPagos
FROM Recebidas rec WITH(NOLOCK)
INNER JOIN (
    SELECT Num_Ven, Vendedor_Ven, Data_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK)
    WHERE Status_Ven = 0
    UNION ALL
    SELECT Num_VRec, Vendedor_VRec, Data_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK)
    WHERE Status_VRec = 0
) v ON rec.NumVend_Rec = v.Num_Ven AND rec.Empresa_Rec = v.Empresa_Ven AND rec.Obra_Rec = v.Obra_Ven
INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
WHERE rec.Tipo_Rec = 'S'
AND v.Vendedor_Ven = {vendedor_cod}
GROUP BY v.Vendedor_Ven
"""
result_sinais = execute_query(sinais_pagos_query)
print(f"  Resultado da query do sistema:")
for s in result_sinais:
    print(f"    Sinais Pagos: {s.get('sinaisPagos')}")
    print(f"    Valor Total: R$ {float(s.get('valorSinaisPagos') or 0):,.2f}")

# 4. Buscar recebimentos detalhados para este vendedor
print(f"\n4. RECEBIMENTOS DETALHADOS (Recebidas + Tipo_Rec='S'):")
detalhe_query = f"""
SELECT 
    rec.NumVend_Rec as Venda,
    rec.Data_Rec as DataRecebimento,
    rec.Valor_Rec,
    rec.ValorConf_Rec,
    rec.VlCorrecao_Rec,
    rec.VlCorrecaoConf_Rec,
    rec.VlMulta_Rec,
    rec.VlMultaConf_Rec,
    rec.VlJuros_Rec,
    rec.VlJurosConf_Rec,
    rec.VlJurosParc_Rec,
    rec.VlJurosParcConf_Rec,
    (rec.Valor_Rec + rec.ValorConf_Rec + rec.VlCorrecao_Rec + rec.VlCorrecaoConf_Rec + 
     rec.VlMulta_Rec + rec.VlMultaConf_Rec + rec.VlJuros_Rec + rec.VlJurosConf_Rec + 
     rec.VlJurosParc_Rec + rec.VlJurosParcConf_Rec) as TotalRecebido,
    P.Nome_pes as Cliente
FROM Recebidas rec WITH(NOLOCK)
INNER JOIN (
    SELECT Num_Ven, Vendedor_Ven, Cliente_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK)
    WHERE Status_Ven = 0
    UNION ALL
    SELECT Num_VRec, Vendedor_VRec, Cliente_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK)
    WHERE Status_VRec = 0
) v ON rec.NumVend_Rec = v.Num_Ven AND rec.Empresa_Rec = v.Empresa_Ven AND rec.Obra_Rec = v.Obra_Ven
LEFT JOIN Pessoas P WITH(NOLOCK) ON v.Cliente_Ven = P.cod_pes
INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
WHERE rec.Tipo_Rec = 'S'
AND v.Vendedor_Ven = {vendedor_cod}
ORDER BY rec.Data_Rec
"""
result_detalhe = execute_query(detalhe_query)
print(f"  Total de registros: {len(result_detalhe)}")
total_soma = 0
for r in result_detalhe:
    total = float(r.get('TotalRecebido') or 0)
    total_soma += total
    data = r.get('DataRecebimento')
    data_str = data.strftime('%d/%m/%Y') if data else 'N/A'
    print(f"    Venda {r.get('Venda')}: R$ {total:,.2f} ({data_str}) - {r.get('Cliente', '')[:30]}")

print(f"\n  SOMA MANUAL: R$ {total_soma:,.2f}")

# 5. Verificar recebimentos na tabela Recebidas sem filtro de Tipo_Rec
print(f"\n5. TODOS OS RECEBIMENTOS (Recebidas, qualquer Tipo_Rec):")
todos_receb_query = f"""
SELECT 
    rec.NumVend_Rec as Venda,
    rec.Tipo_Rec,
    rec.Data_Rec as DataRecebimento,
    (rec.Valor_Rec + rec.ValorConf_Rec) as ValorRecebido,
    P.Nome_pes as Cliente
FROM Recebidas rec WITH(NOLOCK)
INNER JOIN (
    SELECT Num_Ven, Vendedor_Ven, Cliente_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK)
    WHERE Status_Ven = 0
    UNION ALL
    SELECT Num_VRec, Vendedor_VRec, Cliente_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK)
    WHERE Status_VRec = 0
) v ON rec.NumVend_Rec = v.Num_Ven AND rec.Empresa_Rec = v.Empresa_Ven AND rec.Obra_Rec = v.Obra_Ven
LEFT JOIN Pessoas P WITH(NOLOCK) ON v.Cliente_Ven = P.cod_pes
INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
WHERE v.Vendedor_Ven = {vendedor_cod}
ORDER BY rec.Tipo_Rec, rec.Data_Rec
"""
result_todos = execute_query(todos_receb_query)
print(f"  Total de registros: {len(result_todos)}")
tipos = {}
for r in result_todos:
    tipo = r.get('Tipo_Rec', 'N/A')
    if tipo not in tipos:
        tipos[tipo] = {'qtd': 0, 'valor': 0}
    tipos[tipo]['qtd'] += 1
    tipos[tipo]['valor'] += float(r.get('ValorRecebido') or 0)

for tipo, dados in tipos.items():
    print(f"    Tipo {tipo}: {dados['qtd']} registros, Total: R$ {dados['valor']:,.2f}")

print("\n" + "=" * 70)
print("FIM DO DEBUG")
print("=" * 70)
