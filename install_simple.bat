@echo off
chcp 65001 >nul
title 🧠 INSTALADOR SIMPLE - ASISTENTE IA
color 0A

echo ====================================================
echo 🧠 INSTALADOR SIMPLE - ASISTENTE IA
echo ====================================================
echo.

:check_python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado
    echo 📥 Ejecutando instalador de Python...
    start "" "instalar_python.bat"
    exit
)

echo ✅ Python detectado: 
python --version
echo.

:install_deps
echo 📦 Instalando dependencias...
echo 💡 Esto puede tomar varios minutos...
echo.

pip install --upgrade pip >nul
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo 📋 Instalando dependencias basicas...
    pip install gradio requests pyttsx3 SpeechRecognition pyaudio
)

echo.
echo ✅ Dependencias instaladas!
echo.

:create_launcher
echo 🚀 Creando lanzador...
(
echo @echo off
echo chcp 65001 ^>nul
echo title Asistente IA
echo echo Iniciando Asistente IA...
echo python main.py
echo pause
) > "Asistente IA.bat"

echo ✅ Lanzador creado: "Asistente IA.bat"
echo.

:final
echo ====================================================
echo ✅ INSTALACION COMPLETADA!
echo ====================================================
echo.
echo 🚀 PARA USAR LA APLICACION:
echo   1. Doble clic en: "Asistente IA.bat"
echo   2. O ejecuta: python main.py
echo.
echo ⚠️  Si hay errores de voz, ignoralos por ahora.
echo.

set /p run="¿Ejecutar ahora? (s/n): "
if /i "%run%"=="s" (
    echo Iniciando...
    "Asistente IA.bat"
)

pause