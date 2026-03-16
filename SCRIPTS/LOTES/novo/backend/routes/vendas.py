"""
VallePrime Dashboard - Vendas Routes
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from database import execute_query
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/vendas")
async def get_vendas(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Busca todas as vendas da obra"""
    query = """
    SELECT 
        Vendas.Empresa_Ven AS empresa,
        Vendas.Obra_Ven AS obra,
        Vendas.Num_Ven AS venda,
        Vendas.Cliente_Ven AS clienteId,
        Pessoas.nome_pes AS cliente,
        Vendas.Vendedor_Ven AS vendedorId,
        PessoasVendedor.nome_pes AS corretor,
        FORMAT(Vendas.Data_Ven, 'dd/MM/yyyy') AS dataVenda,
        FORMAT(Vendas.DataCad_Ven, 'dd/MM/yyyy') AS dataCadastro,
        (Vendas.ValorTot_Ven + Vendas.Acrescimo_Ven - Vendas.Desconto_Ven) AS valorTotal,
        Vendas.Obra_Ven + ' - Q' + ISNULL(u.C1_unid, '') + ' L' + ISNULL(u.C2_unid, '') AS identificador,
        Vendas.Status_Ven AS status
    FROM Vendas WITH(NOLOCK)
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.cod_pes
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_itv 
        AND Vendas.Obra_Ven = ItensVenda.Obra_Itv 
        AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer u WITH(NOLOCK) ON ItensVenda.Empresa_itv = u.Empresa_unid 
        AND ItensVenda.Produto_Itv = u.Prod_unid 
        AND ItensVenda.CodPerson_Itv = u.NumPer_unid
    WHERE Vendas.Empresa_Ven = ? AND Vendas.Obra_Ven = ?
    ORDER BY Vendas.Num_Ven
    """
    
    try:
        results = execute_query(query, (empresa, obra))
        return {"data": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/venda/{num}")
async def get_venda_by_num(
    num: int,
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Busca uma venda específica pelo número"""
    query = """
    SELECT 
        Vendas.Empresa_Ven AS empresa,
        Vendas.Obra_Ven AS obra,
        Vendas.Num_Ven AS venda,
        Vendas.Cliente_Ven AS clienteId,
        Pessoas.nome_pes AS cliente,
        Vendas.Vendedor_Ven AS vendedorId,
        PessoasVendedor.nome_pes AS corretor,
        FORMAT(Vendas.Data_Ven, 'dd/MM/yyyy') AS dataVenda,
        FORMAT(Vendas.DataCad_Ven, 'dd/MM/yyyy') AS dataCadastro,
        (Vendas.ValorTot_Ven + Vendas.Acrescimo_Ven - Vendas.Desconto_Ven) AS valorTotal,
        Vendas.Obra_Ven + ' - Q' + ISNULL(u.C1_unid, '') + ' L' + ISNULL(u.C2_unid, '') AS identificador,
        Vendas.Status_Ven AS status
    FROM Vendas WITH(NOLOCK)
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.cod_pes
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_itv 
        AND Vendas.Obra_Ven = ItensVenda.Obra_Itv 
        AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer u WITH(NOLOCK) ON ItensVenda.Empresa_itv = u.Empresa_unid 
        AND ItensVenda.Produto_Itv = u.Prod_unid 
        AND ItensVenda.CodPerson_Itv = u.NumPer_unid
    WHERE Vendas.Empresa_Ven = ? AND Vendas.Obra_Ven = ? AND Vendas.Num_Ven = ?
    """
    
    try:
        results = execute_query(query, (empresa, obra, num))
        if not results:
            raise HTTPException(status_code=404, detail=f"Venda {num} não encontrada")
        return {"data": results[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/venda/cpf/{cpf_cnpj}")
async def get_vendas_by_cpf(
    cpf_cnpj: str,
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Busca vendas pelo CPF ou CNPJ do cliente - otimizado"""
    # Remove caracteres não numéricos do CPF/CNPJ
    cpf_cnpj_limpo = ''.join(filter(str.isdigit, cpf_cnpj))
    
    if not cpf_cnpj_limpo:
        raise HTTPException(status_code=400, detail="CPF/CNPJ inválido")
    
    # Criar padrões para busca com e sem formatação para permitir uso de índices
    # Em vez de REPLACE() no WHERE (que impede índice), buscamos ambos formatos
    patterns = []
    
    # CPF: 401.662.102-00 ou 40166210200
    if len(cpf_cnpj_limpo) == 11:
        # Formato CPF com pontos e hífen
        cpf_formatted = f"{cpf_cnpj_limpo[:3]}.{cpf_cnpj_limpo[3:6]}.{cpf_cnpj_limpo[6:9]}-{cpf_cnpj_limpo[9:]}"
        patterns.append(cpf_formatted)
        patterns.append(cpf_cnpj_limpo)
    elif len(cpf_cnpj_limpo) == 14:
        # Formato CNPJ: 00.000.000/0000-00
        cnpj_formatted = f"{cpf_cnpj_limpo[:2]}.{cpf_cnpj_limpo[2:5]}.{cpf_cnpj_limpo[5:8]}/{cpf_cnpj_limpo[8:12]}-{cpf_cnpj_limpo[12:]}"
        patterns.append(cnpj_formatted)
        patterns.append(cpf_cnpj_limpo)
    else:
        # Busca parcial
        patterns.append(cpf_cnpj_limpo)
    
    # Construir query com OR para cada padrão
    or_conditions = " OR ".join([f"Pessoas.cpf_pes LIKE ?" for _ in patterns])
    
    query = f"""
    SELECT 
        Vendas.Empresa_Ven AS empresa,
        Vendas.Obra_Ven AS obra,
        Vendas.Num_Ven AS venda,
        Vendas.Cliente_Ven AS clienteId,
        Pessoas.nome_pes AS cliente,
        Pessoas.cpf_pes AS cpfCnpj,
        Vendas.Vendedor_Ven AS vendedorId,
        PessoasVendedor.nome_pes AS corretor,
        FORMAT(Vendas.Data_Ven, 'dd/MM/yyyy') AS dataVenda,
        FORMAT(Vendas.DataCad_Ven, 'dd/MM/yyyy') AS dataCadastro,
        (Vendas.ValorTot_Ven + Vendas.Acrescimo_Ven - Vendas.Desconto_Ven) AS valorTotal,
        Vendas.Obra_Ven + ' - Q' + ISNULL(u.C1_unid, '') + ' L' + ISNULL(u.C2_unid, '') AS identificador,
        Vendas.Status_Ven AS status
    FROM Vendas WITH(NOLOCK)
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.cod_pes
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_itv 
        AND Vendas.Obra_Ven = ItensVenda.Obra_Itv 
        AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer u WITH(NOLOCK) ON ItensVenda.Empresa_itv = u.Empresa_unid 
        AND ItensVenda.Produto_Itv = u.Prod_unid 
        AND ItensVenda.CodPerson_Itv = u.NumPer_unid
    WHERE Vendas.Empresa_Ven = ? AND Vendas.Obra_Ven = ?
        AND ({or_conditions})
    ORDER BY Vendas.Num_Ven
    """
    
    try:
        # Parâmetros: empresa, obra, e depois padrões de CPF/CNPJ
        params = [empresa, obra] + [f"%{p}%" for p in patterns]
        results = execute_query(query, tuple(params))
        if not results:
            raise HTTPException(status_code=404, detail=f"Nenhuma venda encontrada para CPF/CNPJ {cpf_cnpj}")
        return {"data": results, "total": len(results)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vendas/buscar-cliente/{nome}")
async def get_vendas_by_cliente(
    nome: str,
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Busca vendas pelo nome do cliente - otimizado para busca rápida"""
    if not nome or len(nome.strip()) < 2:
        raise HTTPException(status_code=400, detail="Nome do cliente deve ter pelo menos 2 caracteres")
    
    query = """
    SELECT 
        Vendas.Empresa_Ven AS empresa,
        Vendas.Obra_Ven AS obra,
        Vendas.Num_Ven AS venda,
        Vendas.Cliente_Ven AS clienteId,
        Pessoas.nome_pes AS cliente,
        Vendas.Vendedor_Ven AS vendedorId,
        PessoasVendedor.nome_pes AS corretor,
        FORMAT(Vendas.Data_Ven, 'dd/MM/yyyy') AS dataVenda,
        FORMAT(Vendas.DataCad_Ven, 'dd/MM/yyyy') AS dataCadastro,
        (Vendas.ValorTot_Ven + Vendas.Acrescimo_Ven - Vendas.Desconto_Ven) AS valorTotal,
        Vendas.Obra_Ven + ' - Q' + ISNULL(u.C1_unid, '') + ' L' + ISNULL(u.C2_unid, '') AS identificador,
        Vendas.Status_Ven AS status
    FROM Vendas WITH(NOLOCK)
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.cod_pes
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_itv 
        AND Vendas.Obra_Ven = ItensVenda.Obra_Itv 
        AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer u WITH(NOLOCK) ON ItensVenda.Empresa_itv = u.Empresa_unid 
        AND ItensVenda.Produto_Itv = u.Prod_unid 
        AND ItensVenda.CodPerson_Itv = u.NumPer_unid
    WHERE Vendas.Empresa_Ven = ? AND Vendas.Obra_Ven = ?
        AND Pessoas.nome_pes LIKE ?
    ORDER BY Vendas.Num_Ven
    """
    
    try:
        results = execute_query(query, (empresa, obra, f"%{nome.strip()}%"))
        if not results:
            raise HTTPException(status_code=404, detail=f"Nenhuma venda encontrada para cliente '{nome}'")
        return {"data": results, "total": len(results)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vendas/buscar-lote")
async def get_venda_by_lote(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    quadra: str = Query(..., description="Número da quadra"),
    lote: str = Query(..., description="Número do lote")
):
    """Busca venda por quadra e lote - otimizado para busca rápida"""
    query = """
    SELECT 
        Vendas.Empresa_Ven AS empresa,
        Vendas.Obra_Ven AS obra,
        Vendas.Num_Ven AS venda,
        Vendas.Cliente_Ven AS clienteId,
        Pessoas.nome_pes AS cliente,
        Vendas.Vendedor_Ven AS vendedorId,
        PessoasVendedor.nome_pes AS corretor,
        FORMAT(Vendas.Data_Ven, 'dd/MM/yyyy') AS dataVenda,
        FORMAT(Vendas.DataCad_Ven, 'dd/MM/yyyy') AS dataCadastro,
        (Vendas.ValorTot_Ven + Vendas.Acrescimo_Ven - Vendas.Desconto_Ven) AS valorTotal,
        Vendas.Obra_Ven + ' - Q' + ISNULL(u.C1_unid, '') + ' L' + ISNULL(u.C2_unid, '') AS identificador,
        Vendas.Status_Ven AS status
    FROM Vendas WITH(NOLOCK)
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.cod_pes
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_itv 
        AND Vendas.Obra_Ven = ItensVenda.Obra_Itv 
        AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer u WITH(NOLOCK) ON ItensVenda.Empresa_itv = u.Empresa_unid 
        AND ItensVenda.Produto_Itv = u.Prod_unid 
        AND ItensVenda.CodPerson_Itv = u.NumPer_unid
    WHERE Vendas.Empresa_Ven = ? AND Vendas.Obra_Ven = ?
        AND RTRIM(LTRIM(u.C1_unid)) = ?
        AND RTRIM(LTRIM(u.C2_unid)) = ?
    ORDER BY Vendas.Num_Ven
    """
    
    try:
        results = execute_query(query, (empresa, obra, quadra.strip(), lote.strip()))
        if not results:
            raise HTTPException(status_code=404, detail=f"Nenhuma venda encontrada para Quadra {quadra}, Lote {lote}")
        return {"data": results, "total": len(results)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/corretores/lista")
async def get_corretores_lista(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Retorna lista de corretores distintos para filtro"""
    query = f"""
    SELECT DISTINCT
        UPPER(ISNULL(PessoasVendedor.nome_pes, 'NAO INFORMADO')) AS corretor
    FROM Vendas WITH(NOLOCK)
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK)
        ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    WHERE Vendas.Empresa_Ven = {empresa}
        AND Vendas.Obra_Ven = '{obra}'
    ORDER BY corretor
    """
    try:
        results = execute_query(query)
        return {"corretores": [r['corretor'] for r in results if r['corretor']]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/corretores/estruturas")
async def get_corretores_estruturas(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)")
):
    """Retorna lista de estruturas/equipes que tiveram vendas naquela obra/periodo"""
    
    date_filter = ""
    if data_inicio and data_fim:
        data_inicio_sql = data_inicio.replace('-', '')
        data_fim_sql = data_fim.replace('-', '')
        date_filter = f"AND (Data_Ven BETWEEN CONVERT(datetime, '{data_inicio_sql}', 112) AND CONVERT(datetime, '{data_fim_sql}', 112))"
    elif data_inicio:
        data_inicio_sql = data_inicio.replace('-', '')
        date_filter = f"AND Data_Ven >= CONVERT(datetime, '{data_inicio_sql}', 112)"
    elif data_fim:
        data_fim_sql = data_fim.replace('-', '')
        date_filter = f"AND Data_Ven <= CONVERT(datetime, '{data_fim_sql}', 112)"

    emp_obra_param = f"{empresa}|{obra}"

    query = f"""
    SELECT DISTINCT
        P_Super.cod_pes as codigo,
        P_Super.nome_pes as nome
    FROM (
        SELECT Vendedor_Ven, Data_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK)
        WHERE Status_Ven = 0 {date_filter}
        UNION
        SELECT Vendedor_VRec, Data_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK)
        WHERE Status_VRec = 0 {date_filter.replace('Data_Ven', 'Data_VRec')}
    ) AS V
    INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON V.Empresa_Ven = Empresa AND V.Obra_Ven = Obra
    INNER JOIN (SELECT DISTINCT CodPes_hqi, CodPesSuper_hqi FROM HierarquiaIntegrante WITH(NOLOCK)) HI ON V.Vendedor_Ven = HI.CodPes_hqi
    INNER JOIN Pessoas P_Super WITH(NOLOCK) ON HI.CodPesSuper_hqi = P_Super.cod_pes
    WHERE P_Super.nome_pes IS NOT NULL
    ORDER BY P_Super.nome_pes
    """
    try:
        results = execute_query(query)
        return results
    except Exception as e:
        print(f"Erro ao buscar estruturas: {e}")
        return []

@router.get("/corretores/stats")
async def get_corretores_stats(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    corretor: str = Query("", description="Nome do corretor para filtrar (vazio = todos)"),
    estrutura: Optional[int] = Query(None, description="Código da estrutura/equipe (CodPesSuper_hqi)"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)")
):
    """Retorna estatísticas agregadas por corretor com dados completos de boletos e sinais"""
    
    # Filtro de corretor
    corretor_filter = f"AND UPPER(Pessoas.nome_pes) = UPPER('{corretor}')" if corretor else ""
    
    # Filtro de estrutura/equipe
    estrutura_filter = f"AND HI.CodPesSuper_hqi = {estrutura}" if estrutura else ""
    # Usar subquery com DISTINCT para evitar duplicação se houver múltiplos registros de hierarquia
    hi_subquery = "(SELECT DISTINCT CodPes_hqi, CodPesSuper_hqi FROM HierarquiaIntegrante WITH(NOLOCK)) HI"
    join_estrutura = f"INNER JOIN {hi_subquery} ON Vendas.Vendedor_Ven = HI.CodPes_hqi" if estrutura else ""
    join_estrutura_v = f"INNER JOIN {hi_subquery} ON v.Vendedor_Ven = HI.CodPes_hqi" if estrutura else ""
    # Para sinais pagos usamos a tabela VendasRecebidas/Vendas que já tem Vendedor_Ven
    join_estrutura_sp = f"INNER JOIN {hi_subquery} ON COALESCE(Vendas.Vendedor_Ven, VendasRecebidas.Vendedor_VRec) = HI.CodPes_hqi" if estrutura else ""
    
    # Filtro de data - usar Data_Ven (data da venda) conforme SQL correto
    # Usar formato YYYYMMDD que é universalmente aceito pelo SQL Server
    date_filter = ""
    if data_inicio and data_fim:
        # Converter de YYYY-MM-DD para YYYYMMDD (formato ISO)
        data_inicio_sql = data_inicio.replace('-', '')
        data_fim_sql = data_fim.replace('-', '')
        date_filter = f"AND (Data_Ven BETWEEN CONVERT(datetime, '{data_inicio_sql}', 112) AND CONVERT(datetime, '{data_fim_sql}', 112))"
    elif data_inicio:
        data_inicio_sql = data_inicio.replace('-', '')
        date_filter = f"AND Data_Ven >= CONVERT(datetime, '{data_inicio_sql}', 112)"
    elif data_fim:
        data_fim_sql = data_fim.replace('-', '')
        date_filter = f"AND Data_Ven BETWEEN CONVERT(datetime, '19000101', 112) AND CONVERT(datetime, '{data_fim_sql}', 112)"
    
    # Parâmetro para fn_ListEmpObr no formato 'empresa|obra'
    emp_obra_param = f"{empresa}|{obra}"
    
    # Query principal usando UNION entre Vendas e VendasRecebidas (igual ao SQL do Power BI)
    # Usando fn_ListEmpObr para filtrar empresa/obra conforme o SQL original
    stats_query = f"""
    SELECT 
        ISNULL(Pessoas.nome_pes, 'Não informado') AS corretor,
        COUNT(*) AS totalVendas,
        ISNULL(SUM(VendaLiquida), 0) AS valorTotal,
        Vendedor_Ven AS vendedorCod
    FROM (
        SELECT Status_Ven, Data_Ven, Num_Ven, Vendedor_Ven, Cliente_Ven, 
               ValorTot_Ven, Desconto_Ven, Acrescimo_Ven,
               Empresa_Ven, Obra_Ven, 
               (ValorTot_Ven - Desconto_Ven + Acrescimo_Ven) AS VendaLiquida
        FROM Vendas WITH(NOLOCK)
        WHERE Status_Ven IN (0, 1, 3)  -- Normal, Cancelada, Quitada
            {date_filter}
        UNION
        SELECT Status_VRec, Data_VRec, Num_VRec, Vendedor_VRec, Cliente_VRec,
               ValorTot_VRec, Desconto_VRec, Acrescimo_VRec,
               Empresa_VRec, Obra_VRec,
               (ValorTot_VRec - Desconto_VRec + Acrescimo_VRec) AS VendaLiquida
        FROM VendasRecebidas WITH(NOLOCK)
        WHERE Status_VRec IN (0, 1, 3)  -- Normal, Cancelada, Quitada
            {date_filter.replace('Data_Ven', 'Data_VRec')}
    ) AS Vendas
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Vendedor_Ven = Pessoas.cod_pes
    INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON Vendas.Empresa_Ven = Empresa AND Vendas.Obra_Ven = Obra
    {join_estrutura}
    WHERE Status_Ven = 0  -- Apenas vendas ativas para o ranking
    {corretor_filter}
    {estrutura_filter}
    GROUP BY Pessoas.nome_pes, Vendedor_Ven
    ORDER BY COUNT(*) DESC
    """
    
    # Query para boletos por corretor
    boletos_query = f"""
    SELECT 
        v.Vendedor_Ven,
        COUNT(DISTINCT rea.NumVendPrc_Rea) AS comBoleto
    FROM RecebAutoConfirmado rea WITH(NOLOCK)
    INNER JOIN BoletoConfirmado bol WITH(NOLOCK) 
        ON rea.SeuNum_Rea = bol.SeuNum_Bol AND rea.Banco_Rea = bol.Banco_Bol
    INNER JOIN (
        SELECT Num_Ven, Vendedor_Ven, Data_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK)
        WHERE Status_Ven = 0 {date_filter}
        UNION
        SELECT Num_VRec, Vendedor_VRec, Data_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK)
        WHERE Status_VRec = 0 {date_filter.replace('Data_Ven', 'Data_VRec')}
    ) v ON rea.NumVendPrc_Rea = v.Num_Ven AND rea.Empresa_rea = v.Empresa_Ven AND rea.ObraPrc_Rea = v.Obra_Ven
    INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
    {join_estrutura_v}
    WHERE 1=1 {estrutura_filter}
    GROUP BY v.Vendedor_Ven
    """
    
    # Query para sinais abertos por corretor
    sinais_abertos_query = f"""
    SELECT 
        v.Vendedor_Ven,
        COUNT(*) AS sinaisAbertos,
        ISNULL(SUM(cr.Valor_Prc), 0) AS valorSinaisAberto,
        SUM(CASE WHEN cr.Data_Prc < CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) AS sinaisVencidos,
        ISNULL(SUM(CASE WHEN cr.Data_Prc < CAST(GETDATE() AS DATE) THEN cr.Valor_Prc ELSE 0 END), 0) AS valorSinaisVencidos
    FROM ContasReceber cr WITH(NOLOCK)
    INNER JOIN (
        SELECT Num_Ven, Vendedor_Ven, Data_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK)
        WHERE Status_Ven = 0 {date_filter}
        UNION
        SELECT Num_VRec, Vendedor_VRec, Data_VRec, Empresa_VRec, Obra_VRec FROM VendasRecebidas WITH(NOLOCK)
        WHERE Status_VRec = 0 {date_filter.replace('Data_Ven', 'Data_VRec')}
    ) v ON cr.NumVend_prc = v.Num_Ven AND cr.Empresa_prc = v.Empresa_Ven AND cr.Obra_Prc = v.Obra_Ven
    INNER JOIN fn_ListEmpObr('{emp_obra_param}', ',') ON v.Empresa_Ven = Empresa AND v.Obra_Ven = Obra
    {join_estrutura_v}
    WHERE cr.Tipo_Prc = 'S' AND cr.Status_Prc = 0 {estrutura_filter}
    GROUP BY v.Vendedor_Ven
    """
    
    # Contas bancárias por empresa (mesmo padrão da tela de Recebimentos)
    CONTAS_POR_EMPRESA = {
        28: ("'13005587-5'", "'529-5'", "'529-0'", "'27083-6'"),
        29: ("'13005588-2'", "'549-0'", "'31714-8'"),
    }
    contas = CONTAS_POR_EMPRESA.get(empresa, CONTAS_POR_EMPRESA[28])
    contas_filter = f"({','.join(contas)})"
    
    # Query para sinais pagos por corretor - usando metodologia de Depósitos Conciliados
    sinais_pagos_query = f"""
    SELECT
        COALESCE(Vendas.Vendedor_Ven, VendasRecebidas.Vendedor_VRec) AS Vendedor_Ven,
        COUNT(*) AS sinaisPagos,
        ISNULL(SUM(RecebePgtoDiv.PercentValor_Rpd * (CAST((ItensRecebidas.Qtde_Itr * ItensRecebidas.PrecoProc_Itr - ItensRecebidas.ValComissaoDir_Itr) AS NUMERIC(18, 6)) / NULLIF(VendasRecebidas.ValorTot_VRec, 0))), 0) AS valorSinaisPagos
    FROM Extrato WITH(NOLOCK)
    INNER JOIN Depositos WITH(NOLOCK)
        ON Extrato.Empresa_Doc = Depositos.Empresa_Dep
        AND Extrato.Banco_Doc = Depositos.Banco_Dep
        AND Extrato.Conta_Doc = Depositos.Conta_Dep
        AND Extrato.Numero_Doc = Depositos.Numero_Dep
    INNER JOIN RecebePgto WITH(NOLOCK)
        ON Depositos.Empresa_Dep = RecebePgto.Empresa_Rpg
        AND Depositos.Numero_Dep = RecebePgto.NumDep_Rpg
        AND Depositos.Banco_Dep = RecebePgto.BancoDep_Rpg
        AND Depositos.Conta_Dep = RecebePgto.ContaDep_Rpg
        AND RecebePgto.Status_Rpg <> 2
    INNER JOIN RecebePgtoDiv WITH(NOLOCK)
        ON RecebePgto.Empresa_Rpg = RecebePgtoDiv.Empresa_Rpd
        AND RecebePgto.NumReceb_Rpg = RecebePgtoDiv.NumReceb_Rpd
        AND RecebePgto.Tipo_Rpg = RecebePgtoDiv.TipoRpg_Rpd
        AND RecebePgto.NumCont_Rpg = RecebePgtoDiv.NumCont_Rpd
    INNER JOIN Recebidas WITH(NOLOCK)
        ON RecebePgtoDiv.Empresa_Rpd = Recebidas.Empresa_Rec
        AND RecebePgtoDiv.Obra_Rpd = Recebidas.Obra_Rec
        AND RecebePgtoDiv.NumVend_Rpd = Recebidas.NumVend_Rec
        AND RecebePgtoDiv.NumParc_Rpd = Recebidas.NumParc_Rec
        AND RecebePgtoDiv.ParcType_Rpd = Recebidas.ParcType_Rec
        AND RecebePgtoDiv.Tipo_Rpd = Recebidas.Tipo_Rec
        AND RecebePgtoDiv.NumParcGer_Rpd = Recebidas.NumParcGer_Rec
    INNER JOIN VendasRecebidas WITH(NOLOCK)
        ON Recebidas.Empresa_Rec = VendasRecebidas.Empresa_VRec
        AND Recebidas.Obra_Rec = VendasRecebidas.Obra_VRec
        AND Recebidas.NumVend_Rec = VendasRecebidas.Num_VRec
    INNER JOIN ItensRecebidas WITH(NOLOCK)
        ON VendasRecebidas.Empresa_VRec = ItensRecebidas.Empresa_Itr
        AND VendasRecebidas.Obra_VRec = ItensRecebidas.Obra_Itr
        AND VendasRecebidas.Num_VRec = ItensRecebidas.NumVend_Itr
    LEFT JOIN Vendas WITH(NOLOCK)
        ON Recebidas.Empresa_Rec = Vendas.Empresa_Ven
        AND Recebidas.Obra_Rec = Vendas.Obra_Ven
        AND Recebidas.NumVend_Rec = Vendas.Num_Ven
    {join_estrutura_sp}
    WHERE Extrato.Tipo_Doc = 1
        AND Extrato.Empresa_doc = {empresa}
        AND Extrato.Conta_doc IN {contas_filter}
        AND Recebidas.Tipo_Rec = 'S'
        AND VendasRecebidas.Obra_VRec = '{obra}'
        {estrutura_filter}
    GROUP BY COALESCE(Vendas.Vendedor_Ven, VendasRecebidas.Vendedor_VRec)
    """
    
    try:
        stats = execute_query(stats_query)
        boletos = execute_query(boletos_query)
        sinais_abertos = execute_query(sinais_abertos_query)
        sinais_pagos = execute_query(sinais_pagos_query)
        
        # Criar mapas para lookup por vendedor
        boletos_map = {b['Vendedor_Ven']: b['comBoleto'] for b in boletos}
        sinais_abertos_map = {s['Vendedor_Ven']: {
            'sinaisAbertos': s['sinaisAbertos'],
            'valorSinaisAberto': float(s['valorSinaisAberto'] or 0),
            'sinaisVencidos': s['sinaisVencidos'],
            'valorSinaisVencidos': float(s['valorSinaisVencidos'] or 0)
        } for s in sinais_abertos}
        sinais_pagos_map = {s['Vendedor_Ven']: {
            'sinaisPagos': s['sinaisPagos'],
            'valorSinaisPagos': float(s['valorSinaisPagos'] or 0)
        } for s in sinais_pagos}
        
        # Combinar resultados
        corretores_completos = []
        for s in stats:
            vendedor_cod = s.get('vendedorCod')
            corretor_data = {
                'corretor': s.get('corretor'),
                'totalVendas': int(s.get('totalVendas', 0) or 0),
                'valorTotal': float(s.get('valorTotal', 0) or 0),
                'comBoleto': boletos_map.get(vendedor_cod, 0),
                'sinaisAbertos': sinais_abertos_map.get(vendedor_cod, {}).get('sinaisAbertos', 0),
                'valorSinaisAberto': sinais_abertos_map.get(vendedor_cod, {}).get('valorSinaisAberto', 0),
                'sinaisVencidos': sinais_abertos_map.get(vendedor_cod, {}).get('sinaisVencidos', 0),
                'valorSinaisVencidos': sinais_abertos_map.get(vendedor_cod, {}).get('valorSinaisVencidos', 0),
                'sinaisPagos': sinais_pagos_map.get(vendedor_cod, {}).get('sinaisPagos', 0),
                'valorSinaisPagos': sinais_pagos_map.get(vendedor_cod, {}).get('valorSinaisPagos', 0)
            }
            corretores_completos.append(corretor_data)
        
        # Calcular totais
        totais = {
            "totalVendas": sum(c['totalVendas'] for c in corretores_completos),
            "valorTotal": sum(c['valorTotal'] for c in corretores_completos),
            "totalCorretores": len(corretores_completos),
            "sinaisPagos": sum(c['sinaisPagos'] for c in corretores_completos),
            "valorSinaisPagos": sum(c['valorSinaisPagos'] for c in corretores_completos),
            "sinaisAbertos": sum(c['sinaisAbertos'] for c in corretores_completos),
            "valorSinaisAbertos": sum(c['valorSinaisAberto'] for c in corretores_completos),
            "sinaisVencidos": sum(c['sinaisVencidos'] for c in corretores_completos),
            "valorSinaisVencidos": sum(c['valorSinaisVencidos'] for c in corretores_completos)
        }
        
        return {
            "corretores": corretores_completos,
            "totais": totais
        }
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")

@router.get("/resumo")
async def get_resumo(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    estrutura: Optional[int] = Query(None, description="Código da estrutura/equipe (CodPesSuper_hqi)"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)")
):
    """Retorna resumo consolidado das vendas"""
    
    # Filtro de data
    date_filter = ""
    if data_inicio and data_fim:
        data_inicio_sql = data_inicio.replace('-', '')
        data_fim_sql = data_fim.replace('-', '')
        date_filter = f"AND (Data_Ven BETWEEN CONVERT(datetime, '{data_inicio_sql}', 112) AND CONVERT(datetime, '{data_fim_sql}', 112))"
    elif data_inicio:
        data_inicio_sql = data_inicio.replace('-', '')
        date_filter = f"AND Data_Ven >= CONVERT(datetime, '{data_inicio_sql}', 112)"
    elif data_fim:
        data_fim_sql = data_fim.replace('-', '')
        date_filter = f"AND Data_Ven <= CONVERT(datetime, '{data_fim_sql}', 112)"

    # Filtro de estrutura/equipe
    estrutura_filter = f"AND HI.CodPesSuper_hqi = {estrutura}" if estrutura else ""
    hi_subquery = "(SELECT DISTINCT CodPes_hqi, CodPesSuper_hqi FROM HierarquiaIntegrante WITH(NOLOCK)) HI"
    join_estrutura = f"INNER JOIN {hi_subquery} ON Vendas.Vendedor_Ven = HI.CodPes_hqi" if estrutura else ""
    join_estrutura_b = f"INNER JOIN {hi_subquery} ON Vendas.Vendedor_Ven = HI.CodPes_hqi" if estrutura else ""
    join_estrutura_s = f"INNER JOIN {hi_subquery} ON Vendas.Vendedor_Ven = HI.CodPes_hqi" if estrutura else ""

    params = [empresa, obra]
    
    # Buscar vendas
    vendas_query = f"""
    SELECT 
        Vendas.Num_Ven AS venda,
        Pessoas.nome_pes AS cliente,
        Vendas.Obra_Ven + ' - Q' + ISNULL(u.C1_unid, '') + ' L' + ISNULL(u.C2_unid, '') AS identificador,
        PessoasVendedor.nome_pes AS corretor,
        Vendas.Vendedor_Ven AS vendedorCod,
        FORMAT(Vendas.Data_Ven, 'dd/MM/yyyy') AS dataVenda,
        FORMAT(Vendas.DataCad_Ven, 'dd/MM/yyyy') AS dataCadastro,
        (Vendas.ValorTot_Ven + Vendas.Acrescimo_Ven - Vendas.Desconto_Ven) AS valorTotal
    FROM (
        SELECT Num_Ven, Cliente_Ven, Obra_Ven, Vendedor_Ven, Data_Ven, DataCad_Ven, ValorTot_Ven, Acrescimo_Ven, Desconto_Ven, Empresa_Ven, Status_Ven
        FROM Vendas WITH(NOLOCK)
        WHERE Status_Ven = 0 {date_filter}
        UNION
        SELECT Num_VRec as Num_Ven, Cliente_VRec as Cliente_Ven, Obra_VRec as Obra_Ven, Vendedor_VRec as Vendedor_Ven, Data_VRec as Data_Ven, DataCad_VRec as DataCad_Ven, ValorTot_VRec as ValorTot_Ven, Acrescimo_VRec as Acrescimo_Ven, Desconto_VRec as Desconto_Ven, Empresa_VRec as Empresa_Ven, Status_VRec as Status_Ven
        FROM VendasRecebidas WITH(NOLOCK)
        WHERE Status_VRec = 0 {date_filter.replace('Data_Ven', 'Data_VRec')}
    ) AS Vendas
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.cod_pes
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.cod_pes
    {join_estrutura}
    LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_itv 
        AND Vendas.Obra_Ven = ItensVenda.Obra_Itv 
        AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer u WITH(NOLOCK) ON ItensVenda.Empresa_itv = u.Empresa_unid 
        AND ItensVenda.Produto_Itv = u.Prod_unid 
        AND ItensVenda.CodPerson_Itv = u.NumPer_unid
    WHERE Vendas.Empresa_Ven = ? AND Vendas.Obra_Ven = ? {estrutura_filter}
    ORDER BY Vendas.Num_Ven
    """
    
    boletos_query = f"""
    SELECT 
        RecebAutoConfirmado.NumVendPrc_Rea AS venda,
        RecebAutoConfirmado.UsrCad_Rea AS usuarioGerou,
        RecebAutoConfirmado.DataGera_Rea AS dataGerou,
        BoletoConfirmado.SeuNum_Bol AS seuNumBoleto
    FROM RecebAutoConfirmado WITH(NOLOCK)
    INNER JOIN BoletoConfirmado WITH(NOLOCK) 
        ON RecebAutoConfirmado.SeuNum_Rea = BoletoConfirmado.SeuNum_Bol
        AND RecebAutoConfirmado.Banco_Rea = BoletoConfirmado.Banco_Bol
        AND RecebAutoConfirmado.NumBol_Rea = BoletoConfirmado.Num_Bol
    INNER JOIN (
        SELECT Num_Ven, Vendedor_Ven, Data_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK)
        WHERE Status_Ven = 0 {date_filter}
        UNION
        SELECT Num_VRec as Num_Ven, Vendedor_VRec as Vendedor_Ven, Data_VRec as Data_Ven, Empresa_VRec as Empresa_Ven, Obra_VRec as Obra_Ven FROM VendasRecebidas WITH(NOLOCK)
        WHERE Status_VRec = 0 {date_filter.replace('Data_Ven', 'Data_VRec')}
    ) AS Vendas ON RecebAutoConfirmado.NumVendPrc_Rea = Vendas.Num_Ven AND RecebAutoConfirmado.Empresa_rea = Vendas.Empresa_Ven AND RecebAutoConfirmado.ObraPrc_Rea = Vendas.Obra_Ven
    {join_estrutura_b}
    WHERE RecebAutoConfirmado.Empresa_rea = ? {estrutura_filter}
    """
    
    # Buscar sinais em aberto com data do primeiro vencimento e valor
    sinais_aberto_query = f"""
    SELECT 
        r.NumVend_prc AS venda,
        COUNT(*) AS qtdSinaisAberto,
        SUM(r.Valor_Prc) AS valorSinaisAberto,
        MIN(r.Data_Prc) AS primeiroVencimento,
        SUM(CASE WHEN r.Data_Prc < CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) AS sinaisVencidos,
        ISNULL(SUM(CASE WHEN r.Data_Prc < CAST(GETDATE() AS DATE) THEN r.Valor_Prc ELSE 0 END), 0) AS valorSinaisVencidos
    FROM ContasReceber r WITH(NOLOCK)
    INNER JOIN (
        SELECT Num_Ven, Vendedor_Ven, Data_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK)
        WHERE Status_Ven = 0 {date_filter}
        UNION
        SELECT Num_VRec as Num_Ven, Vendedor_VRec as Vendedor_Ven, Data_VRec as Data_Ven, Empresa_VRec as Empresa_Ven, Obra_VRec as Obra_Ven FROM VendasRecebidas WITH(NOLOCK)
        WHERE Status_VRec = 0 {date_filter.replace('Data_Ven', 'Data_VRec')}
    ) AS Vendas ON r.NumVend_prc = Vendas.Num_Ven AND r.Empresa_prc = Vendas.Empresa_Ven AND r.Obra_Prc = Vendas.Obra_Ven
    {join_estrutura_s}
    WHERE r.Empresa_prc = {empresa}
      AND r.Obra_Prc = '{obra}'
      AND r.Tipo_Prc = 'S'
      AND r.Status_Prc = 0
      {estrutura_filter}
    GROUP BY r.NumVend_prc
    """
    
    # Buscar sinais pagos por venda (da tabela Recebidas) - com valor
    sinais_pagos_query = f"""
    SELECT 
        r.NumVend_Rec AS venda,
        COUNT(*) AS sinaisPagos,
        SUM(r.Valor_Rec + r.ValorConf_Rec) AS valorSinaisPagos
    FROM Recebidas r WITH(NOLOCK)
    INNER JOIN (
        SELECT Num_Ven, Vendedor_Ven, Data_Ven, Empresa_Ven, Obra_Ven FROM Vendas WITH(NOLOCK)
        WHERE Status_Ven = 0 {date_filter}
        UNION
        SELECT Num_VRec as Num_Ven, Vendedor_VRec as Vendedor_Ven, Data_VRec as Data_Ven, Empresa_VRec as Empresa_Ven, Obra_VRec as Obra_Ven FROM VendasRecebidas WITH(NOLOCK)
        WHERE Status_VRec = 0 {date_filter.replace('Data_Ven', 'Data_VRec')}
    ) AS Vendas ON r.NumVend_Rec = Vendas.Num_Ven AND r.Empresa_Rec = Vendas.Empresa_Ven AND r.Obra_Rec = Vendas.Obra_Ven
    {join_estrutura}
    WHERE r.Empresa_Rec = {empresa}
      AND r.Obra_Rec = '{obra}'
      AND r.Tipo_Rec = 'S'
      AND r.Status_Rec = 1
      {estrutura_filter}
    GROUP BY r.NumVend_Rec
    """
    
    try:
        vendas = execute_query(vendas_query, (empresa, obra))
        boletos_result = execute_query(boletos_query, (empresa,))
        sinais_aberto_result = execute_query(sinais_aberto_query)
        sinais_pagos_result = execute_query(sinais_pagos_query)
        
        # Map boletos with user and date info (get most recent per venda)
        boletos_map = {}
        for b in boletos_result:
            venda = b['venda']
            data_gerou = b['dataGerou']
            if venda not in boletos_map or (data_gerou and (boletos_map[venda]['_raw_data'] is None or data_gerou > boletos_map[venda]['_raw_data'])):
                boletos_map[venda] = {
                    'usuarioGerou': b['usuarioGerou'],
                    'dataGerou': data_gerou.strftime('%d/%m/%Y %H:%M') if data_gerou else None,
                    '_raw_data': data_gerou,
                    'seuNumBoleto': b['seuNumBoleto']
                }
        
        # Map sinais em aberto - agora inclui valor e vencidos
        sinais_aberto_map = {s['venda']: {
            'qtd': s['qtdSinaisAberto'],
            'valor': s['valorSinaisAberto'] or 0,
            'vencidos': s['sinaisVencidos'] or 0,
            'valorVencidos': float(s['valorSinaisVencidos'] or 0),
            'vencimento': s['primeiroVencimento'].strftime('%d/%m/%Y') if s['primeiroVencimento'] else None,
            'vencimentoISO': s['primeiroVencimento'].strftime('%Y-%m-%d') if s['primeiroVencimento'] else None
        } for s in sinais_aberto_result}
        
        # Map sinais pagos - agora inclui valor
        sinais_pagos_map = {s['venda']: {
            'qtd': s['sinaisPagos'],
            'valor': s['valorSinaisPagos'] or 0
        } for s in sinais_pagos_result}
        
        # Build resumo
        resumo = []
        for v in vendas:
            sinal_aberto = sinais_aberto_map.get(v['venda'], {'qtd': 0, 'valor': 0, 'vencidos': 0, 'valorVencidos': 0, 'vencimento': None, 'vencimentoISO': None})
            sinais_pagos_info = sinais_pagos_map.get(v['venda'], {'qtd': 0, 'valor': 0})
            sinais_pagos = sinais_pagos_info['qtd']
            valor_sinais_pagos = sinais_pagos_info['valor']
            sinais_total = sinal_aberto['qtd'] + sinais_pagos
            boleto_info = boletos_map.get(v['venda'], {'usuarioGerou': None, 'dataGerou': None, 'seuNumBoleto': None})
            resumo.append({
                **v,
                "boletoGerado": v['venda'] in boletos_map,
                "boletoUsuario": boleto_info['usuarioGerou'],
                "boletoDataHora": boleto_info['dataGerou'],
                "sinaisAberto": sinal_aberto['qtd'],
                "valorSinaisAberto": sinal_aberto['valor'],
                "sinaisVencidos": sinal_aberto['vencidos'],
                "valorSinaisVencidos": sinal_aberto['valorVencidos'],
                "sinaisPagos": sinais_pagos,
                "valorSinaisPagos": valor_sinais_pagos,
                "sinaisTotal": sinais_total,
                "primeiroVencimento": sinal_aberto['vencimento'],
                "primeiroVencimentoISO": sinal_aberto['vencimentoISO']
            })
        
        # Calculate metrics
        total_vendas = len(resumo)
        vendas_com_boleto_count = sum(1 for r in resumo if r['boletoGerado'])
        vendas_sem_boleto = total_vendas - vendas_com_boleto_count
        total_sinais = sum(r['sinaisAberto'] for r in resumo)
        valor_total = sum(r['valorTotal'] or 0 for r in resumo)
        
        # Buscar nome da obra
        obra_nome = f"{empresa} - {obra}"
        try:
            obra_query = f"""
            SELECT RTRIM(LTRIM(Descr_Obr)) as nome
            FROM Obras WITH(NOLOCK)
            WHERE Empresa_Obr = {empresa} AND RTRIM(LTRIM(Cod_Obr)) = '{obra}'
            """
            obra_result = execute_query(obra_query)
            if obra_result and obra_result[0].get('nome'):
                obra_nome = f"{empresa} - {obra} - {obra_result[0]['nome']}"
        except Exception as e:
            print(f"Erro ao buscar nome da obra: {e}")
        
        return {
            "data": resumo,
            "obraNome": obra_nome,
            "metrics": {
                "totalVendas": total_vendas,
                "vendasComBoleto": vendas_com_boleto_count,
                "vendasSemBoleto": vendas_sem_boleto,
                "totalSinaisAberto": total_sinais,
                "valorTotal": valor_total
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard-resumo")
async def get_dashboard_resumo(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    data_inicio: Optional[str] = Query(None, description="Data início (dd/mm/yyyy)"),
    data_fim: Optional[str] = Query(None, description="Data fim (dd/mm/yyyy)")
):
    """Retorna resumo completo para Dashboard Executivo com vendas diárias e cancelamentos"""
    
    # Default: mês atual em formato ISO
    hoje = datetime.now()
    if not data_inicio:
        primeiro_dia = hoje.replace(day=1)
        data_inicio_sql = primeiro_dia.strftime('%Y-%m-%d')
        data_inicio = primeiro_dia.strftime('%d/%m/%Y')
    else:
        # Converter de dd/mm/yyyy para yyyy-mm-dd
        parts = data_inicio.split('/')
        data_inicio_sql = f"{parts[2]}-{parts[1]}-{parts[0]}" if len(parts) == 3 else data_inicio
    
    if not data_fim:
        data_fim_sql = hoje.strftime('%Y-%m-%d')
        data_fim = hoje.strftime('%d/%m/%Y')
    else:
        parts = data_fim.split('/')
        data_fim_sql = f"{parts[2]}-{parts[1]}-{parts[0]}" if len(parts) == 3 else data_fim
    
    # Query 1: Resumo por Status de Unidades (contagens)
    status_query = f"""
    SELECT 
        SUM(CASE WHEN Vendido_unid = 1 THEN 1 ELSE 0 END) as qtd_vendido,
        SUM(CASE WHEN Vendido_unid = 3 THEN 1 ELSE 0 END) as qtd_quitado,
        SUM(CASE WHEN Vendido_unid = 2 THEN 1 ELSE 0 END) as qtd_reservado,
        SUM(CASE WHEN Vendido_unid = 0 THEN 1 ELSE 0 END) as qtd_disponivel,
        SUM(CASE WHEN Vendido_unid = 6 THEN 1 ELSE 0 END) as qtd_suspenso,
        SUM(CASE WHEN Vendido_unid IN (7, 8) THEN 1 ELSE 0 END) as qtd_fora_venda,
        SUM(CASE WHEN Vendido_unid = 9 THEN 1 ELSE 0 END) as qtd_permuta,
        COUNT(*) as total_unidades
    FROM UnidadePer WITH(NOLOCK)
    WHERE Empresa_unid = {empresa} AND Obra_unid = '{obra}'
    """
    
    # Query para valores por status (usando Vendas/VendasRecebidas)
    valores_status_query = f"""
    SELECT 
        SUM(CASE WHEN Status_Ven = 0 THEN ValorLiquido ELSE 0 END) as valor_vendido,
        SUM(CASE WHEN Status_Ven = 3 THEN ValorLiquido ELSE 0 END) as valor_quitado,
        SUM(CASE WHEN Status_Ven = 2 THEN ValorLiquido ELSE 0 END) as valor_reservado,
        SUM(ValorLiquido) as valor_total
    FROM (
        SELECT Status_Ven, (ValorTot_Ven + Acrescimo_Ven - Desconto_Ven) as ValorLiquido
        FROM Vendas WITH(NOLOCK)
        WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}'
        UNION ALL
        SELECT Status_VRec, (ValorTot_VRec + Acrescimo_VRec - Desconto_VRec) as ValorLiquido
        FROM VendasRecebidas WITH(NOLOCK)
        WHERE Empresa_VRec = {empresa} AND Obra_VRec = '{obra}'
    ) AS VendasUnion
    """
    
    # Query 2a: Vendas diárias (por DataCad, Status = 0)
    vendas_query = f"""
    SELECT 
        CAST(Data_Cad AS DATE) as DataRef,
        FORMAT(CAST(Data_Cad AS DATE), 'dd/MM/yyyy') as data,
        COUNT(*) as qtd_vendas,
        SUM(ValorLiquido) as valor_vendas,
        AVG(ValorLiquido) as valor_medio
    FROM (
        SELECT DataCad_Ven as Data_Cad, (ValorTot_Ven + Acrescimo_Ven - Desconto_Ven) as ValorLiquido
        FROM Vendas WITH(NOLOCK)
        WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}'
            AND CAST(DataCad_Ven AS DATE) >= CAST('{data_inicio_sql}' AS DATE)
            AND CAST(DataCad_Ven AS DATE) <= CAST('{data_fim_sql}' AS DATE)
            AND Status_Ven = 0
        UNION ALL
        SELECT DataCad_VRec, (ValorTot_VRec + Acrescimo_VRec - Desconto_VRec)
        FROM VendasRecebidas WITH(NOLOCK)
        WHERE Empresa_VRec = {empresa} AND Obra_VRec = '{obra}'
            AND CAST(DataCad_VRec AS DATE) >= CAST('{data_inicio_sql}' AS DATE)
            AND CAST(DataCad_VRec AS DATE) <= CAST('{data_fim_sql}' AS DATE)
            AND Status_VRec = 0
    ) AS V
    GROUP BY CAST(Data_Cad AS DATE)
    ORDER BY DataRef
    """
    
    # Query 2b: Cancelamentos diários (por DataCancel, Status = 1)
    cancelamentos_query = f"""
    SELECT 
        CAST(DataCancel AS DATE) as DataRef,
        FORMAT(CAST(DataCancel AS DATE), 'dd/MM/yyyy') as data,
        COUNT(*) as qtd_cancelamentos
    FROM (
        SELECT DataCancel_Ven as DataCancel
        FROM Vendas WITH(NOLOCK)
        WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}'
            AND DataCancel_Ven IS NOT NULL
            AND CAST(DataCancel_Ven AS DATE) >= CAST('{data_inicio_sql}' AS DATE)
            AND CAST(DataCancel_Ven AS DATE) <= CAST('{data_fim_sql}' AS DATE)
            AND Status_Ven = 1
        UNION ALL
        SELECT DataCancel_VRec
        FROM VendasRecebidas WITH(NOLOCK)
        WHERE Empresa_VRec = {empresa} AND Obra_VRec = '{obra}'
            AND DataCancel_VRec IS NOT NULL
            AND CAST(DataCancel_VRec AS DATE) >= CAST('{data_inicio_sql}' AS DATE)
            AND CAST(DataCancel_VRec AS DATE) <= CAST('{data_fim_sql}' AS DATE)
            AND Status_VRec = 1
    ) AS C
    GROUP BY CAST(DataCancel AS DATE)
    ORDER BY DataRef
    """
    
    # Query para totais - vendas
    total_vendas_query = f"""
    SELECT COUNT(*) as total
    FROM (
        SELECT 1 as x FROM Vendas WITH(NOLOCK) 
        WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}'
            AND CAST(DataCad_Ven AS DATE) >= CAST('{data_inicio_sql}' AS DATE)
            AND CAST(DataCad_Ven AS DATE) <= CAST('{data_fim_sql}' AS DATE)
            AND Status_Ven = 0
        UNION ALL
        SELECT 1 FROM VendasRecebidas WITH(NOLOCK) 
        WHERE Empresa_VRec = {empresa} AND Obra_VRec = '{obra}'
            AND CAST(DataCad_VRec AS DATE) >= CAST('{data_inicio_sql}' AS DATE)
            AND CAST(DataCad_VRec AS DATE) <= CAST('{data_fim_sql}' AS DATE)
            AND Status_VRec = 0
    ) t
    """
    
    # Query para totais - valor
    total_valor_query = f"""
    SELECT SUM(ValorLiquido) as total, AVG(ValorLiquido) as media
    FROM (
        SELECT (ValorTot_Ven + Acrescimo_Ven - Desconto_Ven) as ValorLiquido
        FROM Vendas WITH(NOLOCK) 
        WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}'
            AND CAST(DataCad_Ven AS DATE) >= CAST('{data_inicio_sql}' AS DATE)
            AND CAST(DataCad_Ven AS DATE) <= CAST('{data_fim_sql}' AS DATE)
            AND Status_Ven = 0
        UNION ALL
        SELECT (ValorTot_VRec + Acrescimo_VRec - Desconto_VRec)
        FROM VendasRecebidas WITH(NOLOCK) 
        WHERE Empresa_VRec = {empresa} AND Obra_VRec = '{obra}'
            AND CAST(DataCad_VRec AS DATE) >= CAST('{data_inicio_sql}' AS DATE)
            AND CAST(DataCad_VRec AS DATE) <= CAST('{data_fim_sql}' AS DATE)
            AND Status_VRec = 0
    ) t
    """
    
    # Query para totais - cancelamentos
    total_cancel_query = f"""
    SELECT COUNT(*) as total
    FROM (
        SELECT 1 as x FROM Vendas WITH(NOLOCK) 
        WHERE Empresa_Ven = {empresa} AND Obra_Ven = '{obra}'
            AND DataCancel_Ven IS NOT NULL
            AND CAST(DataCancel_Ven AS DATE) >= CAST('{data_inicio_sql}' AS DATE)
            AND CAST(DataCancel_Ven AS DATE) <= CAST('{data_fim_sql}' AS DATE)
            AND Status_Ven = 1
        UNION ALL
        SELECT 1 FROM VendasRecebidas WITH(NOLOCK) 
        WHERE Empresa_VRec = {empresa} AND Obra_VRec = '{obra}'
            AND DataCancel_VRec IS NOT NULL
            AND CAST(DataCancel_VRec AS DATE) >= CAST('{data_inicio_sql}' AS DATE)
            AND CAST(DataCancel_VRec AS DATE) <= CAST('{data_fim_sql}' AS DATE)
            AND Status_VRec = 1
    ) t
    """
    
    try:
        status_result = execute_query(status_query)
        valores_result = execute_query(valores_status_query)
        vendas_result = execute_query(vendas_query)
        cancelamentos_result = execute_query(cancelamentos_query)
        total_vendas_result = execute_query(total_vendas_query)
        total_valor_result = execute_query(total_valor_query)
        total_cancel_result = execute_query(total_cancel_query)
        
        # Merge vendas e cancelamentos por data usando Python
        diario_map = {}
        for v in vendas_result:
            data = v.get('data')
            diario_map[data] = {
                'data': data,
                'qtdVendas': int(v.get('qtd_vendas', 0) or 0),
                'valorVendas': float(v.get('valor_vendas', 0) or 0),
                'valorMedio': float(v.get('valor_medio', 0) or 0),
                'qtdCancelamentos': 0
            }
        
        for c in cancelamentos_result:
            data = c.get('data')
            if data in diario_map:
                diario_map[data]['qtdCancelamentos'] = int(c.get('qtd_cancelamentos', 0) or 0)
            else:
                diario_map[data] = {
                    'data': data,
                    'qtdVendas': 0,
                    'valorVendas': 0,
                    'valorMedio': 0,
                    'qtdCancelamentos': int(c.get('qtd_cancelamentos', 0) or 0)
                }
        
        # Sort by data
        sorted_dates = sorted(diario_map.keys(), key=lambda x: '/'.join(reversed(x.split('/'))))
        diario = [diario_map[d] for d in sorted_dates]
        
        # Process status summary
        status = status_result[0] if status_result else {}
        valores = valores_result[0] if valores_result else {}
        total_unidades = int(status.get('total_unidades', 0) or 0)
        
        resumo_status = [
            {
                "status": "Vendido",
                "qtde": int(status.get('qtd_vendido', 0) or 0),
                "percent": round((int(status.get('qtd_vendido', 0) or 0) / total_unidades * 100), 2) if total_unidades > 0 else 0,
                "valor": float(valores.get('valor_vendido', 0) or 0)
            },
            {
                "status": "Quitado",
                "qtde": int(status.get('qtd_quitado', 0) or 0),
                "percent": round((int(status.get('qtd_quitado', 0) or 0) / total_unidades * 100), 2) if total_unidades > 0 else 0,
                "valor": float(valores.get('valor_quitado', 0) or 0)
            },
            {
                "status": "Reservado",
                "qtde": int(status.get('qtd_reservado', 0) or 0),
                "percent": round((int(status.get('qtd_reservado', 0) or 0) / total_unidades * 100), 2) if total_unidades > 0 else 0,
                "valor": float(valores.get('valor_reservado', 0) or 0)
            },
            {
                "status": "Disponível",
                "qtde": int(status.get('qtd_disponivel', 0) or 0),
                "percent": round((int(status.get('qtd_disponivel', 0) or 0) / total_unidades * 100), 2) if total_unidades > 0 else 0,
                "valor": 0
            },
            {
                "status": "Suspenso",
                "qtde": int(status.get('qtd_suspenso', 0) or 0),
                "percent": round((int(status.get('qtd_suspenso', 0) or 0) / total_unidades * 100), 2) if total_unidades > 0 else 0,
                "valor": 0
            },
            {
                "status": "Fora de Venda",
                "qtde": int(status.get('qtd_fora_venda', 0) or 0),
                "percent": round((int(status.get('qtd_fora_venda', 0) or 0) / total_unidades * 100), 2) if total_unidades > 0 else 0,
                "valor": 0
            },
            {
                "status": "Permuta/Dação",
                "qtde": int(status.get('qtd_permuta', 0) or 0),
                "percent": round((int(status.get('qtd_permuta', 0) or 0) / total_unidades * 100), 2) if total_unidades > 0 else 0,
                "valor": 0
            }
        ]
        
        # Process totals from separate queries
        tv = total_vendas_result[0] if total_vendas_result else {}
        tvl = total_valor_result[0] if total_valor_result else {}
        tc = total_cancel_result[0] if total_cancel_result else {}
        
        return {
            "resumoStatus": resumo_status,
            "totalUnidades": total_unidades,
            "valorTotalUnidades": float(valores.get('valor_total', 0) or 0),
            "vendasDiarias": diario,
            "totaisPeriodo": {
                "totalVendas": int(tv.get('total', 0) or 0),
                "valorTotalVendas": float(tvl.get('total', 0) or 0),
                "totalCancelamentos": int(tc.get('total', 0) or 0),
                "valorMedio": float(tvl.get('media', 0) or 0)
            },
            "periodo": {
                "inicio": data_inicio,
                "fim": data_fim
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
