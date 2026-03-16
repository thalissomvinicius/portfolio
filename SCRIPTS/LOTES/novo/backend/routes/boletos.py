"""
VallePrime Dashboard - Boletos Routes
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from database import execute_query

router = APIRouter()

@router.get("/boletos")
async def get_boletos(
    empresa: int = Query(..., description="Código da empresa"),
    venda: Optional[int] = Query(None, description="Filtrar por venda específica")
):
    """Busca todos os boletos gerados"""
    query = """
    SELECT 
        RecebAutoConfirmado.Empresa_rea AS empresa,
        RecebAutoConfirmado.ObraPrc_Rea AS obra,
        RecebAutoConfirmado.NumVendPrc_Rea AS venda,
        RecebAutoConfirmado.NumParcPrc_Rea AS parcela,
        RecebAutoConfirmado.TipoPrc_Rea AS tipo,
        RecebAutoConfirmado.UsrCad_Rea AS usuarioGerou,
        FORMAT(RecebAutoConfirmado.DataGera_Rea, 'dd/MM/yyyy HH:mm') AS dataGeracao,
        RecebAutoConfirmado.UsrAlt_Rea AS usuarioAlterou,
        Pessoas.nome_pes AS cliente,
        BoletoConfirmado.SeuNum_Bol AS nossoNumero,
        BoletoConfirmado.NossoNum_Bol AS numeroBoleto,
        FORMAT(BoletoConfirmado.DataEmis_Bol, 'dd/MM/yyyy') AS dataEmissao,
        FORMAT(BoletoConfirmado.DataVenc_Bol, 'dd/MM/yyyy') AS dataVencimento,
        FORMAT(BoletoConfirmado.DataGera_Bol, 'dd/MM/yyyy HH:mm') AS dataGeracaoBoleto,
        BoletoConfirmado.ValDoc_Bol AS valorDocumento,
        CASE 
            WHEN BoletoConfirmado.DataEnvioPorEmail_bol IS NOT NULL THEN 1
            ELSE 0
        END AS enviadoEmail,
        CASE 
            WHEN RecebAutoConfirmado.UsrAlt_Rea IS NOT NULL AND RecebAutoConfirmado.UsrAlt_Rea <> RecebAutoConfirmado.UsrCad_Rea THEN 1
            ELSE 0
        END AS foiAlterado
    FROM RecebAutoConfirmado WITH(NOLOCK)
    INNER JOIN BoletoConfirmado WITH(NOLOCK) 
        ON RecebAutoConfirmado.SeuNum_Rea = BoletoConfirmado.SeuNum_Bol
        AND RecebAutoConfirmado.Banco_Rea = BoletoConfirmado.Banco_Bol
        AND RecebAutoConfirmado.NumBol_Rea = BoletoConfirmado.Num_Bol
    INNER JOIN Pessoas WITH(NOLOCK) ON BoletoConfirmado.ClienteVen_bol = Pessoas.cod_pes
    WHERE RecebAutoConfirmado.Empresa_rea = ?
    ORDER BY RecebAutoConfirmado.NumVendPrc_Rea, RecebAutoConfirmado.NumParcPrc_Rea
    """
    
    try:
        results = execute_query(query, (empresa,))
        
        # Filter by venda if specified
        if venda:
            results = [r for r in results if r['venda'] == venda]
        
        # Calculate metrics
        total_valor = sum(r['valorDocumento'] or 0 for r in results)
        enviados = sum(1 for r in results if r['enviadoEmail'])
        
        return {
            "data": results, 
            "total": len(results),
            "metrics": {
                "totalBoletos": len(results),
                "enviadosEmail": enviados,
                "valorTotal": total_valor
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/boletos/vendas")
async def get_vendas_com_boleto(
    empresa: int = Query(..., description="Código da empresa")
):
    """Lista vendas que possuem boletos"""
    query = """
    SELECT DISTINCT RecebAuto.NumVendPrc_Rea AS venda
    FROM RecebAuto WITH(NOLOCK)
    INNER JOIN Boleto WITH(NOLOCK) 
        ON RecebAuto.SeuNum_Rea = Boleto.SeuNum_Bol
        AND RecebAuto.Banco_Rea = Boleto.Banco_Bol
    WHERE RecebAuto.Empresa_rea = ?
    ORDER BY RecebAuto.NumVendPrc_Rea
    """
    
    try:
        results = execute_query(query, (empresa,))
        vendas = [r['venda'] for r in results]
        return {"vendas": vendas, "total": len(vendas)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
