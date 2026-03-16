"""
VallePrime Dashboard - Mensagens Routes
"""

from fastapi import APIRouter, Query, HTTPException
from database import execute_query
from datetime import date

router = APIRouter()

@router.get("/mensagens/resumo-diario")
async def get_resumo_diario(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Busca resumo diário para mensagem do WhatsApp"""
    
    # Get today's date
    hoje = date.today()
    
    # Query 1: Vendas do dia e mês - using SQL Server date functions
    vendas_query = f"""
    DECLARE @DataInicial date = DATEADD(day, 1-DAY(GETDATE()), CONVERT(date, GETDATE()))
    DECLARE @DataFinal date = CONVERT(date, GETDATE())
    
    SELECT 
        SUM(CASE WHEN CONVERT(date, DataCad_Ven) = @DataFinal THEN 1 ELSE 0 END) AS qtdVendasDia,
        SUM(CASE WHEN CONVERT(date, DataCad_Ven) = @DataFinal THEN (ValorTot_Ven - Desconto_Ven) ELSE 0 END) AS valorVendasDia,
        COUNT(*) AS qtdVendasMes,
        SUM(ValorTot_Ven - Desconto_Ven) AS valorVendasMes
    FROM Vendas WITH(NOLOCK)
    WHERE Empresa_Ven = {empresa} 
      AND Obra_Ven = '{obra}'
      AND DataCad_Ven BETWEEN @DataInicial AND @DataFinal
    """
    
    # Query 2: Total de vendas (QTD_TOTAL_VENDAS)
    total_qtd_query = f"""
    SELECT COUNT(*) AS qtdTotalVendas FROM Vendas WITH(NOLOCK) 
    WHERE Empresa_ven = {empresa} AND Obra_Ven = '{obra}'
    """
    
    # Query 2b: Total a receber - usando ContasReceber que funciona
    total_valor_query = f"""
    SELECT ISNULL(SUM(Valor_Prc), 0) AS valorTotalCR 
    FROM ContasReceber WITH(NOLOCK) 
    WHERE Empresa_prc = {empresa} AND Obra_Prc = '{obra}' AND Status_Prc = 0
    """
    
    # Query 2c: Total - BASEADA NO DADOS2 DO EXCEL
    # O Excel usa o valor das unidades com Vendido_unid = 1 (Vendido)
    # usando ValPrecoPerc_Unid que é o valor atualizado baseado na tabela de preços
    total_produtos_query = f"""
    DECLARE @DataFinal date = CONVERT(date, GETDATE())
    
    SELECT ISNULL(SUM(ValPrecoPerc_Unid), 0) AS valorTotalProdutos
    FROM (
        SELECT 
            CASE WHEN ud.TipoContrato_udt IN (1,2,4)
                THEN up.ValPreco_Unid
                ELSE (SELECT TOP 1 cpp.Valor_cpp 
                      FROM CategoriasPrecoProd cpp
                      WHERE cpp.NumProd_cpp = up.Prod_unid
                        AND cpp.Codigo_cpp = up.Codigo_unid
                        AND cpp.Empresa_cpp = up.Empresa_unid
                        AND cpp.Data_cpp <= @DataFinal
                      ORDER BY cpp.Data_cpp DESC)
            END * (up.PorcentPr_unid / 100) * up.Qtde_unid AS ValPrecoPerc_Unid
        FROM UnidadePer up WITH(NOLOCK)
        LEFT JOIN UnidadeDetalhe ud WITH(NOLOCK)
            ON up.Empresa_unid = ud.Empresa_udt
           AND up.Prod_unid = ud.Prod_udt
           AND up.NumPer_unid = ud.NumPer_udt
        WHERE up.Empresa_unid = {empresa} 
          AND up.Obra_unid = '{obra}'
          AND up.Vendido_unid = 1  -- Apenas unidades VENDIDAS
    ) AS UnidadesVendidas
    """
    
    # Query 3: Distratos do dia e mês
    distratos_query = f"""
    DECLARE @DataInicial date = DATEADD(day, 1-DAY(GETDATE()), CONVERT(date, GETDATE()))
    DECLARE @DataFinal date = CONVERT(date, GETDATE())
    
    SELECT 
        SUM(CASE WHEN CONVERT(date, DataAprov_vdd) = @DataFinal THEN 1 ELSE 0 END) AS qtdDistratoDia,
        COUNT(*) AS qtdDistratoMes
    FROM VendaDistrato WITH(NOLOCK)
    WHERE Empresa_vdd = {empresa} 
      AND Obra_vdd = '{obra}'
      AND StatusAprov_vdd = 1
      AND TipoAditivo_vdd = 0
      AND DataAprov_vdd BETWEEN @DataInicial AND @DataFinal
    """
    
    # Query 4: Estoque por tipo
    estoque_query = f"""
    SELECT 
        Vendido_unid,
        CASE Vendido_unid
            WHEN 0 THEN 'Disponível'
            WHEN 1 THEN 'Vendido'
            WHEN 2 THEN 'Reservado'
            WHEN 3 THEN 'Proposta'
            WHEN 4 THEN 'Quitado'
            WHEN 5 THEN 'Escriturado'
            WHEN 6 THEN 'Em venda'
            WHEN 7 THEN 'Suspenso'
            WHEN 8 THEN 'Fora de venda'
            WHEN 9 THEN 'Em acerto'
            WHEN 10 THEN 'Dação'
        END AS tipoEstoque,
        COUNT(*) AS quantidade
    FROM UnidadePer WITH(NOLOCK)
    WHERE Empresa_unid = {empresa} AND Obra_unid = '{obra}'
    GROUP BY Vendido_unid
    """
    
    # Query 5: Nome do empreendimento
    obra_query = f"""
    SELECT descr_obr FROM Obras WITH(NOLOCK)
    WHERE Empresa_obr = {empresa} AND Cod_obr = '{obra}'
    """
    
    try:
        vendas_result = execute_query(vendas_query)
        total_qtd_result = execute_query(total_qtd_query)
        
        # Try ContasReceberCalc with error capture
        try:
            total_valor_result = execute_query(total_valor_query)
            print(f"DEBUG total_valor_result: {total_valor_result}")
            valor_total = float(total_valor_result[0].get('valorTotalCR', 0) or 0) if total_valor_result else 0
        except Exception as valor_err:
            print(f"ERROR in ContasReceberCalc query: {valor_err}")
            valor_total = 0
        
        # Query valorTotalProdutos (ValorTot_Ven sem desconto)
        try:
            total_produtos_result = execute_query(total_produtos_query)
            valor_total_produtos = float(total_produtos_result[0].get('valorTotalProdutos', 0) or 0) if total_produtos_result else 0
        except Exception as prod_err:
            print(f"ERROR in total_produtos_query: {prod_err}")
            valor_total_produtos = 0
        
        distratos_result = execute_query(distratos_query)
        estoque_result = execute_query(estoque_query)
        obra_result = execute_query(obra_query)
        
        # Process results
        vendas = vendas_result[0] if vendas_result else {}
        qtd_total = total_qtd_result[0].get('qtdTotalVendas', 0) if total_qtd_result else 0
        distratos = distratos_result[0] if distratos_result else {}
        
        # Map estoque
        estoque = {}
        total_estoque = 0
        for e in estoque_result:
            tipo = e.get('tipoEstoque', 'Outro')
            qtd = e.get('quantidade', 0)
            estoque[tipo] = qtd
            total_estoque += qtd
        
        nome_obra = obra_result[0]['descr_obr'] if obra_result else f"Obra {obra}"
        
        # Override para nomes específicos
        if empresa == 999 and obra == '70100':
            nome_obra = "VALLE DO IPITINGA ML - TOMÉ - AÇU"
        
        return {
            "nomeObra": nome_obra,
            "data": hoje.strftime('%d/%m/%Y'),
            "vendas": {
                "qtdDia": vendas.get('qtdVendasDia', 0) or 0,
                "valorDia": float(vendas.get('valorVendasDia', 0) or 0),
                "qtdMes": vendas.get('qtdVendasMes', 0) or 0,
                "valorMes": float(vendas.get('valorVendasMes', 0) or 0),
                "qtdTotal": qtd_total or 0,
                "valorTotal": valor_total,
                "valorTotalProdutos": valor_total_produtos
            },
            "distratos": {
                "qtdDia": distratos.get('qtdDistratoDia', 0) or 0,
                "qtdMes": distratos.get('qtdDistratoMes', 0) or 0
            },
            "estoque": {
                "disponivel": estoque.get('Disponível', 0),
                "reservado": estoque.get('Reservado', 0),
                "suspenso": estoque.get('Suspenso', 0),
                "foraVenda": estoque.get('Fora de venda', 0),
                "vendido": estoque.get('Vendido', 0),
                "quitado": estoque.get('Quitado', 0),
                "total": total_estoque
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
