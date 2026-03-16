"""
VallePrime Dashboard - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes import vendas, sinais, boletos, relatorio, mensagens, inadimplentes, evolucao, recebimentos, loteamento, disponibilidades, contratos, relatorio_executivo, quitacao, feedbacks, auth, users

# Create FastAPI app
app = FastAPI(
    title="VallePrime Dashboard API",
    description="API para o sistema de controle de vendas e boletos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vendas.router, prefix="/api", tags=["Vendas"])
app.include_router(sinais.router, prefix="/api", tags=["Sinais"])
app.include_router(boletos.router, prefix="/api", tags=["Boletos"])
app.include_router(relatorio.router, prefix="/api", tags=["Relatórios"])
app.include_router(mensagens.router, prefix="/api", tags=["Mensagens"])
app.include_router(inadimplentes.router, prefix="/api", tags=["Inadimplentes"])
app.include_router(evolucao.router, prefix="/api", tags=["Evolução"])
app.include_router(recebimentos.router, prefix="/api", tags=["Recebimentos"])
app.include_router(loteamento.router, prefix="/api/loteamento", tags=["Loteamento"])
app.include_router(disponibilidades.router, prefix="/api", tags=["Disponibilidades"])
app.include_router(contratos.router, prefix="/api", tags=["Contratos"])
app.include_router(relatorio_executivo.router, prefix="/api", tags=["Relatório Executivo"])
app.include_router(quitacao.router, prefix="/api", tags=["Quitação"])
app.include_router(feedbacks.router, prefix="/api", tags=["Feedbacks"])
app.include_router(auth.router, prefix="/api", tags=["Autenticação"])
app.include_router(users.router, prefix="/api", tags=["Usuários"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "online", "message": "VallePrime Dashboard API"}

@app.get("/api/health")
async def health():
    """API health check"""
    return {"status": "healthy"}

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
