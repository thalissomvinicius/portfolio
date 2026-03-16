import os
import sys
import pyodbc
from database import get_connection_string, DB_CONFIG

def test_connection():
    print("="*60)
    print("TESTE DE CONEXÃO COM BANCO DE DADOS")
    print("="*60)
    
    print(f"Configuração Atual:")
    print(f"Server:   {DB_CONFIG['server']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"UID:      {DB_CONFIG['uid']}")
    print(f"Port:     {DB_CONFIG['port'] or 'Default (1433 or Dynamic)'}")
    print("-" * 60)
    
    conn_str = get_connection_string()
    # Mask password for display
    safe_str = conn_str.replace(DB_CONFIG['pwd'], '********')
    print(f"String de Conexão: {safe_str}")
    print("-" * 60)
    
    print("Tentando conectar... (Isso pode levar alguns segundos)")
    
    try:
        conn = pyodbc.connect(conn_str)
        print("\n✅ SUCESSO! Conexão estabelecida.")
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print(f"Versão do Banco: {row[0]}")
        
        conn.close()
        
    except Exception as e:
        print("\n❌ FALHA NA CONEXÃO.")
        print(f"Erro: {e}")
        
        print("\nSUGESTÕES DE RESOLUÇÃO:")
        print("1. VPN: Verifique se sua VPN da empresa está ligada.")
        print("2. Endereço IP: Se estiver fora da rede, defina a variável de ambiente DB_SERVER para o IP do servidor.")
        print("   Exemplo (PowerShell): $env:DB_SERVER='192.168.1.100'")
        print("3. Porta: Se usar SSH Tunnel, defina DB_SERVER='localhost' e DB_PORT='1433'.")
        print("   Exemplo (PowerShell): $env:DB_SERVER='localhost'; $env:DB_PORT='1433'")

if __name__ == "__main__":
    # Ensure current directory is in path to import database.py
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    test_connection()
