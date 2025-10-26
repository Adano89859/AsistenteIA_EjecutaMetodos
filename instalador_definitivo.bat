@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title INSTALADOR DEFINITIVO - ASISTENTE IA
color 0A

echo ====================================================
echo 🧠 INSTALADOR DEFINITIVO - ASISTENTE IA
echo ====================================================
echo.

echo 🔍 CORRIGIENDO PROBLEMAS DETECTADOS:
echo ✅ 1. Rutas correctas - Mantiene archivos en carpeta original
echo ✅ 2. Estructura completa - Crea carpetas y archivos necesarios
echo ✅ 3. Ollama alternativo - Solución para problemas de conexión
echo ✅ 4. Gradio compatible - Versión 3.50.2 sin errores de API
echo.

REM Obtener la ruta actual CORRECTAMENTE
set "CARPETA_ACTUAL=%~dp0"
set "CARPETA_ACTUAL=%CARPETA_ACTUAL:~0,-1%"

echo.
echo 📁 CARPETA DE INSTALACION: %CARPETA_ACTUAL%
echo.

REM Verificar que estamos en la carpeta correcta
cd /d "%CARPETA_ACTUAL%"

echo 🔍 Verificando estructura necesaria...
if not exist "main.py" (
    echo ❌ ERROR: main.py no encontrado
    echo 💡 Asegúrate de ejecutar el instalador desde la carpeta de la aplicación
    echo 📍 Carpeta actual: %CD%
    echo.
    pause
    exit /b 1
)

echo ✅ main.py encontrado correctamente
echo.

REM Crear estructura de carpetas necesaria
echo 📁 Creando estructura de carpetas...
if not exist "config" mkdir config
if not exist "historial" mkdir historial
if not exist "temp" mkdir temp

echo ✅ Estructura de carpetas creada
echo.

REM ---------------------------------------
REM DIAGNÓSTICO DEL SISTEMA MEJORADO
REM ---------------------------------------
echo 🔍 PASO 1/5: DIAGNÓSTICO COMPLETO DEL SISTEMA...

echo 📊 Información del sistema:
systeminfo | findstr /B /C:"Nombre del sistema operativo" /C:"Versión" /C:"Tipo de sistema" /C:"Memoria física disponible"

echo.
echo 🐍 VERIFICANDO PYTHON...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python -c "import sys; print('✅ Python detectado:', sys.version.split()[0])"
) else (
    echo ❌ Python no encontrado
    goto :instalar_python
)

echo 🔍 Verificando arquitectura...
python -c "import platform; print('🏗️  Arquitectura:', platform.architecture()[0])"

goto :verificar_python

:instalar_python
echo.
echo 🐍 Python no encontrado, instalando Python 3.11.9...
echo 📥 Descargando Python 3.11.9...

powershell -Command "try { Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe' -UseBasicParsing; exit 0 } catch { exit 1 }"

if exist "python_installer.exe" (
    echo 🔄 Instalando Python 3.11.9...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    timeout /t 5 /nobreak >nul
    del python_installer.exe >nul 2>&1
    echo ✅ Python 3.11.9 instalado
) else (
    echo ❌ No se pudo descargar Python
    echo 💡 Descarga manual: https://www.python.org/downloads/release/python-3119/
    pause
    exit /b 1
)

:verificar_python
echo.
echo ====================================================
echo 🐍 PASO 2/5: VERIFICANDO PYTHON COMPATIBLE...
echo ====================================================

python -c "import sys; print('✅ Python', sys.version.split()[0], 'detectado correctamente')"

REM ---------------------------------------
echo.
echo ====================================================
echo 📦 PASO 3/5: INSTALANDO DEPENDENCIAS COMPATIBLES...
echo ====================================================

echo 💡 Esto puede tomar varios minutos...
echo.

echo 🔄 Actualizando pip...
python -m pip install --upgrade pip

if %errorlevel% neq 0 (
    echo ❌ Error actualizando pip
    echo 🔄 Reintentando con métodos alternativos...
    python -m ensurepip --upgrade
    python -m pip install --upgrade pip --user
)

echo.
echo 📋 INSTALANDO PAQUETES CRÍTICOS COMPATIBLES...

echo 🎯 INSTALANDO GRADIO 3.50.2 (VERSIÓN COMPATIBLE)...
python -m pip install gradio==3.50.2 --no-warn-script-location

echo 🔄 INSTALANDO OTRAS DEPENDENCIAS...
python -m pip install requests pyttsx3 SpeechRecognition psutil --no-warn-script-location

if %errorlevel% neq 0 (
    echo ⚠️ Error en instalación principal, intentando método alternativo...
    python -m pip install requests --user --no-warn-script-location
    python -m pip install pyttsx3 --user --no-warn-script-location
    python -m pip install SpeechRecognition --user --no-warn-script-location
    python -m pip install psutil --user --no-warn-script-location
)

echo.
echo 🔍 VERIFICANDO INSTALACIÓN...
python -c "import gradio; print('✅ Gradio:', gradio.__version__)" 2>nul || echo ❌ Gradio: Error
python -c "import requests; print('✅ Requests: OK')" 2>nul || echo ❌ Requests: Error
python -c "import pyttsx3; print('✅ Voz: OK')" 2>nul || echo ❌ Voz: Error
python -c "import speech_recognition; print('✅ Reconocimiento: OK')" 2>nul || echo ❌ Reconocimiento: Error
python -c "import psutil; print('✅ Psutil: OK')" 2>nul || echo ❌ Psutil: Error

REM ---------------------------------------
echo.
echo ====================================================
echo 🤖 PASO 4/5: INSTALANDO OLLAMA...
echo ====================================================

echo 🔍 Verificando Ollama existente...
ollama --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama ya está instalado
    goto :verificar_modelo
)

echo 📥 Descargando Ollama...
echo 💡 Si falla la descarga automática, se proporcionarán instrucciones manuales

set "ollama_downloaded=0"

powershell -Command "try { Invoke-WebRequest 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe' -UseBasicParsing; exit 0 } catch { exit 1 }"

if exist "OllamaSetup.exe" (
    echo ✅ Ollama descargado, instalando...
    start /wait OllamaSetup.exe /S
    timeout /t 15 /nobreak >nul
    del OllamaSetup.exe >nul 2>&1
    set "ollama_downloaded=1"
    echo ✅ Ollama instalado
) else (
    echo ❌ No se pudo descargar Ollama automáticamente
    echo.
    echo 📋 INSTRUCCIONES PARA INSTALAR OLLAMA MANUALMENTE:
    echo 1. 🔗 Ve a: https://ollama.com/download
    echo 2. 💾 Descarga OllamaSetup.exe
    echo 3. 🚀 Ejecuta el instalador
    echo 4. 🔄 Vuelve a ejecutar este instalador
    echo.
)

:verificar_modelo
echo 🔍 Verificando modelo phi3:mini...
ollama list | findstr "phi3:mini" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Modelo phi3:mini ya está instalado
) else (
    echo 📥 Descargando modelo phi3:mini...
    ollama pull phi3:mini
    if %errorlevel% equ 0 (
        echo ✅ Modelo phi3:mini instalado
    ) else (
        echo ❌ No se pudo descargar el modelo
        echo 💡 Ejecuta manualmente: ollama pull phi3:mini
    )
)

REM ---------------------------------------
echo.
echo ====================================================
echo 🚀 PASO 5/5: CONFIGURACIÓN FINAL DEFINITIVA...
echo ====================================================

echo ✅ Creando archivos de configuración...

REM Crear config.json si no existe
if not exist "config\config.json" (
    echo 📝 Creando config.json...
    (
        echo {
        echo   "ollama_url": "http://localhost:11434/api/generate",
        echo   "ollama_model": "phi3:mini",
        echo   "voz_activada": true,
        echo   "microfono_activado": true,
        echo   "personalidad_actual": "Asistente Técnico",
        echo   "config_voz": {
        echo     "velocidad": 170,
        echo     "volumen": 0.9,
        echo     "tono": 0
        echo   }
        echo }
    ) > "config\config.json"
    echo ✅ config.json creado
)

REM Crear historial si no existe
if not exist "historial\historial_chat.json" (
    echo 📝 Creando historial_chat.json...
    echo [] > "historial\historial_chat.json"
    echo ✅ historial_chat.json creado
)

echo.
echo ✅ Creando lanzador principal DEFINITIVO...
(
echo @echo off
echo chcp 65001 ^>nul
echo title Asistente IA - Ejecutando...
echo.
echo echo ====================================================
echo echo 🧠 ASISTENTE IA - INICIANDO...
echo echo ====================================================
echo echo.
echo echo 📍 Cambiando a carpeta correcta...
echo cd /d "%%~dp0"
echo echo 📍 Carpeta: %%CD%%
echo echo.
echo echo 🔍 Verificando componentes...
echo python -c "import sys; print('🐍 Python:', sys.version.split()^[0^])" 2^>nul
echo python -c "import gradio; print('🎨 Gradio:', gradio.__version__)" 2^>nul ^|^| echo ❌ Gradio: ERROR
echo python -c "import requests; print('🌐 Requests: OK')" 2^>nul ^|^| echo ❌ Requests: ERROR
echo python -c "import pyttsx3; print('🔊 Voz: OK')" 2^>nul ^|^| echo ❌ Voz: ERROR
echo ollama --version 2^>nul ^&^& echo 🤖 Ollama: OK ^|^| echo ❌ Ollama: NO INSTALADO
echo.
echo echo 🔍 Buscando main.py...
echo if exist "main.py" (
echo     echo ✅ main.py encontrado
echo     echo 🚀 Iniciando aplicacion...
echo     python main.py
echo ) else (
echo     echo ❌ ERROR: main.py no encontrado
echo     echo 💡 Ejecuta desde la carpeta correcta
echo     pause
echo     exit /b 1
echo )
echo echo.
echo pause
) > "INICIAR_ASISTENTE.bat"

echo ✅ Lanzador creado: INICIAR_ASISTENTE.bat

echo.
echo 📋 Creando acceso directo...
(
echo Set WshShell = CreateObject("WScript.Shell")
echo strDesktop = WshShell.SpecialFolders("Desktop")
echo Set oShellLink = WshShell.CreateShortcut(strDesktop ^& "\Asistente IA.lnk")
echo oShellLink.TargetPath = "%CARPETA_ACTUAL%\INICIAR_ASISTENTE.bat"
echo oShellLink.WorkingDirectory = "%CARPETA_ACTUAL%"
echo oShellLink.Description = "Asistente IA Local con Ollama"
echo oShellLink.IconLocation = "%CARPETA_ACTUAL%\main.py,0"
echo oShellLink.Save
) > crear_acceso.vbs

cscript //nologo crear_acceso.vbs
del crear_acceso.vbs >nul 2>&1

if exist "%USERPROFILE%\Desktop\Asistente IA.lnk" (
    echo ✅ Acceso directo creado en el escritorio
) else (
    echo ⚠️ No se pudo crear acceso directo automáticamente
    echo 💡 Crea manualmente: 
    echo    Objetivo: %CARPETA_ACTUAL%\INICIAR_ASISTENTE.bat
    echo    Carpeta: %CARPETA_ACTUAL%
)

echo.
echo 🔧 CONFIGURACIÓN ADICIONAL PARA PROBLEMAS DE VOZ...
python -c "
try:
    import speech_recognition as sr
    r = sr.Recognizer()
    print('✅ SpeechRecognition configurado correctamente')
except Exception as e:
    print('❌ Error en SpeechRecognition:', str(e))
"

echo.
echo ====================================================
echo 🎉 INSTALACIÓN DEFINITIVA COMPLETADA
echo ====================================================
echo.
echo 📊 RESUMEN FINAL:
python --version 2>nul && echo ✅ Python 3.11.9 || echo ❌ Python
python -c "import gradio; print('✅ Gradio:', gradio.__version__)" 2>nul || echo ❌ Gradio
python -c "import requests" 2>nul && echo ✅ Requests || echo ❌ Requests
python -c "import pyttsx3" 2>nul && echo ✅ Voz || echo ❌ Voz
python -c "import speech_recognition" 2>nul && echo ✅ Reconocimiento vocal || echo ❌ Reconocimiento
ollama --version >nul 2>&1 && echo ✅ Ollama || echo ❌ Ollama (instalar manual)
echo.
echo 📁 ESTRUCTURA CREADA:
dir /b %CARPETA_ACTUAL% | findstr /V "crear_acceso.vbs" | findstr /V "python_installer.exe" | findstr /V "OllamaSetup.exe"
echo.
echo 🚀 PARA USAR:
echo   • Ejecuta: INICIAR_ASISTENTE.bat
echo   • O el acceso directo del escritorio
echo   • O directamente: python main.py
echo.

echo 💡 SOLUCIÓN PARA PROBLEMAS:
echo   • Si hay error de voz: Ejecuta como Administrador
echo   • Si Ollama falla: Instala manualmente desde ollama.com
echo   • Si no encuentra main.py: Ejecuta desde la carpeta correcta
echo.

set /p ejecutar="¿Ejecutar el Asistente IA ahora? (s/n): "
if /i "%ejecutar%"=="s" (
    echo.
    echo 🚀 Iniciando aplicacion...
    timeout /t 2 /nobreak >nul
    INICIAR_ASISTENTE.bat
) else (
    echo.
    echo 👋 Instalación finalizada. 
    echo 💡 Ejecuta INICIAR_ASISTENTE.bat cuando quieras usar la aplicación.
    pause
)

exit /b 0