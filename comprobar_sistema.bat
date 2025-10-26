@echo off
chcp 65001 >nul
title 🔧 DIAGNÓSTICO COMPLETO DEL SISTEMA
color 0E

echo ====================================================
echo 🔧 DIAGNÓSTICO COMPLETO - ASISTENTE IA
echo ====================================================
echo.

echo 1. 🔍 INFORMACIÓN DEL SISTEMA...
systeminfo | findstr /C:"Nombre del sistema" /C:"Memoria física" /C:"Procesador(es)" | head -3

echo.
echo 2. 🐍 VERIFICANDO PYTHON...
python --version >nul 2>&1
if %errorlevel% == 0 (
    python --version
    echo ✅ Python funciona correctamente
) else (
    echo ❌ Python NO está instalado o no está en PATH
)

echo.
echo 3. 📁 VERIFICANDO ARCHIVOS...
if exist "main.py" (echo ✅ main.py encontrado) else (echo ❌ main.py NO encontrado)
if exist "requirements.txt" (echo ✅ requirements.txt encontrado) else (echo ❌ requirements.txt NO encontrado)

echo.
echo 4. 📦 VERIFICANDO DEPENDENCIAS...
python -c "import gradio" >nul 2>&1 && echo ✅ gradio instalado || echo ❌ gradio NO instalado
python -c "import requests" >nul 2>&1 && echo ✅ requests instalado || echo ❌ requests NO instalado
python -c "import pyttsx3" >nul 2>&1 && echo ✅ pyttsx3 instalado || echo ❌ pyttsx3 NO instalado
python -c "import psutil" >nul 2>&1 && echo ✅ psutil instalado || echo ❌ psutil NO instalado

echo.
echo 5. 🤖 VERIFICANDO OLLAMA...
ollama --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Ollama instalado
    ollama --version
) else (
    echo ❌ Ollama NO instalado
)

echo.
echo 6. 🌐 VERIFICANDO CONEXIÓN...
python -c "import requests; r=requests.get('http://localhost:11434/api/tags', timeout=5); print('✅ Ollama responde') if r.status_code==200 else print('❌ Ollama no responde')" 2>nul

echo.
echo 7. 💾 ESPACIO EN DISCO...
for /f "tokens=3" %%a in ('dir /-c . 2^>nul ^| find "bytes libres"') do echo ✅ Espacio libre: %%a

echo.
echo ====================================================
echo 📊 DIAGNÓSTICO COMPLETADO
echo ====================================================
echo.
pause