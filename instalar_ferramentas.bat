@echo off
setlocal
cd /d "%~dp0"

echo ==============================================================================
echo              MEZZOLD TERMART SUITE - INSTALADOR AUTOMATICO
echo ==============================================================================
echo.
echo [1/3] Verificando instalacao do Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Python nao foi encontrado no sistema!
    echo Por favor, instale o Python 3.10+ e marque a opcao "Add python.exe to PATH".
    echo Download em: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python detectado com sucesso!
echo.

echo [2/3] Instalando dependencias do Python (FastAPI, Pillow, PyFiglet, etc)...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao instalar alguns pacotes via pip.
    echo.
    pause
    exit /b 1
)
echo.
echo [OK] Todas as bibliotecas Python foram instaladas!
echo.

echo [3/3] Verificando binarios nativos de alta performance...
if exist "bin\ascii-image-converter.exe" (
    echo   [OK] ascii-image-converter.exe - Go Engine
) else (
    echo   [AVISO] ascii-image-converter.exe nao encontrado em bin\
)

if exist "bin\chafa.exe" (
    echo   [OK] chafa.exe - C Engine Sub-pixel Graphics
) else (
    echo   [AVISO] chafa.exe nao encontrado em bin\
)

if exist "bin\vhs.exe" (
    echo   [OK] vhs.exe - Go Engine Terminal Recorder
) else (
    echo   [AVISO] vhs.exe nao encontrado em bin\
)

if exist "bin\agg.exe" (
    echo   [OK] agg.exe - Rust Engine Asciinema to GIF
) else (
    echo   [AVISO] agg.exe nao encontrado em bin\
)

echo.
echo ==============================================================================
echo          TUDO PRONTO! O AMBIENTE ESTA 100%% CONFIGURADO!
echo ==============================================================================
echo.
echo Agora voce pode dar um duplo clique em:
echo   - iniciar_studio.bat   (Para abrir o Web Studio no navegador)
echo   - iniciar_terminal.bat (Para abrir o Terminal Interativo)
echo.
pause
