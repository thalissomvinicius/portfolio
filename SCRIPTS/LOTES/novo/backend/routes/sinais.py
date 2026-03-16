"""
VallePrime Dashboard - Sinais Routes
"""

from fastapi import APIRouter, Query, HTTPException
from database import execute_query

router = APIRouter()

@router.get("/sinais")
async def get_sinais_corretagem(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    data_vencimento: str = Query(..., description="Data limite de vencimento (YYYY-MM-DD)")
):
    """Busca sinais de corretagem a receber"""
    query = f"""
    SELECT 
        c.nome_pes as corretor,
        p.nome_pes as cliente,
        r.Empresa_prc as empresa,
        r.NumVend_prc as venda,
        r.Obra_Prc as obra,
        u.C1_unid as quadra,
        u.C2_unid as lote,
        FORMAT(vendas.Data_Ven,'dd/MM/yyyy') as dataVenda,
        FORMAT(vendas.DataCad_Ven,'dd/MM/yyyy') as dataCadastro,
        vendas.[Vlr. Venda] as valorVenda,
        r.NumParc_Prc as parcela,
        r.TotParc_Prc as qtdParcelas,
        FORMAT(r.Data_Prc,'dd/MM/yyyy') as vencimento,
        FORMAT(r.DataPror_Prc,'dd/MM/yyyy') as prorrogacao,
        r.Valor_Prc as valorParcela
    FROM ContasReceber r WITH(NOLOCK)
    INNER JOIN pessoas p WITH(NOLOCK) ON p.cod_pes = r.Cliente_Prc
    INNER JOIN (
        SELECT v.empresa_ven, v.num_ven, v.obra_ven, v.vendedor_ven, v.cliente_ven,
               (v.ValorTot_Ven + v.Acrescimo_Ven - v.Desconto_Ven) AS 'Vlr. Venda',
               v.Data_ven, v.datacad_ven
        FROM vendas v WITH(NOLOCK)
        UNION
        SELECT vr.empresa_vrec, vr.num_vrec, vr.obra_vrec, vr.vendedor_vrec, vr.cliente_vrec,
               (vr.ValorTot_VRec + vr.Acrescimo_VRec - vr.Desconto_VRec) AS 'Vlr. Venda',
               vr.Data_VRec, vr.DataCad_VRec
        FROM VendasRecebidas vr WITH(NOLOCK)
    ) as vendas ON vendas.Empresa_ven = r.Empresa_prc 
                AND vendas.Obra_Ven = r.Obra_Prc 
                AND vendas.Num_Ven = r.NumVend_prc
    INNER JOIN pessoas c WITH(NOLOCK) ON c.cod_pes = vendas.Vendedor_Ven
    INNER JOIN (
        SELECT Empresa_itv, NumVend_Itv, Obra_Itv, Produto_Itv, CodPerson_Itv 
        FROM ItensVenda WITH(NOLOCK)
        UNION
        SELECT Empresa_itr, NumVend_Itr, Obra_Itr, Produto_Itr, CodPerson_Itr 
        FROM ItensRecebidas WITH(NOLOCK)
    ) as ItensVendas ON ItensVendas.Empresa_itv = r.Empresa_prc 
                     AND ItensVendas.Obra_Itv = r.Obra_Prc 
                     AND ItensVendas.NumVend_Itv = r.NumVend_prc
    LEFT JOIN UnidadePer u WITH(NOLOCK) ON ItensVendas.Empresa_itv = u.Empresa_unid 
                                        AND ItensVendas.Produto_Itv = u.Prod_unid 
                                        AND ItensVendas.CodPerson_Itv = u.NumPer_unid
    WHERE vendas.Empresa_ven = {empresa} 
      AND r.Empresa_prc = {empresa} 
      AND r.Tipo_Prc IN ('S') 
      AND r.Obra_Prc = '{obra}' 
      AND r.Data_Prc <= CONVERT(date, '{data_vencimento}', 23)
    ORDER BY r.NumVend_prc, r.NumParc_Prc
    """
    
    try:
        results = execute_query(query)
        total_valor = sum(r['valorParcela'] or 0 for r in results)
        vendas_distintas = len(set(r['venda'] for r in results))
        
        return {
            "data": results, 
            "total": len(results),
            "metrics": {
                "totalParcelas": len(results),
                "valorTotal": total_valor,
                "vendasDistintas": vendas_distintas
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sinais/abertos")
async def get_sinais_abertos(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Busca contagem de sinais em aberto por venda"""
    query = f"""
    SELECT 
        r.NumVend_prc as venda,
        COUNT(*) as qtdSinaisAberto
    FROM ContasReceber r WITH(NOLOCK)
    WHERE r.Empresa_prc = {empresa}
      AND r.Obra_Prc = '{obra}'
      AND r.Tipo_Prc = 'S'
      AND r.Status_Prc = 0
    GROUP BY r.NumVend_prc
    """
    
    try:
        results = execute_query(query)
        return {"data": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sinais/pagos/{venda}")
async def get_sinais_pagos(
    venda: int,
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Busca sinais pagos de uma venda específica"""
    query = """
    SELECT 
        Recebidas.Empresa_Rec as empresa,
        Recebidas.Obra_Rec as obra,
        Recebidas.NumVend_Rec AS venda,
        Recebidas.NumParc_Rec AS parcela,
        Recebidas.Tipo_Rec as tipo,
        FORMAT(Recebidas.Data_Rec, 'dd/MM/yyyy') AS dataRecebimento,
        FORMAT(Recebidas.DataVenci_Rec, 'dd/MM/yyyy') AS dataVencimento,
        Recebidas.Valor_Rec + Recebidas.ValorConf_Rec AS valorPago,
        Pessoas.nome_pes AS cliente
    FROM Recebidas WITH(NOLOCK)
    INNER JOIN VendasRecebidas WITH(NOLOCK) 
        ON VendasRecebidas.Empresa_VRec = Recebidas.Empresa_Rec
        AND VendasRecebidas.Obra_VRec = Recebidas.Obra_Rec
        AND VendasRecebidas.Num_VRec = Recebidas.NumVend_Rec
    INNER JOIN Pessoas WITH(NOLOCK) ON Pessoas.Cod_pes = Recebidas.Cliente_Rec
    WHERE Recebidas.Obra_Rec = ?
      AND Recebidas.NumVend_Rec = ?
      AND Recebidas.Empresa_Rec = ?
      AND Recebidas.Tipo_Rec = 'S'
      AND Recebidas.Status_Rec = 1
    ORDER BY Recebidas.NumParc_Rec
    """
    
    try:
        results = execute_query(query, (obra, venda, empresa))
        return {"data": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
