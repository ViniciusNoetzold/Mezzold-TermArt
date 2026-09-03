@echo off
setlocal enabledelayedexpansion
title Mezzold TermArt - Web Studio
color 0B
cd /d "%~dp0"

echo ==============================================================================
echo                      MEZZOLD TERMART STUDIO v2.0
echo                 Iniciando painel visual e rede local...
echo ==============================================================================
echo.

:: Detect primary LAN IPv4 address automatically
set LAN_IP=192.168.0.188
for /f "tokens=*" %%i in ('python -c "import subprocess, re; out = subprocess.check_output('ipconfig', text=True); ips = [m.group(1) for m in re.finditer(r'IPv4[^\r\n:]*:\s*([0-9.]+)', out) if not m.group(1).startswith('127.') and not m.group(1).startswith('169.254.')]; lan = [ip for ip in ips if ip.startswith('192.168.') or ip.startswith('10.')]; print(lan[0] if lan else (ips[0] if ips else '192.168.0.188'))"') do (
    set LAN_IP=%%i
)

echo  ==============================================================================
echo    [1] ACESSO LOCAL (Neste Computador):
echo        --^> http://localhost:7860
echo.
echo    [2] ACESSO PELA REDE LOCAL (Wi-Fi / Celular / Outros Computadores):
echo        --^> http://!LAN_IP!:7860
echo.
echo    [3] ACESSO PELA INTERNET (Link Publico Seguro Cloudflare):
echo        --^> Se desejar abrir para o mundo, execute: iniciar_tunel_publico.bat
echo  ==============================================================================
echo.
echo Abrindo janela Localhost e janela da Rede Local (!LAN_IP!)...
echo.

:: Abre as duas abas: Localhost e IP de rede
start http://localhost:7860
timeout /t 1 /nobreak >nul
start http://!LAN_IP!:7860

echo Pressione Ctrl+C nesta janela para encerrar o servidor.
echo.

python termstudio.py

pause
