"""Debug para verificar duplicação entre Vendas e VendasRecebidas"""
from database import execute_query

empresa = 28
obra = '70100'
vendedor_cod = 73242  # RAIMUNDO CESAR
emp_obra_param = f"{empresa}|{obra}"

print("=" * 70)
print("VERIFICANDO DUPLICAÇÃO")
print("=" * 70)

# Verificar se as vendas existem em ambas as tabelas
print("\n1. VENDAS NA TABELA 'Vendas':")
query_vendas = f"""
SELECT Num_Ven, Status_Ven, Vendedor_Ven, Empresa_Ven, Obra_Ven
FROM Vendas WITH(NOLOCK)
WHERE Vendedor_Ven = {vendedor_cod}
AND Empresa_Ven = {empresa}
AND Obra_Ven = '{obra}'
AND Status_Ven = 0
"""
result_vendas = execute_query(query_vendas)
print(f"  Total: {len(result_vendas)}")
for v in result_vendas:
    print(f"    Venda {v.get('Num_Ven')}, Status: {v.get('Status_Ven')}")

print("\n2. VENDAS NA TABELA 'VendasRecebidas':")
query_vendas_rec = f"""
SELECT Num_VRec, Status_VRec, Vendedor_VRec, Empresa_VRec, Obra_VRec
FROM VendasRecebidas WITH(NOLOCK)
WHERE Vendedor_VRec = {vendedor_cod}
AND Empresa_VRec = {empresa}
AND Obra_VRec = '{obra}'
AND Status_VRec = 0
"""
result_vendas_rec = execute_query(query_vendas_rec)
print(f"  Total: {len(result_vendas_rec)}")
for v in result_vendas_rec:
    print(f"    Venda {v.get('Num_VRec')}, Status: {v.get('Status_VRec')}")

# Verificar se há vendas em comum (mesmo Num_Ven)
vendas_set = set(v.get('Num_Ven') for v in result_vendas)
vendas_rec_set = set(v.get('Num_VRec') for v in result_vendas_rec)
duplicados = vendas_set.intersection(vendas_rec_set)

print(f"\n3. VENDAS DUPLICADAS (existem em ambas as tabelas):")
print(f"  Total de duplicados: {len(duplicados)}")
if duplicados:
    for d in sorted(duplicados):
        print(f"    Venda {d}")

# Verificar os recebimentos da venda 259 especificamente
print("\n4. RECEBIMENTOS DA VENDA 259 (EXEMPLO):")
query_rec_259 = f"""
SELECT 
    rec.Empresa_Rec,
    rec.Obra_Rec,
    rec.NumVend_Rec,
    rec.SeqPrc_Rec,
    rec.Tipo_Rec,
    rec.Data_Rec,
    rec.Valor_Rec,
    rec.ValorConf_Rec
FROM Recebidas rec WITH(NOLOCK)
WHERE rec.Empresa_Rec = {empresa}
AND rec.Obra_Rec = '{obra}'
AND rec.NumVend_Rec = 259
AND rec.Tipo_Rec = 'S'
ORDER BY rec.Data_Rec
"""
result_rec = execute_query(query_rec_259)
print(f"  Total de registros: {len(result_rec)}")
for r in result_rec:
    print(f"    Seq {r.get('SeqPrc_Rec')}: R$ {float(r.get('Valor_Rec') or 0) + float(r.get('ValorConf_Rec') or 0):,.2f} ({r.get('Data_Rec')})")

# Recalcular corretamente SEM duplicar via UNION ALL
print("\n5. RECÁLCULO SEM DUPLICAÇÃO (usando apenas Vendas OU VendasRecebidas):")

# Opção 1: Usar Recebidas diretamente sem o UNION de vendas
query_direto = f"""
SELECT 
    COUNT(*) AS qtdSinais,
    SUM(rec.Valor_Rec + rec.ValorConf_Rec) AS valorTotal
FROM Recebidas rec WITH(NOLOCK)
WHERE rec.Empresa_Rec = {empresa}
AND rec.Obra_Rec = '{obra}'
AND rec.Tipo_Rec = 'S'
AND EXISTS (
    SELECT 1 FROM Vendas V WITH(NOLOCK)
    WHERE V.Empresa_Ven = rec.Empresa_Rec
    AND V.Obra_Ven = rec.Obra_Rec
    AND V.Num_Ven = rec.NumVend_Rec
    AND V.Vendedor_Ven = {vendedor_cod}
    AND V.Status_Ven = 0
)
"""
result_direto = execute_query(query_direto)
if result_direto:
    r = result_direto[0]
    print(f"  Via Vendas: {r.get('qtdSinais')} sinais, R$ {float(r.get('valorTotal') or 0):,.2f}")

# Opção 2: Usando VendasRecebidas
query_direto2 = f"""
SELECT 
    COUNT(*) AS qtdSinais,
    SUM(rec.Valor_Rec + rec.ValorConf_Rec) AS valorTotal
FROM Recebidas rec WITH(NOLOCK)
WHERE rec.Empresa_Rec = {empresa}
AND rec.Obra_Rec = '{obra}'
AND rec.Tipo_Rec = 'S'
AND EXISTS (
    SELECT 1 FROM VendasRecebidas VR WITH(NOLOCK)
    WHERE VR.Empresa_VRec = rec.Empresa_Rec
    AND VR.Obra_VRec = rec.Obra_Rec
    AND VR.Num_VRec = rec.NumVend_Rec
    AND VR.Vendedor_VRec = {vendedor_cod}
    AND VR.Status_VRec = 0
)
"""
result_direto2 = execute_query(query_direto2)
if result_direto2:
    r = result_direto2[0]
    print(f"  Via VendasRecebidas: {r.get('qtdSinais')} sinais, R$ {float(r.get('valorTotal') or 0):,.2f}")

# Opção 3: UNION sem ALL (elimina duplicados)
query_union = f"""
SELECT 
    COUNT(*) AS qtdSinais,
    SUM(ValorRecebido) AS valorTotal
FROM (
    SELECT DISTINCT rec.Empresa_Rec, rec.Obra_Rec, rec.NumVend_Rec, rec.SeqPrc_Rec,
           (rec.Valor_Rec + rec.ValorConf_Rec) as ValorRecebido
    FROM Recebidas rec WITH(NOLOCK)
    INNER JOIN (
        SELECT Num_Ven, Vendedor_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK)
        WHERE Status_Ven = 0
        UNION
        SELECT Num_VRec, Vendedor_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK)
        WHERE Status_VRec = 0
    ) v ON rec.NumVend_Rec = v.Num_Ven AND rec.Empresa_Rec = v.Empresa_Ven AND rec.Obra_Rec = v.Obra_Ven
    WHERE rec.Tipo_Rec = 'S'
    AND rec.Empresa_Rec = {empresa}
    AND rec.Obra_Rec = '{obra}'
    AND v.Vendedor_Ven = {vendedor_cod}
) t
"""
result_union = execute_query(query_union)
if result_union:
    r = result_union[0]
    print(f"  Via UNION (sem ALL): {r.get('qtdSinais')} sinais, R$ {float(r.get('valorTotal') or 0):,.2f}")

print("\n" + "=" * 70)
print("FIM")
print("=" * 70)
