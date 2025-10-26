@echo off
chcp 65001 >nul
title 🤖 INSTALADOR OLLAMA - VERSIÓN ROBUSTA
color 0B

echo ====================================================
echo 🤖 INSTALADOR OLLAMA - INSTALACIÓN ROBUSTA
echo ====================================================
echo.

echo 🔍 VERIFICANDO REQUISITOS DEL SISTEMA...
echo.

:verificar_permisos
echo 🔒 Verificando permisos...
echo. > %temp%\test_permisos.txt 2>nul
if %errorlevel% equ 0 (
    del %temp%\test_permisos.txt 2>nul
    echo ✅ Permisos de escritura: OK
) else (
    echo ⚠️  Permisos limitados - Ejecuta como Administrador si falla
)

:verificar_espacio
for /f "tokens=3" %%a in ('dir /-c . 2^>nul ^| find "bytes libres"') do (
    echo 💾 Espacio libre: %%a
)

:verificar_ollama_existente
echo.
echo 🔍 Buscando Ollama instalado...
ollama --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama ya está instalado
    goto :seleccionar_modelo
)

:verificar_conexion
echo 🌐 Verificando conexión a internet...
ping -n 1 8.8.8.8 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Sin conexión a internet
    goto :error_conexion
)

:descargar_ollama
echo.
echo 📥 DESCARGANDO OLLAMA...
echo 💡 Esto puede tomar 2-5 minutos...

:: Método principal con PowerShell
echo 🔄 Descargando desde servidor oficial...
powershell -Command "& {
    try {
        Write-Host '📥 Conectando con Ollama...'
        \$ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe' -TimeoutSec 120
        if (Test-Path 'OllamaSetup.exe') {
            \$size = (Get-Item 'OllamaSetup.exe').Length / 1MB
            Write-Host \"✅ Descarga completada - \$size MB\"
        }
    } catch {
        Write-Host \"❌ Error: \$($_.Exception.Message)\"
        exit 1
    }
}"

if not exist "OllamaSetup.exe" (
    echo ❌ No se pudo descargar Ollama automáticamente
    goto :descarga_manual
)

:instalar_ollama
echo.
echo ⚙️ INSTALANDO OLLAMA...
echo 💡 Por favor espera...

start /wait OllamaSetup.exe /S
timeout /t 5 /nobreak >nul

:: Limpiar instalador
if exist "OllamaSetup.exe" del OllamaSetup.exe

:verificar_instalacion
echo 🔍 Verificando instalación...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Ollama puede necesitar reinicio
    echo 💡 Continuando con la instalación...
)

:iniciar_servicio
echo.
echo 🔄 INICIANDO SERVICIO OLLAMA...
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if %errorlevel% neq 0 (
    echo 🚀 Iniciando servicio...
    start "" /B ollama serve
    timeout /t 10 /nobreak >nul
)

:seleccionar_modelo
echo.
echo 🤖 SELECCIÓN DE MODELO IA
echo ====================================================
echo 📊 Modelos recomendados:
echo.
echo 1. 🚀 phi3:mini (1.8 GB) - PARA PC DÉBILES
echo    • 2-4 núcleos, 4-8 GB RAM
echo    • Rápido y eficiente
echo.
echo 2. ⚡ llama3.2:3b (1.9 GB) - EQUILIBRADO
echo    • Buen rendimiento/calidad
echo    • Bueno en español
echo.
echo 3. 💎 gemma2:2b (1.4 GB) - SUPER LIGERO
echo    • Mínimo consumo
echo    • Ideal para pruebas
echo.
set /p opcion="Selecciona modelo (1-3, Enter para phi3:mini): "

if "%opcion%"=="1" set MODELO=phi3:mini && set TAMANO=1.8 GB
if "%opcion%"=="2" set MODELO=llama3.2:3b && set TAMANO=1.9 GB
if "%opcion%"=="3" set MODELO=gemma2:2b && set TAMANO=1.4 GB
if not defined MODELO set MODELO=phi3:mini && set TAMANO=1.8 GB

:descargar_modelo
echo.
echo 📥 DESCARGANDO: %MODELO% (%TAMANO%)
echo ⏰ Tiempo estimado:
if "%MODELO%"=="phi3:mini" echo   • 5-15 minutos
if "%MODELO%"=="llama3.2:3b" echo   • 5-15 minutos
if "%MODELO%"=="gemma2:2b" echo   • 3-10 minutos
echo.
echo 💡 POR FAVOR NO CIERRES ESTA VENTANA
echo.

ollama pull %MODELO%
if %errorlevel% equ 0 (
    echo ✅ %MODELO% instalado correctamente
) else (
    echo ⚠️ Error en primer intento, reintentando...
    timeout /t 3 /nobreak >nul
    ollama pull %MODELO%
)

:actualizar_configuracion
echo.
echo ⚙️ ACTUALIZANDO CONFIGURACIÓN...
python -c "
import json
import os
import sys

try:
    # Ruta absoluta del archivo de configuración
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config_file = os.path.join(base_dir, 'config', 'config.json')

    print(f'📁 Configurando: {config_file}')

    # Crear directorio si no existe
    os.makedirs(os.path.dirname(config_file), exist_ok=True)

    # Cargar configuración existente o crear nueva
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print('✅ Configuración existente cargada')
    else:
        config = {}
        print('✅ Creando nueva configuración')

    # Actualizar modelo
    config['ollama_model'] = '%MODELO%'
    config['ollama_url'] = 'http://localhost:11434/api/generate'
    config['voz_activada'] = True
    config['microfono_activado'] = True
    config['personalidad_actual'] = 'Asistente Técnico'
    config['config_voz'] = {
        'velocidad': 170,
        'volumen': 0.9,
        'tono': 0
    }

    # Guardar configuración
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f'✅ Configuración actualizada a: %MODELO%')

    # Verificar que se guardó correctamente
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config_verificada = json.load(f)
        modelo_guardado = config_verificada.get('ollama_model', 'NO GUARDADO')
        print(f'✅ Verificación: Modelo configurado como {modelo_guardado}')
    else:
        print('❌ ERROR: No se pudo crear el archivo de configuración')

except Exception as e:
    print(f'❌ Error crítico en configuración: {e}')
    print('💡 El asistente usará valores por defecto')
"

:verificacion_final
echo.
echo 🔍 VERIFICACIÓN FINAL...
ollama list
if %errorlevel% equ 0 (
    echo ✅ Ollama configurado correctamente
) else (
    echo ⚠️ Hay problemas con Ollama
)

echo.
echo ====================================================
echo 🎉 INSTALACIÓN OLLAMA COMPLETADA
echo ====================================================
echo 🤖 Modelo: %MODELO%
echo 🌐 URL: http://localhost:11434
echo 🚀 Comando: ollama run %MODELO% "Hola"
echo.
goto :fin

:descarga_manual
echo.
echo ❌ DESCARGAR MANUALMENTE
echo ====================================================
echo 📥 Ve a: https://ollama.com/download
echo 💡 Guarda 'OllamaSetup.exe' en esta carpeta
echo 🔄 Luego ejecuta este instalador nuevamente
echo.
pause
goto :fin

:error_conexion
echo.
echo ❌ ERROR DE CONEXIÓN
echo ====================================================
echo 🌐 Verifica tu conexión a internet
echo 🔧 Comprueba firewall/proxy
echo 📡 Intenta nuevamente con conexión estable
echo.
pause

:fin
echo ⏰ Saliendo en 3 segundos...
timeout /t 3 /nobreak >nul
exit /b 0