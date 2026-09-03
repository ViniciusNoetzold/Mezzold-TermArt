@echo off
title Mezzold TermArt - Tunel Publico (Cloudflare)
color 0A
cd /d "%~dp0"

echo ==============================================================================
echo                 MEZZOLD TERMART STUDIO - TUNEL PUBLICO (HTTPS)
echo       Criando link publico com SSL seguro via Cloudflare...
echo ==============================================================================
echo.

if not exist "bin\cloudflared.exe" (
    echo Baixando binario oficial do Cloudflare Tunnel...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'bin\cloudflared.exe'"
)

echo Conectando ao Cloudflare... Aguarde o link https aparecer abaixo:
echo.
bin\cloudflared.exe tunnel --url http://localhost:7860

pause
