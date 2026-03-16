import sys
from fastapi.testclient import TestClient
sys.path.append('c:/Users/thalissom.cruz/Desktop/PORTIFOLIO/SCRIPTS/LOTES/novo/backend')
import main

client = TestClient(main.app)

try:
    # Just a basic request, even if it 404s, it's fine. We want to see if the DOCX path crashes on valid data
    # Actually, we know this Lote exists: Empresa 6, Obra 001, Quadra 01, Lote 01 based on earlier history.
    response = client.get("/api/quitacao/termo?empresa=6&obra=001&quadra=01&lote=01&formato=docx")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print(response.json())
    elif response.status_code == 200:
        print("Success!")
    else:
        print(response.content)
except Exception as e:
    import traceback
    traceback.print_exc()
