@echo off
chcp 65001 >nul
title 🐍 INSTALADOR DE PYTHON - VERSIÓN ROBUSTA
color 0A

echo ====================================================
echo 🐍 INSTALADOR DE PYTHON 3.11.9
echo ====================================================
echo.

echo 📥 Descargando Python...
powershell -Command "& {
    try {
        Write-Host '📥 Descargando Python 3.11.9...'
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        \$ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe' -TimeoutSec 60
        if (Test-Path 'python_installer.exe') {
            \$size = (Get-Item 'python_installer.exe').Length / 1MB
            Write-Host \"✅ Descarga completada - \$size MB\"
            exit 0
        } else {
            Write-Host '❌ El archivo no se descargó correctamente'
            exit 1
        }
    } catch {
        Write-Host \"❌ Error en descarga: \$($_.Exception.Message)\"
        exit 1
    }
}"

if not exist "python_installer.exe" (
    echo ❌ Error al descargar Python
    echo 🔗 Descarga manual desde: https://python.org
    echo 📋 Abriendo navegador...
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ⚙️ Instalando Python... POR FAVOR ESPERA...
echo 💡 Se instalará automáticamente con las opciones recomendadas
echo 📋 Esto puede tomar 2-3 minutos...
echo.

start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Limpiar instalador
if exist "python_installer.exe" del python_installer.exe

:: Verificar instalación
timeout /t 3 /nobreak >nul
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python --version
    echo ✅ Python instalado correctamente!
    echo.
    echo 🔄 Continuando con la instalación principal...
    timeout /t 3 /nobreak >nul
    start "" "INSTALADOR_COMPLETO.bat"
) else (
    echo ❌ ERROR: Python no se instaló correctamente
    echo 💡 POSIBLES SOLUCIONES:
    echo   1. Reinicia el ordenador
    echo   2. Instala Python manualmente desde python.org
    echo   3. Asegúrate de marcar "Add Python to PATH"
    echo.
    pause
)

exit /b 0