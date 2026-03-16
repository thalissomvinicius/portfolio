---
description: Iniciar o sistema (backend + frontend) no localhost e IP
---

// turbo-all

1. Iniciar o backend FastAPI:
```
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Executar no diretório: `novo/backend`

2. Iniciar o frontend React:
```
npm run dev -- --host
```
Executar no diretório: `novo/frontend`

## URLs de acesso:
- **Backend:** http://localhost:8000 ou http://[SEU-IP]:8000
- **Frontend:** http://localhost:5173 ou http://[SEU-IP]:5173
