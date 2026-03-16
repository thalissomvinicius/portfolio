from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import pyodbc

router = APIRouter()

DATA_FILE = os.path.join("data", "users.json")

# Database configuration
DB_CONFIG = {
    "driver": "SQL Server",
    "server": os.getenv('DB_SERVER', 'DCWBD11\\VALLEPRIME_PRD'),
    "database": os.getenv('DB_DATABASE', 'UAU-VALLEPRIME'),
    "uid": os.getenv('DB_UID', 'consultasBD'),
    "pwd": os.getenv('DB_PWD', 'V@lle#2021'),
    "timeout": 30
}

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: str
    username: str
    nome: str
    role: str
    modulos: List[str] = []
    email: Optional[str] = None

def get_db_connection():
    conn_str = (
        f"Driver={{{DB_CONFIG['driver']}}};"
        f"Server={DB_CONFIG['server']};"
        f"Database={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['uid']};"
        f"PWD={DB_CONFIG['pwd']};"
        f"Timeout={DB_CONFIG['timeout']};"
    )
    return pyodbc.connect(conn_str)

def validate_windows_credentials(username: str, password: str, domain: str = "VALLEPRIME") -> bool:
    """Valida credenciais usando autenticação Windows via tentativa de conexão SQL"""
    try:
        # Tenta conectar no SQL Server usando as credenciais do usuário
        # Esta é uma forma de validar indiretamente as credenciais do AD
        conn_str = (
            f"Driver={{SQL Server}};"
            f"Server={DB_CONFIG['server']};"
            f"Database={DB_CONFIG['database']};"
            f"UID={domain}\\{username};"
            f"PWD={password};"
            f"Timeout=5;"
        )
        conn = pyodbc.connect(conn_str)
        conn.close()
        return True
    except Exception as e:
        print(f"Falha na autenticação Windows: {e}")
        return False

def get_user_from_uau(username_ad: str):
    """Busca dados do usuário no banco UAU pelo UsuarioAD"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Login_usr, Nome_usr, Email_usr, UsuarioAD_usr
            FROM Usuarios 
            WHERE (UsuarioAD_usr = ? OR LOWER(UsuarioAD_usr) = ?) AND Status_usr = 1
        """, (username_ad, username_ad.lower()))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "login": row[0],
                "nome": row[1],
                "email": row[2],
                "usuario_ad": row[3]
            }
        return None
    except Exception as e:
        print(f"Erro banco: {e}")
        return None

def load_local_users():
    """Carrega usuários locais do arquivo JSON"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def get_user_permissions(username: str):
    """Busca permissões de módulos do usuário no arquivo local"""
    users = load_local_users()
    for user in users:
        if user.get("username", "").lower() == username.lower() or user.get("usuario_ad", "").lower() == username.lower():
            return user.get("modulos", []), user.get("role", "user")
    return ["all"], "user"  # Padrão: acesso total se não tiver config específica

@router.post("/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    username = credentials.username.strip()
    password = credentials.password
    
    # Normalizar username (remover domínio se existir)
    if "\\" in username:
        username = username.split("\\")[1]
    if "@" in username:
        username = username.split("@")[0]
    
    username_lower = username.lower()
    
    # 1. Primeiro, tentar login local (admin e usuários configurados manualmente)
    local_users = load_local_users()
    for user in local_users:
        user_login = user.get("username", "").lower()
        user_ad = user.get("usuario_ad", "").lower()
        
        if (user_login == username_lower or user_ad == username_lower):
            if user.get("password") == password:
                return LoginResponse(
                    id=user["id"],
                    username=user["username"],
                    nome=user["nome"],
                    role=user.get("role", "user"),
                    modulos=user.get("modulos", ["all"]),
                    email=user.get("email")
                )
    
    # 2. Buscar usuário no banco UAU pelo UsuarioAD
    uau_user = get_user_from_uau(username_lower)
    
    if not uau_user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado no sistema")
    
    # 3. Tentar validar senha via Windows/AD
    ad_valid = validate_windows_credentials(username, password)
    
    if ad_valid:
        # Login AD bem-sucedido
        modulos, role = get_user_permissions(username_lower)
        return LoginResponse(
            id=uau_user["login"],
            username=username_lower,
            nome=uau_user["nome"],
            role=role,
            modulos=modulos,
            email=uau_user.get("email")
        )
    
    # 4. Se AD falhou, verificar se tem senha local configurada para este usuário AD
    for user in local_users:
        if user.get("usuario_ad", "").lower() == username_lower:
            if user.get("password") == password:
                return LoginResponse(
                    id=user["id"],
                    username=user["username"],
                    nome=user["nome"],
                    role=user.get("role", "user"),
                    modulos=user.get("modulos", ["all"]),
                    email=user.get("email")
                )
    
    raise HTTPException(status_code=401, detail="Senha inválida. Use sua senha do Windows ou a senha configurada no sistema.")
