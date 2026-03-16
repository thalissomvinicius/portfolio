"""
Contratos Routes
Rotas para gerenciamento de contratos de venda
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from database import execute_query
from contracts_storage import (
    get_contract,
    update_contract,
    get_all_contracts_for_obra,
    get_contracts_metrics,
    STATUS_OPTIONS,
    TIPO_ASSINATURA_OPTIONS,
    PROPOSTA_STATUS_OPTIONS
)

router = APIRouter()


class ContratoUpdate(BaseModel):
    """Modelo para atualização de contrato"""
    venda: int
    status: Optional[str] = None
    tipo_assinatura: Optional[str] = None
    data_envio: Optional[str] = None
    data_assinatura: Optional[str] = None
    responsavel_envio: Optional[str] = None
    observacoes: Optional[str] = None
    proposta_status: Optional[str] = None
    proposta_data: Optional[str] = None
    pendencias: Optional[str] = None


def get_vendas_from_db(empresa: int, obra: str) -> List[Dict[str, Any]]:
    """Busca vendas do SQL Server para combinar com dados de contratos"""
    query = """
    SELECT 
        Vendas.Empresa_Ven AS empresa,
        Vendas.Obra_Ven AS obra,
        Vendas.Num_Ven AS venda,
        Vendas.Cliente_Ven AS clienteId,
        Pessoas.nome_pes AS cliente,
        Pessoas.cpf_pes AS cpf,
        Vendas.Vendedor_Ven AS vendedorId,
        PessoasVendedor.nome_pes AS corretor,
        FORMAT(Vendas.Data_Ven, 'dd/MM/yyyy') AS dataVenda,
        Vendas.Status_Ven AS statusVenda,
        ISNULL(u.C1_unid, '') AS quadra,
        ISNULL(u.C2_unid, '') AS lote,
        ISNULL(u.Identificador_unid, '') AS identificador
    FROM Vendas WITH(NOLOCK)
    INNER JOIN Pessoas WITH(NOLOCK) ON Vendas.Cliente_Ven = Pessoas.Cod_pes
    LEFT JOIN Pessoas AS PessoasVendedor WITH(NOLOCK) ON Vendas.Vendedor_Ven = PessoasVendedor.Cod_pes
    LEFT JOIN ItensVenda WITH(NOLOCK) ON Vendas.Empresa_Ven = ItensVenda.Empresa_Itv 
        AND Vendas.Obra_Ven = ItensVenda.Obra_Itv 
        AND Vendas.Num_Ven = ItensVenda.NumVend_Itv
    LEFT JOIN UnidadePer u WITH(NOLOCK) ON ItensVenda.Empresa_itv = u.Empresa_unid 
        AND ItensVenda.Produto_Itv = u.Prod_unid 
        AND ItensVenda.CodPerson_Itv = u.NumPer_unid
    WHERE Vendas.Empresa_Ven = ? 
      AND Vendas.Obra_Ven = ?
      AND Vendas.Status_Ven NOT IN (3, 8)  -- Excluir cancelados e distratos
    ORDER BY Vendas.Data_Ven DESC
    """
    
    try:
        return execute_query(query, (empresa, obra))
    except Exception as e:
        print(f"Erro ao buscar vendas: {e}")
        return []


@router.get("/contratos")
async def get_contratos(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    tipo_assinatura: Optional[str] = Query(None, description="Filtrar por tipo de assinatura"),
    corretor: Optional[str] = Query(None, description="Filtrar por corretor")
):
    """Lista todos os contratos combinando dados de vendas com status local"""
    
    # Buscar vendas do SQL Server
    vendas = get_vendas_from_db(empresa, obra)
    
    # Buscar contratos locais
    contratos_locais = {
        c["venda"]: c for c in get_all_contracts_for_obra(empresa, obra)
    }
    
    # Combinar dados
    resultado = []
    for venda in vendas:
        venda_num = venda.get("venda")
        contrato_local = contratos_locais.get(venda_num, {})
        
        item = {
            **venda,
            "status": contrato_local.get("status", "nao_enviado"),
            "tipoAssinatura": contrato_local.get("tipo_assinatura", "pendente_escolha"),
            "dataEnvio": contrato_local.get("data_envio"),
            "dataAssinatura": contrato_local.get("data_assinatura"),
            "responsavelEnvio": contrato_local.get("responsavel_envio"),
            "observacoes": contrato_local.get("observacoes", ""),
            "propostaStatus": contrato_local.get("proposta_status", "nao_gerada"),
            "propostaData": contrato_local.get("proposta_data"),
            "pendencias": contrato_local.get("pendencias", ""),
            "atualizadoEm": contrato_local.get("atualizado_em")
        }
        
        # Aplicar filtros
        if status and item["status"] != status:
            continue
        if tipo_assinatura and item["tipoAssinatura"] != tipo_assinatura:
            continue
        if corretor and corretor.lower() not in (item.get("corretor") or "").lower():
            continue
        
        resultado.append(item)
    
    return {
        "data": resultado,
        "total": len(resultado),
        "statusOptions": STATUS_OPTIONS,
        "tipoAssinaturaOptions": TIPO_ASSINATURA_OPTIONS,
        "propostaStatusOptions": PROPOSTA_STATUS_OPTIONS
    }


@router.post("/contratos")
async def atualizar_contrato(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra"),
    contrato: ContratoUpdate = ...
):
    """Cria ou atualiza o status de um contrato"""
    
    # Validar status
    if contrato.status and contrato.status not in STATUS_OPTIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Status inválido. Opções: {STATUS_OPTIONS}"
        )
    
    # Validar tipo de assinatura
    if contrato.tipo_assinatura and contrato.tipo_assinatura not in TIPO_ASSINATURA_OPTIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de assinatura inválido. Opções: {TIPO_ASSINATURA_OPTIONS}"
        )
    
    # Atualizar contrato
    resultado = update_contract(
        empresa=empresa,
        obra=obra,
        venda=contrato.venda,
        status=contrato.status,
        tipo_assinatura=contrato.tipo_assinatura,
        data_envio=contrato.data_envio,
        data_assinatura=contrato.data_assinatura,
        responsavel_envio=contrato.responsavel_envio,
        observacoes=contrato.observacoes,
        proposta_status=contrato.proposta_status,
        proposta_data=contrato.proposta_data,
        pendencias=contrato.pendencias
    )
    
    return {
        "success": True,
        "data": resultado,
        "message": "Contrato atualizado com sucesso"
    }


@router.get("/contratos/metrics")
async def get_metricas_contratos(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Retorna métricas consolidadas dos contratos"""
    
    # Buscar total de vendas para comparar
    vendas = get_vendas_from_db(empresa, obra)
    total_vendas = len(vendas)
    
    # Buscar métricas dos contratos locais
    metrics = get_contracts_metrics(empresa, obra)
    
    # Calcular quantos não tem status definido ainda
    com_status = metrics["total"]
    sem_status = total_vendas - com_status
    
    return {
        "totalVendas": total_vendas,
        "comControle": com_status,
        "semControle": sem_status,
        "naoEnviado": metrics["nao_enviado"] + sem_status,  # Inclui os sem status
        "enviado": metrics["enviado"],
        "pendenteAssinatura": metrics["pendente_assinatura"],
        "assinado": metrics["assinado"],
        "cancelado": metrics["cancelado"],
        "assinaturaDigital": metrics["assinatura_digital"],
        "assinaturaBalcao": metrics["assinatura_balcao"],
        "pendenteEscolha": metrics["pendente_escolha"] + sem_status
    }


@router.get("/contratos/export")
async def exportar_contratos(
    empresa: int = Query(..., description="Código da empresa"),
    obra: str = Query(..., description="Código da obra")
):
    """Exporta lista de contratos em formato para Excel"""
    
    vendas = get_vendas_from_db(empresa, obra)
    contratos_locais = {
        c["venda"]: c for c in get_all_contracts_for_obra(empresa, obra)
    }
    
    # Mapeamento de labels
    status_labels = {
        "nao_enviado": "Não Enviado",
        "enviado": "Enviado",
        "pendente_assinatura": "Pend. Assinatura",
        "assinado": "Assinado",
        "cancelado": "Cancelado"
    }
    
    tipo_labels = {
        "pendente_escolha": "Pendente",
        "digital": "Digital",
        "balcao": "Balcão"
    }
    
    resultado = []
    for venda in vendas:
        venda_num = venda.get("venda")
        contrato_local = contratos_locais.get(venda_num, {})
        
        status = contrato_local.get("status", "nao_enviado")
        tipo = contrato_local.get("tipo_assinatura", "pendente_escolha")
        
        resultado.append({
            "Venda": venda_num,
            "Cliente": venda.get("cliente", ""),
            "CPF": venda.get("cpf", ""),
            "Quadra": venda.get("quadra", ""),
            "Lote": venda.get("lote", ""),
            "Corretor": venda.get("corretor", ""),
            "Data Venda": venda.get("dataVenda", ""),
            "Status Contrato": status_labels.get(status, status),
            "Tipo Assinatura": tipo_labels.get(tipo, tipo),
            "Data Envio": contrato_local.get("data_envio", ""),
            "Data Assinatura": contrato_local.get("data_assinatura", ""),
            "Responsável Envio": contrato_local.get("responsavel_envio", ""),
            "Observações": contrato_local.get("observacoes", "")
        })
    
    return {
        "data": resultado,
        "total": len(resultado),
        "geradoEm": datetime.now().isoformat()
    }
