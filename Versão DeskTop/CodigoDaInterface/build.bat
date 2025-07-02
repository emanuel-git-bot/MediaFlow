@echo off
chcp 65001 >nul
echo ================================================
echo 🔧 MEDIAFLOW DESKTOP - BUILD AUTOMATIZADO
echo ================================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro: Python não encontrado!
    echo Instale o Python e tente novamente.
    pause
    exit /b 1
)

REM Verifica se PyInstaller está instalado
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Erro ao instalar PyInstaller!
        pause
        exit /b 1
    )
)

REM Verifica se as dependências estão instaladas
echo 🔍 Verificando dependências...
python -c "import customtkinter, yt_dlp, PIL, requests" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando dependências...
    pip install -r requisitos.txt
    if errorlevel 1 (
        echo ❌ Erro ao instalar dependências!
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Iniciando build...
echo.

REM Executa o script de build
python build_app.py

echo.
echo ✅ Processo concluído!
echo 📁 Verifique a pasta MediaFlow/
echo.
pause 