"""
Contracts Storage Module
Gerencia armazenamento de dados de contratos em arquivo JSON
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path

# Caminho do arquivo JSON para armazenar os contratos
DATA_DIR = Path(__file__).parent / "data"
CONTRACTS_FILE = DATA_DIR / "contratos.json"

# Status possíveis do contrato
STATUS_OPTIONS = [
    "nao_enviado",
    "enviado", 
    "pendente_assinatura",
    "assinado",
    "cancelado"
]

# Tipos de assinatura
TIPO_ASSINATURA_OPTIONS = [
    "pendente_escolha",
    "digital",
    "balcao"
]

# Status possíveis da proposta
PROPOSTA_STATUS_OPTIONS = [
    "nao_gerada",
    "gerada",
    "enviada",
    "assinada_digital",
    "assinada_presencial",
    "cancelada"
]


def ensure_data_dir():
    """Garante que o diretório de dados existe"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_contracts() -> Dict[str, Any]:
    """Carrega todos os contratos do arquivo JSON"""
    ensure_data_dir()
    
    if not CONTRACTS_FILE.exists():
        return {"contratos": {}, "ultima_atualizacao": None}
    
    try:
        with open(CONTRACTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"contratos": {}, "ultima_atualizacao": None}


def save_contracts(data: Dict[str, Any]) -> bool:
    """Salva os contratos no arquivo JSON"""
    ensure_data_dir()
    
    data["ultima_atualizacao"] = datetime.now().isoformat()
    
    try:
        with open(CONTRACTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Erro ao salvar contratos: {e}")
        return False


def get_contract_key(empresa: int, obra: str, venda: int) -> str:
    """Gera a chave única para um contrato"""
    return f"{empresa}_{obra}_{venda}"


def get_contract(empresa: int, obra: str, venda: int) -> Optional[Dict[str, Any]]:
    """Busca um contrato específico"""
    data = load_contracts()
    key = get_contract_key(empresa, obra, venda)
    return data["contratos"].get(key)


def update_contract(
    empresa: int,
    obra: str,
    venda: int,
    status: Optional[str] = None,
    tipo_assinatura: Optional[str] = None,
    data_envio: Optional[str] = None,
    data_assinatura: Optional[str] = None,
    responsavel_envio: Optional[str] = None,
    observacoes: Optional[str] = None,
    proposta_status: Optional[str] = None,
    proposta_data: Optional[str] = None,
    pendencias: Optional[str] = None
) -> Dict[str, Any]:
    """Cria ou atualiza um contrato"""
    data = load_contracts()
    key = get_contract_key(empresa, obra, venda)
    
    # Busca contrato existente ou cria novo
    contrato = data["contratos"].get(key, {
        "empresa": empresa,
        "obra": obra,
        "venda": venda,
        "status": "nao_enviado",
        "tipo_assinatura": "pendente_escolha",
        "data_envio": None,
        "data_assinatura": None,
        "responsavel_envio": None,
        "observacoes": "",
        "proposta_status": "nao_gerada",
        "proposta_data": None,
        "pendencias": "",
        "criado_em": datetime.now().isoformat(),
        "atualizado_em": None
    })
    
    # Atualiza campos se fornecidos
    if status is not None and status in STATUS_OPTIONS:
        contrato["status"] = status
    if tipo_assinatura is not None and tipo_assinatura in TIPO_ASSINATURA_OPTIONS:
        contrato["tipo_assinatura"] = tipo_assinatura
    if data_envio is not None:
        contrato["data_envio"] = data_envio
    if data_assinatura is not None:
        contrato["data_assinatura"] = data_assinatura
    if responsavel_envio is not None:
        contrato["responsavel_envio"] = responsavel_envio
    if observacoes is not None:
        contrato["observacoes"] = observacoes
    if proposta_status is not None and proposta_status in PROPOSTA_STATUS_OPTIONS:
        contrato["proposta_status"] = proposta_status
    if proposta_data is not None:
        contrato["proposta_data"] = proposta_data
    if pendencias is not None:
        contrato["pendencias"] = pendencias
    
    contrato["atualizado_em"] = datetime.now().isoformat()
    
    data["contratos"][key] = contrato
    save_contracts(data)
    
    return contrato


def get_all_contracts_for_obra(empresa: int, obra: str) -> List[Dict[str, Any]]:
    """Retorna todos os contratos de uma obra específica"""
    data = load_contracts()
    prefix = f"{empresa}_{obra}_"
    
    return [
        contrato for key, contrato in data["contratos"].items()
        if key.startswith(prefix)
    ]


def delete_contract(empresa: int, obra: str, venda: int) -> bool:
    """Remove um contrato"""
    data = load_contracts()
    key = get_contract_key(empresa, obra, venda)
    
    if key in data["contratos"]:
        del data["contratos"][key]
        save_contracts(data)
        return True
    return False


def get_contracts_metrics(empresa: int, obra: str) -> Dict[str, Any]:
    """Calcula métricas dos contratos de uma obra"""
    contratos = get_all_contracts_for_obra(empresa, obra)
    
    metrics = {
        "total": len(contratos),
        "nao_enviado": 0,
        "enviado": 0,
        "pendente_assinatura": 0,
        "assinado": 0,
        "cancelado": 0,
        "assinatura_digital": 0,
        "assinatura_balcao": 0,
        "pendente_escolha": 0
    }
    
    for c in contratos:
        status = c.get("status", "nao_enviado")
        tipo = c.get("tipo_assinatura", "pendente_escolha")
        
        if status in metrics:
            metrics[status] += 1
        
        if tipo == "digital":
            metrics["assinatura_digital"] += 1
        elif tipo == "balcao":
            metrics["assinatura_balcao"] += 1
        else:
            metrics["pendente_escolha"] += 1
    
    return metrics
