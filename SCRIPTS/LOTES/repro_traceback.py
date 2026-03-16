import asyncio
import sys
import os

# Ajustar sys.path para o backend
sys.path.append(os.path.join(os.getcwd(), 'novo', 'backend'))

from routes import quitacao
from fastapi import HTTPException

async def test_error():
    params = {
        'empresa': 999,
        'obra': '70100',
        'venda': 22198,
        'data': '2026-01-13',
        'matricula': '4006',
        'folha': '06',
        'livro': '2N',
        'tipos': 'E,P,S,I'
    }
    
    print(f"Testando com parâmetros: {params}")
    try:
        # Chamando a função diretamente como faria o FastAPI
        response = await quitacao.gerar_termo_quitacao_docx(**params)
        print("Sucesso! O documento foi gerado.")
    except HTTPException as e:
        print(f"HTTPException {e.status_code}: {e.detail}")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_error())
