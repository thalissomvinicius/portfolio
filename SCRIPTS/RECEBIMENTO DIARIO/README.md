# Sistema de Recebimento Diário 💰

Sistema moderno de relatórios de recebimentos diários desenvolvido com React + TypeScript (frontend) e FastAPI (backend).

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Executando o Projeto](#executando-o-projeto)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Solução de Problemas](#solução-de-problemas)

## 🎯 Visão Geral

Este sistema permite:
- Gerar relatórios detalhados de recebimentos por período
- Comparar recebimentos entre diferentes meses
- Exportar dados para Excel
- Visualizar estatísticas e gráficos interativos
- Suportar múltiplas empresas simultaneamente

## 📦 Pré-requisitos

### Backend
- Python 3.8 ou superior
- SQL Server (acesso ao banco de dados configurado)
- pip (gerenciador de pacotes Python)

### Frontend
- Node.js 16.x ou superior
- npm ou yarn

## 🚀 Instalação

### 1. Clone o repositório (se aplicável)
```bash
git clone <url-do-repositorio>
cd "RECEBIMENTO DIARIO"
```

### 2. Instale as dependências do Backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Instale as dependências do Frontend

```bash
cd frontend
npm install
```

## ⚙️ Configuração

### Backend

1. Copie o arquivo de exemplo de configuração:
```bash
cd backend
copy .env.example .env
```

2. Edite o arquivo `.env` com suas configurações:
```env
# Database Configuration
DB_SERVER=DCWBD11\VALLEPRIME_PRD
DB_DATABASE=UAU-VALLEPRIME
DB_UID=consultasBD
DB_PWD=V@lle#2021

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

### Frontend

O frontend está pré-configurado para conectar ao backend em `http://localhost:8000`.

Para alterar a URL da API, crie um arquivo `.env` na pasta `frontend`:
```env
VITE_API_URL=http://localhost:8000
```

## 🎮 Executando o Projeto

### Opção 1: Executar Manualmente

#### Terminal 1 - Backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Opção 2: Script Automatizado (Windows)

Execute o script PowerShell na raiz do projeto:
```bash
.\start-dev.ps1
```

### Acessando a Aplicação

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentação API (Swagger)**: http://localhost:8000/docs
- **Documentação API (ReDoc)**: http://localhost:8000/redoc

## 📁 Estrutura do Projeto

```
RECEBIMENTO DIARIO/
├── backend/
│   ├── main.py              # Aplicação FastAPI principal
│   ├── database.py          # Configuração do banco de dados
│   ├── services.py          # Lógica de negócio
│   ├── requirements.txt     # Dependências Python
│   └── .env.example         # Exemplo de configuração
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── api.ts          # Cliente API
│   │   ├── App.tsx         # Componente principal
│   │   └── index.css       # Estilos globais
│   ├── package.json        # Dependências Node
│   └── vite.config.ts      # Configuração Vite
├── start-dev.ps1           # Script de inicialização
└── README.md               # Este arquivo
```

## ✨ Funcionalidades

### Relatórios Diários
- Selecione período personalizado ou por mês
- Escolha uma ou múltiplas empresas
- Visualize recebimentos diários com estatísticas
- Exporte para Excel

### Comparação Mensal
- Compare até 12 meses diferentes
- Visualize gráficos comparativos
- Analise tendências e variações
- Exporte comparações para Excel

### Interface Moderna
- Design responsivo (mobile e desktop)
- Animações suaves
- Gradientes e efeitos glassmorphism
- Tema moderno e profissional

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e rápido
- **Uvicorn**: Servidor ASGI
- **Pandas**: Manipulação de dados
- **PyODBC**: Conexão com SQL Server
- **OpenPyXL**: Geração de arquivos Excel

### Frontend
- **React 19**: Biblioteca UI
- **TypeScript**: Tipagem estática
- **Vite**: Build tool
- **Tailwind CSS**: Framework CSS
- **Axios**: Cliente HTTP
- **Recharts**: Gráficos interativos
- **React Router**: Roteamento

## 🔧 Solução de Problemas

### Backend não inicia

**Erro: "Driver not found"**
- Instale o SQL Server ODBC Driver
- Verifique se o driver está configurado corretamente

**Erro: "Connection timeout"**
- Verifique se o servidor SQL está acessível
- Confirme as credenciais no arquivo `.env`
- Verifique o firewall

### Frontend não conecta ao Backend

**Erro: "Network Error"**
- Verifique se o backend está rodando em http://localhost:8000
- Confirme a configuração de CORS no backend
- Verifique o console do navegador para erros

### Porta já em uso

**Backend (porta 8000)**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Frontend (porta 5173)**
```bash
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Problemas com dependências

**Backend**
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Frontend**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📝 Notas Adicionais

### Desenvolvimento
- O backend usa reload automático em modo desenvolvimento
- O frontend usa HMR (Hot Module Replacement) para atualizações instantâneas
- Logs detalhados estão disponíveis no console

### Produção
Para deploy em produção:
1. Configure variáveis de ambiente adequadas
2. Desative o modo reload no backend
3. Faça build do frontend: `npm run build`
4. Use um servidor web (nginx, Apache) para servir os arquivos estáticos

## 👨‍💻 Desenvolvedor

**Vinicius Dev**
- Sistema Valle
- Versão: 2.0.0

## 📄 Licença

Proprietary - Uso interno Valle

---

Para mais informações ou suporte, entre em contato com a equipe de desenvolvimento.
