# VallePrime Dashboard - Iniciador Unificado
# Roda backend e frontend em uma única janela

$Host.UI.RawUI.WindowTitle = "VallePrime Dashboard"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    VallePrime Dashboard - Sistema" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $baseDir "backend"
$frontendDir = Join-Path $baseDir "frontend"

Write-Host "[INFO] Diretorio base: $baseDir" -ForegroundColor Gray
Write-Host ""

# Verifica dependencias
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
$npmPath = Get-Command npm -ErrorAction SilentlyContinue

if (-not $pythonPath) {
    Write-Host "[ERRO] Python nao encontrado!" -ForegroundColor Red
    exit 1
}

if (-not $npmPath) {
    Write-Host "[ERRO] npm nao encontrado!" -ForegroundColor Red
    exit 1
}

# Libera portas em uso
Write-Host "[INFO] Liberando portas 8000 e 5173..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 1

# Inicia Backend como job
Write-Host "[1/2] Iniciando Backend (FastAPI na porta 8000)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    python main.py 2>&1
} -ArgumentList $backendDir

# Aguarda backend iniciar
Write-Host "[INFO] Aguardando backend iniciar..." -ForegroundColor Gray
Start-Sleep -Seconds 4

# Verifica se backend esta online
try {
    $null = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get -TimeoutSec 5
    Write-Host "[OK] Backend esta online!" -ForegroundColor Green
}
catch {
    Write-Host "[AVISO] Backend pode demorar mais para iniciar..." -ForegroundColor Yellow
}

# Inicia Frontend como job
Write-Host "[2/2] Iniciando Frontend (Vite na porta 5173)..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npm run dev -- --host 2>&1
} -ArgumentList $frontendDir

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    Sistema iniciado com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Cyan
$localIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Ethernet', 'Wi-Fi' | Select-Object -First 1).IPAddress
Write-Host "Frontend (Network): " -NoNewline; Write-Host "http://$localIP:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione " -NoNewline
Write-Host "Ctrl+C" -ForegroundColor Yellow -NoNewline
Write-Host " para encerrar o sistema."
Write-Host ""
Write-Host "========================================" -ForegroundColor DarkGray
Write-Host "             LOGS DO SISTEMA" -ForegroundColor DarkGray
Write-Host "========================================" -ForegroundColor DarkGray
Write-Host ""

# Loop para mostrar logs em tempo real
try {
    while ($true) {
        # Verifica e exibe saida do backend
        $backendOutput = Receive-Job -Job $backendJob -ErrorAction SilentlyContinue
        if ($backendOutput) {
            foreach ($line in $backendOutput) {
                if ($line -match "ERROR|error|Error|Traceback") {
                    Write-Host "[BACKEND] $line" -ForegroundColor Red
                }
                elseif ($line -match "WARNING|warning") {
                    Write-Host "[BACKEND] $line" -ForegroundColor Yellow
                }
                else {
                    Write-Host "[BACKEND] $line" -ForegroundColor Blue
                }
            }
        }

        # Verifica e exibe saida do frontend
        $frontendOutput = Receive-Job -Job $frontendJob -ErrorAction SilentlyContinue
        if ($frontendOutput) {
            foreach ($line in $frontendOutput) {
                if ($line -match "error|Error|ERROR") {
                    Write-Host "[FRONTEND] $line" -ForegroundColor Red
                }
                elseif ($line -match "warning|Warning") {
                    Write-Host "[FRONTEND] $line" -ForegroundColor Yellow
                }
                else {
                    Write-Host "[FRONTEND] $line" -ForegroundColor Magenta
                }
            }
        }

        # Verifica se os jobs ainda estao rodando
        if ($backendJob.State -eq "Failed") {
            Write-Host "[ERRO] Backend parou inesperadamente!" -ForegroundColor Red
            Receive-Job -Job $backendJob
        }
        if ($frontendJob.State -eq "Failed") {
            Write-Host "[ERRO] Frontend parou inesperadamente!" -ForegroundColor Red
            Receive-Job -Job $frontendJob
        }

        Start-Sleep -Milliseconds 500
    }
}
finally {
    Write-Host ""
    Write-Host "[INFO] Encerrando sistema..." -ForegroundColor Yellow
    
    # Para os jobs
    Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job -Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob -Force -ErrorAction SilentlyContinue
    Remove-Job -Job $frontendJob -Force -ErrorAction SilentlyContinue
    
    # Para processos nas portas
    Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "[OK] Sistema encerrado." -ForegroundColor Green
}
