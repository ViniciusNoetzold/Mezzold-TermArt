@echo off
setlocal
title Mezzold TermArt - Web Studio
color 0B
cd /d "%~dp0"

echo ==============================================================================
echo                      MEZZOLD TERMART STUDIO v2.0
echo                 Iniciando painel visual no navegador...
echo ==============================================================================
echo.
echo Servidor iniciando em: http://localhost:7860
echo Abrindo seu navegador padrao...
echo Pressione Ctrl+C nesta janela para encerrar o servidor.
echo.

start http://localhost:7860
python termstudio.py

pause
