import os
import time
import subprocess
import sys

def start_tunnel():
    """
    Starts a clear SSH tunnel for SQL Server.
    Prerequisite: 'ssh' command must be available in system PATH.
    """
    print("="*60)
    print("INICIADOR DE TÚNEL SSH")
    print("="*60)
    
    # Configuration - REPLACE THESE or set ENV VARS
    SSH_HOST = os.getenv('SSH_HOST', 'user@remote-jump-server.com')
    SSH_KEY_PATH = os.getenv('SSH_KEY_PATH', 'C:/Users/thalissom.cruz/.ssh/id_rsa')
    REMOTE_DB_SERVER = os.getenv('REMOTE_DB_SERVER', 'DCWBD11')
    LOCAL_PORT = os.getenv('DB_PORT', '1433')
    
    print(f"Configuração:")
    print(f"SSH Host: {SSH_HOST}")
    print(f"Key Path: {SSH_KEY_PATH}")
    print(f"Destino:  {REMOTE_DB_SERVER}:1433")
    print(f"Local:    localhost:{LOCAL_PORT}")
    print("-" * 60)
    
    cmd = [
        "ssh",
        "-N", # Do not execute a remote command
        "-L", f"{LOCAL_PORT}:{REMOTE_DB_SERVER}:1433",
        "-i", SSH_KEY_PATH,
        SSH_HOST
    ]
    
    print(f"Executando: {' '.join(cmd)}")
    print("Conectando... (Ctrl+C para parar)")
    
    try:
        # Start SSH process
        process = subprocess.Popen(cmd)
        
        # Wait a bit
        time.sleep(2)
        
        if process.poll() is None:
            print("\n✅ Túnel provávelmente ativo!")
            print("Agora você pode configurar o banco para conectar em 'localhost'.")
            print(f"PowerShell: $env:DB_SERVER='localhost'; $env:DB_PORT='{LOCAL_PORT}'")
            process.wait()
        else:
            print("\n❌ Erro ao iniciar o túnel SSH.")
            print("Verifique suas credenciais e endereço.")
            
    except KeyboardInterrupt:
        print("\nParando túnel...")
        process.terminate()
    except FileNotFoundError:
        print("\n❌ Comando 'ssh' não encontrado. Instale o OpenSSH Client.")

if __name__ == "__main__":
    start_tunnel()
