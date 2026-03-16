"""Test script to verify the transfer chain for Quadra Z Lote 027, venda 21903"""
import pyodbc

connection_string = (
    "Driver={SQL Server};"
    "Server=DCWBD11\\VALLEPRIME_PRD;"
    "Database=UAU-VALLEPRIME;"
    "UID=consultasBD;"
    "PWD=V@lle#2021;"
)

query = """
-- Primeiro, encontrar a venda atual (quitada) do lote
WITH VendaAtual AS (
    SELECT DISTINCT V.Num_Ven as NumVenda, V.Empresa_Ven, V.Obra_Ven, V.Data_Ven, 
           V.ValorTot_Ven, V.Status_Ven, P.Nome_pes as Cliente, P.cpf_pes as CPF, 
           V.DataCessao_Ven as DataCessao, 'Vendas' as Origem
    FROM ItensVenda IV WITH(NOLOCK)
    INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_Itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven AND IV.Obra_Itv = V.Obra_Ven
    INNER JOIN UnidadePer U WITH(NOLOCK) ON IV.Empresa_Itv = U.Empresa_unid AND IV.Obra_Itv = U.Obra_unid 
        AND IV.Produto_Itv = U.Prod_unid AND IV.CodPerson_Itv = U.NumPer_unid
    LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
    WHERE U.Empresa_unid = 999 AND U.Obra_unid = '70100' 
      AND RTRIM(LTRIM(U.C1_unid)) = 'Z' AND RTRIM(LTRIM(U.C2_unid)) = '027'
      AND V.Status_Ven IN (0, 3)  -- Normal ou Quitado (venda vigente)
      
    UNION
    
    SELECT DISTINCT VR.Num_VRec as NumVenda, VR.Empresa_VRec, VR.Obra_VRec, VR.Data_VRec, 
           VR.ValorTot_VRec, VR.Status_VRec, P.Nome_pes as Cliente, P.cpf_pes as CPF,
           VR.DataCessao_VRec as DataCessao, 'VendasRecebidas' as Origem
    FROM ItensRecebidas IR WITH(NOLOCK)
    INNER JOIN VendasRecebidas VR WITH(NOLOCK) ON IR.Empresa_Itr = VR.Empresa_VRec AND IR.NumVend_Itr = VR.Num_VRec AND IR.Obra_Itr = VR.Obra_VRec
    INNER JOIN UnidadePer U WITH(NOLOCK) ON IR.Empresa_Itr = U.Empresa_unid AND IR.Obra_Itr = U.Obra_unid 
        AND IR.Produto_Itr = U.Prod_unid AND IR.CodPerson_Itr = U.NumPer_unid
    LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
    WHERE U.Empresa_unid = 999 AND U.Obra_unid = '70100' 
      AND RTRIM(LTRIM(U.C1_unid)) = 'Z' AND RTRIM(LTRIM(U.C2_unid)) = '027'
      AND VR.Status_VRec IN (0, 3)
),
-- Agora buscar vendas anteriores via VendaHist (cadeia de cessões)
VendasAnteriores AS (
    -- Vendas anteriores que foram cessão para a venda atual
    SELECT DISTINCT VH.NumVend_vhist as NumVenda, VA.Empresa_Ven, VA.Obra_Ven, V.Data_Ven, 
           V.ValorTot_Ven, V.Status_Ven, P.Nome_pes as Cliente, P.cpf_pes as CPF,
           VH.DataAssinaturaCessao_vhist as DataCessao, 'CessaoAnterior' as Origem
    FROM VendaAtual VA
    INNER JOIN VendaHist VH WITH(NOLOCK) 
        ON VH.Empresa_vhist = VA.Empresa_Ven 
        AND VH.Obra_vhist = VA.Obra_Ven 
        AND VH.NumNovaVend_vhist = VA.NumVenda
        AND VH.TipoMnt_vhist = 2  -- Tipo 2 = Cessão
    LEFT JOIN (
        SELECT Empresa_Ven, Obra_Ven, Num_Ven, Data_Ven, ValorTot_Ven, Cliente_Ven, Status_Ven
        FROM Vendas WITH(NOLOCK)
        UNION ALL
        SELECT Empresa_VRec, Obra_VRec, Num_VRec, Data_VRec, ValorTot_VRec, Cliente_VRec, Status_VRec
        FROM VendasRecebidas WITH(NOLOCK)
    ) V ON V.Empresa_Ven = VH.Empresa_vhist AND V.Obra_Ven = VH.Obra_vhist AND V.Num_Ven = VH.NumVend_vhist
    LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
    
    UNION
    
    -- Vendas 2 níveis atrás (cessão da cessão)
    SELECT DISTINCT VH2.NumVend_vhist as NumVenda, VA.Empresa_Ven, VA.Obra_Ven, V.Data_Ven, 
           V.ValorTot_Ven, V.Status_Ven, P.Nome_pes as Cliente, P.cpf_pes as CPF,
           VH2.DataAssinaturaCessao_vhist as DataCessao, 'CessaoAnterior2' as Origem
    FROM VendaAtual VA
    INNER JOIN VendaHist VH WITH(NOLOCK) 
        ON VH.Empresa_vhist = VA.Empresa_Ven 
        AND VH.Obra_vhist = VA.Obra_Ven 
        AND VH.NumNovaVend_vhist = VA.NumVenda
        AND VH.TipoMnt_vhist = 2
    INNER JOIN VendaHist VH2 WITH(NOLOCK) 
        ON VH2.Empresa_vhist = VH.Empresa_vhist 
        AND VH2.Obra_vhist = VH.Obra_vhist 
        AND VH2.NumNovaVend_vhist = VH.NumVend_vhist
        AND VH2.TipoMnt_vhist = 2
    LEFT JOIN (
        SELECT Empresa_Ven, Obra_Ven, Num_Ven, Data_Ven, ValorTot_Ven, Cliente_Ven, Status_Ven
        FROM Vendas WITH(NOLOCK)
        UNION ALL
        SELECT Empresa_VRec, Obra_VRec, Num_VRec, Data_VRec, ValorTot_VRec, Cliente_VRec, Status_VRec
        FROM VendasRecebidas WITH(NOLOCK)
    ) V ON V.Empresa_Ven = VH2.Empresa_vhist AND V.Obra_Ven = VH2.Obra_vhist AND V.Num_Ven = VH2.NumVend_vhist
    LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
)
-- União de venda atual + vendas anteriores da cadeia de cessão
SELECT NumVenda, Empresa_Ven, Obra_Ven, Data_Ven, ValorTot_Ven, Cliente, CPF, DataCessao, Origem
FROM VendaAtual
UNION
SELECT NumVenda, Empresa_Ven, Obra_Ven, Data_Ven, ValorTot_Ven, Cliente, CPF, DataCessao, Origem
FROM VendasAnteriores
WHERE NumVenda IS NOT NULL
ORDER BY Data_Ven
"""

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute(query)
    
    print("=== Cadeia de Cessões - Quadra Z Lote 027 ===")
    print("Esperado: 21434 -> 21884 -> 21903\n")
    
    for row in cursor.fetchall():
        print(f"Venda: {row.NumVenda} | Cliente: {row.Cliente} | Data: {row.Data_Ven} | Cessão: {row.DataCessao} | Origem: {row.Origem}")
    
    conn.close()
except Exception as e:
    print(f"Erro: {e}")
