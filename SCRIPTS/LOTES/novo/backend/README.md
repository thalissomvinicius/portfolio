# Backend FastAPI - VallePrime Dashboard

## Requirements
- Python 3.8+
- FastAPI
- uvicorn
- pyodbc
- pandas
- reportlab

## Run
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Endpoints
- GET /api/vendas?empresa=28&obra=70100
- GET /api/sinais?empresa=28&obra=70100&data_vencimento=2025-12-31
- GET /api/sinais/abertos?empresa=28&obra=70100
- GET /api/boletos?empresa=28
- GET /api/resumo?empresa=28&obra=70100
- GET /api/relatorio/pdf?empresa=28&obra=70100
