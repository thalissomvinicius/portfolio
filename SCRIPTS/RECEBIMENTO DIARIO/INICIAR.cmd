@echo off
chcp 65001 >nul
title Sistema de Recebimento Diário
cls

echo ================================================
echo   Sistema de Recebimento Diário
echo   Desenvolvido por: Vinicius Dev
echo ================================================
echo.

:: Diretórios
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

:: Matar processos anteriores nas portas 8001 e 5174
echo Verificando processos existentes...
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8001') do (
    taskkill /PID %%i /F >nul 2>&1
)
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :5174') do (
    taskkill /PID %%i /F >nul 2>&1
)

:: Verificar se dependências do backend estão instaladas
echo Verificando ambiente do backend...
if not exist "%BACKEND%\venv\Scripts\python.exe" (
    echo ERRO: Ambiente virtual nao encontrado em %BACKEND%\venv
    echo Execute: cd backend ^&^& python -m venv venv ^&^& venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

:: Verificar se node_modules do frontend existem
if not exist "%FRONTEND%\node_modules" (
    echo Instalando dependencias do frontend...
    cd /d "%FRONTEND%"
    call npm install
    cd /d "%ROOT%"
)

echo.
echo Iniciando Backend (FastAPI na porta 8001)...
start "Backend - Recebimento Diario" cmd /k "cd /d "%BACKEND%" && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

echo Aguardando backend inicializar...
timeout /t 3 >nul

echo Iniciando Frontend (React na porta 5174)...
start "Frontend - Recebimento Diario" cmd /k "cd /d "%FRONTEND%" && npm run dev"

timeout /t 3 >nul

echo.
echo ================================================
echo   Sistema iniciado com sucesso!
echo ================================================
echo.
echo   Frontend:  http://localhost:5174
echo   Backend:   http://localhost:8001
echo   API Docs:  http://localhost:8001/docs
echo.
echo Abrindo navegador...
timeout /t 2 >nul
start "" http://localhost:5174

echo.
echo Pressione qualquer tecla para sair deste menu.
echo (Os servidores continuarao rodando em segundo plano)
pause >nul
