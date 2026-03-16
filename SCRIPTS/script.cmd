@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: Configurações
set "PROJECT_PATH=C:\Users\thalissom.cruz\Desktop\DASHVALLE\VALOR QUITAÇÃO"
set "SCRIPT_NAME=main.py"
set "APP_NAME=Dashboard Valle"
set "URL=http://localhost:8501"

:: Cores para mensagens
set "GREEN=^[[92m"
set "RESET=^[[0m"

:: Tela inicial com a mensagem de autoria
:MAIN_MENU
cls
echo ================================
echo  %APP_NAME%
echo ================================
echo.
echo Desenvolvido por Vinicius Dev
echo.
echo [1] Iniciar Dashboard
echo [2] Parar Dashboard
echo [0] Sair
echo ================================
set /p "choice=Escolha uma opção: "

if "%choice%"=="1" goto START_APP
if "%choice%"=="2" goto STOP_APP
if "%choice%"=="0" exit
echo Opção inválida!
timeout /t 2 >nul
goto MAIN_MENU

:: Iniciar o Dashboard
:START_APP
cls
echo Iniciando o Dashboard...
:: Verificar se o Streamlit já está rodando
for /f %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find /i "streamlit" /c') do set count=%%i
if %count% gtr 0 (
    echo Dashboard já está rodando.
    start "" "%URL%"
    timeout /t 3 >nul
    goto MAIN_MENU
)

:: Verificar se o caminho e o script existem
if not exist "%PROJECT_PATH%\%SCRIPT_NAME%" (
    echo Arquivo Python não encontrado!
    pause
    goto MAIN_MENU
)

:: Iniciar o Streamlit
cd /d "%PROJECT_PATH%"
start /b cmd /c "python -m streamlit run %SCRIPT_NAME% --server.port 8501"

:: Animação de sucesso
echo Iniciando o Dashboard. Aguarde
for /L %%i in (1,1,10) do (
    echo.
    timeout /t 1 >nul
)

:: Exibir mensagem de sucesso em verde
echo %GREEN%Dashboard iniciado com sucesso! Acesse em %URL% %RESET%
pause
goto MAIN_MENU

:: Parar o Dashboard
:STOP_APP
cls
echo Parando o Dashboard...
:: Encontrar e matar o processo Streamlit
for /f "skip=1 tokens=2" %%i in ('wmic process where "name='python.exe' and commandline like '%%streamlit%%'" get processid /format:csv') do (
    if not "%%i"=="" (
        taskkill /f /pid %%i >nul
        echo Processo do Dashboard finalizado.
    )
)
pause
goto MAIN_MENU

:: Sair
:EXIT
cls
echo ╔═════════════════════════════════════════════════════════════════╗
echo ║                      👋 ATÉ LOGO!                              ║
echo ╚═════════════════════════════════════════════════════════════════╝
echo.
echo Parando todos os processos do dashboard...

for /f "skip=1 tokens=2" %%i in ('wmic process where "name='python.exe' and commandline like '%%streamlit%%'" get processid /format:csv 2^>nul') do (
    if not "%%i"=="" (
        echo 🔪 Finalizando processo %%i...
        taskkill /f /pid %%i >nul 2>&1
    )
)

echo ✅ Finalizado com sucesso!
timeout /t 2 >nul
exit /b 0