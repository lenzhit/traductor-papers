@echo off
:: Cambiar al directorio donde se encuentra este archivo .bat
cd /d "%~dp0"

title Lanzador - Academic Paper Multi-Translator
color 0B

echo Iniciando Academic Paper Multi-Translator...
echo Directorio de trabajo: %CD%
echo.

if not exist "venv\Scripts\activate.bat" (
    echo Creando entorno virtual e instalando requerimientos...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo Abriendo la aplicacion en tu navegador...
python run_app.py

pause
