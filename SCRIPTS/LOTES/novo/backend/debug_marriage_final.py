
import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

def debug_marriage():
    conn_str = (
        f"DRIVER={{SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASS')};"
    )
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Consulta para o cliente 4380
        query = """
        SELECT cod_pf, estciv_pf, RegCasamento_pf 
        FROM PesFis 
        WHERE cod_pf = 4380
        """
        
        cursor.execute(query)
        row = cursor.fetchone()
        
        if row:
            print(f"Cliente 4380:")
            print(f"Estado Civil: {row.estciv_pf}")
            print(f"Regime Casamento: {row.RegCasamento_pf}")
        else:
            print("Cliente 4380 não encontrado em PesFis.")
            
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    debug_marriage()
