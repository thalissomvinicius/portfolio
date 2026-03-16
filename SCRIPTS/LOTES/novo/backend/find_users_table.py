import pyodbc

# Testar conexão usando autenticação Windows (AD)
print('=== TESTE DE AUTENTICAÇÃO WINDOWS ===\n')

# Primeiro, vamos ver a configuração do servidor
conn_str = (
    'Driver={SQL Server};'
    'Server=DCWBD11\\VALLEPRIME_PRD;'
    'Database=UAU-VALLEPRIME;'
    'UID=consultasBD;'
    'PWD=V@lle#2021;'
    'Timeout=30;'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Ver usuários com UsuarioAD configurado
print('Usuários com login AD configurado:\n')
cursor.execute("""
    SELECT TOP 20 Login_usr, Nome_usr, UsuarioAD_usr, Email_usr
    FROM Usuarios 
    WHERE UsuarioAD_usr IS NOT NULL AND UsuarioAD_usr != ''
    ORDER BY Nome_usr
""")
for row in cursor.fetchall():
    print(f"{row[0]:12} | {row[1]:30} | AD: {row[2]:20} | {row[3] or ''}")

cursor.execute("""
    SELECT COUNT(*) FROM Usuarios WHERE UsuarioAD_usr IS NOT NULL AND UsuarioAD_usr != ''
""")
total = cursor.fetchone()[0]
print(f"\nTotal com AD configurado: {total}")

conn.close()
