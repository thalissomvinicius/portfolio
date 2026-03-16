@echo off
chcp 65001 >nul
title VallePrime Dashboard
powershell -ExecutionPolicy Bypass -File "%~dp0iniciar_sistema.ps1"
pause
