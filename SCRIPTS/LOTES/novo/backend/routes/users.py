from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import uuid

router = APIRouter()

DATA_FILE = os.path.join("data", "users.json")

class User(BaseModel):
    id: Optional[str] = None
    username: str
    password: str
    nome: str
    role: str = "user"
    modulos: List[str] = []

class UserResponse(BaseModel):
    id: str
    username: str
    nome: str
    role: str
    modulos: List[str] = []

def load_users():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

@router.get("/users")
async def get_users():
    users = load_users()
    return [UserResponse(
        id=u["id"], 
        username=u["username"], 
        nome=u["nome"], 
        role=u["role"],
        modulos=u.get("modulos", [])
    ) for u in users]

@router.post("/users")
async def create_user(user: User):
    users = load_users()
    
    for u in users:
        if u["username"] == user.username:
            raise HTTPException(status_code=400, detail="Usuário já existe")
    
    new_user = user.dict()
    new_user["id"] = str(uuid.uuid4())
    
    users.append(new_user)
    save_users(users)
    
    return {"message": "Usuário criado com sucesso", "id": new_user["id"]}

@router.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    users = load_users()
    
    for i, u in enumerate(users):
        if u["id"] == user_id:
            users[i]["username"] = user.username
            users[i]["nome"] = user.nome
            users[i]["role"] = user.role
            users[i]["modulos"] = user.modulos
            if user.password:
                users[i]["password"] = user.password
            save_users(users)
            return {"message": "Usuário atualizado com sucesso"}
    
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    users = load_users()
    
    admins = [u for u in users if u["role"] == "admin"]
    user_to_delete = next((u for u in users if u["id"] == user_id), None)
    
    if user_to_delete and user_to_delete["role"] == "admin" and len(admins) <= 1:
        raise HTTPException(status_code=400, detail="Não é possível excluir o último administrador")
    
    new_users = [u for u in users if u["id"] != user_id]
    
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    save_users(new_users)
    return {"message": "Usuário excluído com sucesso"}


# ========== ACTIVITY TRACKING ==========

ACTIVITY_FILE = os.path.join("data", "user_activity.json")

def load_activity():
    try:
        with open(ACTIVITY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_activity(activity):
    os.makedirs(os.path.dirname(ACTIVITY_FILE), exist_ok=True)
    with open(ACTIVITY_FILE, "w", encoding="utf-8") as f:
        json.dump(activity, f, ensure_ascii=False, indent=2)

class HeartbeatRequest(BaseModel):
    user_id: str

class PageAccessRequest(BaseModel):
    user_id: str
    page: str
    page_name: str

@router.post("/users/heartbeat")
async def user_heartbeat(request: HeartbeatRequest):
    """Registra que o usuário está online (heartbeat)"""
    from datetime import datetime
    
    activity = load_activity()
    user_id = request.user_id
    
    now = datetime.now().isoformat()
    
    if user_id not in activity:
        activity[user_id] = {
            "lastHeartbeat": now,
            "lastAccess": now,
            "pageHistory": []
        }
    else:
        activity[user_id]["lastHeartbeat"] = now
        # Atualiza lastAccess somente se for o primeiro heartbeat em mais de 5 minutos
        last_access = activity[user_id].get("lastAccess")
        if not last_access:
            activity[user_id]["lastAccess"] = now
    
    save_activity(activity)
    return {"status": "ok", "timestamp": now}

@router.post("/users/page-access")
async def user_page_access(request: PageAccessRequest):
    """Registra acesso a uma página específica"""
    from datetime import datetime
    
    activity = load_activity()
    user_id = request.user_id
    
    now = datetime.now().isoformat()
    
    if user_id not in activity:
        activity[user_id] = {
            "lastHeartbeat": now,
            "lastAccess": now,
            "pageHistory": []
        }
    
    # Atualiza último acesso
    activity[user_id]["lastAccess"] = now
    activity[user_id]["lastHeartbeat"] = now
    
    # Adiciona à história de páginas (máximo 20 registros)
    page_entry = {
        "page": request.page,
        "pageName": request.page_name,
        "timestamp": now
    }
    
    # Inserir no início e limitar a 20
    history = activity[user_id].get("pageHistory", [])
    history.insert(0, page_entry)
    activity[user_id]["pageHistory"] = history[:20]
    
    save_activity(activity)
    return {"status": "ok", "timestamp": now}

@router.get("/users/{user_id}/activity")
async def get_user_activity(user_id: str):
    """Retorna dados de atividade do usuário"""
    from datetime import datetime, timedelta
    
    activity = load_activity()
    user_activity = activity.get(user_id, {})
    
    # Determinar status online (considera online se heartbeat < 60 segundos)
    is_online = False
    last_heartbeat = user_activity.get("lastHeartbeat")
    
    if last_heartbeat:
        try:
            last_hb_time = datetime.fromisoformat(last_heartbeat)
            now = datetime.now()
            diff = (now - last_hb_time).total_seconds()
            is_online = diff < 60  # Online se heartbeat foi há menos de 60 segundos
        except:
            pass
    
    return {
        "isOnline": is_online,
        "lastAccess": user_activity.get("lastAccess"),
        "lastHeartbeat": last_heartbeat,
        "pageHistory": user_activity.get("pageHistory", [])
    }
