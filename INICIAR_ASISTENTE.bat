@echo off
chcp 65001 >nul
title Asistente IA - Ejecutando...

echo ====================================================
echo 🧠 ASISTENTE IA - INICIANDO...
echo ====================================================
echo.

REM 📍 CAMBIAR A LA CARPETA DONDE ESTÁ ESTE ARCHIVO
cd /d "%~dp0"
echo 📍 Carpeta correcta: %CD%

echo 🔍 Verificando componentes...
python -c "import sys; print('🐍 Python:', sys.version.split()[0])" 2>nul
python -c "import gradio; print('🎨 Gradio: OK')" 2>nul || echo ❌ Gradio: ERROR
python -c "import requests; print('🌐 Requests: OK')" 2>nul || echo ❌ Requests: ERROR
python -c "import pyttsx3; print('🔊 Voz: OK')" 2>nul || echo ❌ Voz: ERROR
ollama --version 2>nul && echo 🤖 Ollama: OK || echo ❌ Ollama: NO INSTALADO

echo.
echo 🔍 Buscando main.py...
if exist "main.py" (
    echo ✅ main.py encontrado
    echo 🚀 Iniciando aplicacion...
    python main.py
) else (
    echo ❌ ERROR: main.py no encontrado
    echo 💡 El archivo INICIAR_ASISTENTE.bat debe estar en la misma carpeta que main.py
    echo 📍 Buscando main.py en el sistema...
    dir /s /b main.py 2>nul
    echo.
    echo 💡 SOLUCIÓN: Copia main.py a esta carpeta: %CD%
    pause
    exit /b 1
)
echo.
pause