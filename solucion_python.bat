@echo off
echo ====================================================
echo SOLUCION MANUAL - INSTALACION DE PYTHON 3.11.9
echo ====================================================
echo.

echo 1. CERRANDO TODAS LAS VENTANAS DE PYTHON...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1

echo 2. DESCARGANDO PYTHON 3.11.9...
if exist python_installer.exe del python_installer.exe
powershell -Command "Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe' -UseBasicParsing"

echo 3. INSTALANDO PYTHON 3.11.9 CON OPCIONES CORRECTAS...
echo ESPERA 2-3 MINUTOS...
python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_launcher=0

echo 4. ESPERANDO QUE TERMINE LA INSTALACION...
timeout /t 15 /nobreak >nul

echo 5. VERIFICANDO LA NUEVA INSTALACION...
set "PYTHON311_PATH=%LocalAppData%\Programs\Python\Python311\python.exe"
if exist "%PYTHON311_PATH%" (
    echo ✅ Python 3.11.9 instalado correctamente
    "%PYTHON311_PATH%" --version
) else (
    echo ❌ Python 3.11.9 no se instalo correctamente
    echo 💡 Ejecuta manualmente: python_installer.exe
    pause
    exit /b 1
)

echo 6. INSTALANDO GRADIO CON PYTHON 3.11...
"%PYTHON311_PATH%" -m pip install gradio==4.36.1

echo 7. VERIFICANDO...
"%PYTHON311_PATH%" -c "import gradio; print('✅ Gradio instalado correctamente')"

echo.
echo ✅ SOLUCION COMPLETADA
echo 💡 Ahora ejecuta el instalador principal nuevamente
pause