import pyodbc

# Configurações
username = "thalissom.cruz"
password = "@valle2035"
domain = "VALLEPRIME"

DB_SERVER = 'DCWBD11\\VALLEPRIME_PRD'
DB_DATABASE = 'UAU-VALLEPRIME'

print("=== TESTE DE AUTENTICAÇÃO ===\n")

# 1. Verificar se o usuário existe no banco UAU
print("1. Buscando usuário no banco UAU...")
conn_str = (
    f"Driver={{SQL Server}};"
    f"Server={DB_SERVER};"
    f"Database={DB_DATABASE};"
    f"UID=consultasBD;"
    f"PWD=V@lle#2021;"
    f"Timeout=30;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("""
    SELECT Login_usr, Nome_usr, Email_usr, UsuarioAD_usr, Status_usr
    FROM Usuarios 
    WHERE UsuarioAD_usr = ?
""", (username,))
row = cursor.fetchone()
conn.close()

if row:
    status = "Ativo" if row[4] == 1 else "Inativo"
    print(f"   ✓ Encontrado!")
    print(f"   Login: {row[0]}")
    print(f"   Nome: {row[1]}")
    print(f"   Email: {row[2]}")
    print(f"   AD: {row[3]}")
    print(f"   Status: {status}")
else:
    print(f"   ✗ Usuário '{username}' não encontrado no campo UsuarioAD_usr")

# 2. Testar autenticação Windows/AD via SQL Server
print("\n2. Testando autenticação Windows/AD...")
try:
    conn_str_ad = (
        f"Driver={{SQL Server}};"
        f"Server={DB_SERVER};"
        f"Database={DB_DATABASE};"
        f"UID={domain}\\{username};"
        f"PWD={password};"
        f"Timeout=10;"
    )
    conn_ad = pyodbc.connect(conn_str_ad)
    conn_ad.close()
    print("   ✓ Autenticação Windows/AD OK!")
except Exception as e:
    print(f"   ✗ Falha na autenticação: {e}")

print("\n=== TESTE CONCLUÍDO ===")
