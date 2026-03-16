"""
Testar query de recebimentos corrigida - mesma estrutura que recebimentos.py
"""
import sys
sys.path.insert(0, '.')
from database import execute_query

empresa = 28
obra = '70100'

# Datas de dezembro 2025
data_inicio_fmt = '01/12/2025'
data_fim_fmt = '31/12/2025'
contas_filter = "('13005587-5', '529-5', '529-0', '27083-6')"

# Query corrigida igual ao relatorio_executivo.py
query = f"""
SELECT COUNT(*) as qtd, 
ISNULL(SUM(RecebePgtoDiv.PercentValor_Rpd * (CAST((ItensRecebidas.Qtde_Itr * ItensRecebidas.PrecoProc_Itr - ItensRecebidas.ValComissaoDir_Itr) AS NUMERIC(18, 6)) / NULLIF(VendasRecebidas.ValorTot_VRec, 0))), 0) as valor
FROM (SELECT * FROM Extrato WITH(NOLOCK) WHERE Tipo_Doc = 1 AND Empresa_doc = {empresa} AND Conta_doc IN {contas_filter} AND Data_Doc BETWEEN '{data_inicio_fmt}' AND '{data_fim_fmt}') [Extrato]
INNER JOIN Depositos WITH(NOLOCK) ON Extrato.Empresa_Doc = Depositos.Empresa_Dep AND Extrato.Banco_Doc = Depositos.Banco_Dep AND Extrato.Conta_Doc = Depositos.Conta_Dep AND Extrato.Numero_Doc = Depositos.Numero_Dep
INNER JOIN (SELECT * FROM RecebePgto WITH(NOLOCK) WHERE Status_Rpg <> 2) [RecebePgto] ON Depositos.Empresa_Dep = RecebePgto.Empresa_Rpg AND Depositos.Numero_Dep = RecebePgto.NumDep_Rpg AND Depositos.Banco_Dep = RecebePgto.BancoDep_Rpg AND Depositos.Conta_Dep = RecebePgto.ContaDep_Rpg
INNER JOIN RecebePgtoDiv WITH(NOLOCK) ON RecebePgto.Empresa_Rpg = RecebePgtoDiv.Empresa_Rpd AND RecebePgto.NumReceb_Rpg = RecebePgtoDiv.NumReceb_Rpd AND RecebePgto.Tipo_Rpg = RecebePgtoDiv.TipoRpg_Rpd AND RecebePgto.NumCont_Rpg = RecebePgtoDiv.NumCont_Rpd
INNER JOIN Recebidas WITH(NOLOCK) ON RecebePgtoDiv.Empresa_Rpd = Recebidas.Empresa_Rec AND RecebePgtoDiv.Obra_Rpd = Recebidas.Obra_Rec AND RecebePgtoDiv.NumVend_Rpd = Recebidas.NumVend_Rec AND RecebePgtoDiv.NumParc_Rpd = Recebidas.NumParc_Rec AND RecebePgtoDiv.ParcType_Rpd = Recebidas.ParcType_Rec AND RecebePgtoDiv.Tipo_Rpd = Recebidas.Tipo_Rec AND RecebePgtoDiv.NumParcGer_Rpd = Recebidas.NumParcGer_Rec
INNER JOIN VendasRecebidas WITH(NOLOCK) ON Recebidas.Empresa_Rec = VendasRecebidas.Empresa_VRec AND Recebidas.Obra_Rec = VendasRecebidas.Obra_VRec AND Recebidas.NumVend_Rec = VendasRecebidas.Num_VRec
INNER JOIN ItensRecebidas WITH(NOLOCK) ON VendasRecebidas.Empresa_VRec = ItensRecebidas.Empresa_Itr AND VendasRecebidas.Obra_VRec = ItensRecebidas.Obra_Itr AND VendasRecebidas.Num_VRec = ItensRecebidas.NumVend_Itr
WHERE Recebidas.Obra_Rec = '{obra}'
"""

print("="*70)
print("TESTE RECEBIMENTOS - QUERY CORRIGIDA")
print("="*70)

try:
    result = execute_query(query)
    qtd = result[0].get('qtd', 0) if result else 0
    valor = float(result[0].get('valor', 0) or 0) if result else 0
    print(f"Quantidade: {qtd}")
    print(f"Valor: R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print(f"\nValor esperado (tela): R$ 782.609,57")
    print(f"Diferença: R$ {valor - 782609.57:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    if abs(valor - 782609.57) < 1:
        print("\n✅ VALORES BATEM!")
    else:
        print(f"\n⚠️ DIFERENÇA DE R$ {abs(valor - 782609.57):,.2f}")
except Exception as e:
    print(f"ERRO: {e}")

print("="*70)
