# VallePrime Dashboard - React + FastAPI

Sistema de controle de vendas, boletos e sinais de corretagem com interface React moderna e backend FastAPI.

## 🚀 Como Executar

### 1. Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

O backend estará disponível em: **http://localhost:8000**

Documentação da API: **http://localhost:8000/docs**

### 2. Frontend (React + TypeScript)

```bash
cd frontend
npm install
npm run dev
```

O frontend estará disponível em: **http://localhost:5173**

## 📁 Estrutura do Projeto

```
novo/
├── backend/                 # API FastAPI
│   ├── main.py             # Entry point
│   ├── database.py         # Conexão com SQL Server
│   ├── requirements.txt    # Dependências Python
│   └── routes/             # Endpoints da API
│       ├── vendas.py       # Vendas e Resumo
│       ├── sinais.py       # Sinais de Corretagem
│       ├── boletos.py      # Boletos
│       └── relatorio.py    # Geração de PDF
├── frontend/               # Interface React
│   ├── src/
│   │   ├── App.tsx         # Componente principal
│   │   ├── components/     # Componentes React
│   │   ├── api/            # Cliente API
│   │   └── types/          # TypeScript types
│   └── package.json
└── README.md
```

## 🎨 Funcionalidades

### Dashboard
- Métricas consolidadas (vendas, boletos, sinais)
- Tabela de vendas com filtros
- Download CSV e PDF

### Sinais de Corretagem
- Listagem de sinais a receber
- Filtro por data de vencimento
- Métricas e exportação

### Boletos
- Listagem de boletos gerados
- Filtro por venda
- Status de envio por email

### Detalhes por Venda
- Consulta detalhada
- Sinais pagos
- Boletos da venda

## 🛠️ Tecnologias

- **Frontend:** React 18, TypeScript, TailwindCSS, Vite
- **Backend:** FastAPI, Python 3.8+, pyodbc
- **Database:** SQL Server (UAU-VALLEPRIME)
- **PDF:** ReportLab

---

**VallePrime** © 2024
