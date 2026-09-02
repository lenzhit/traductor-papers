@echo off
:: Cambiar al directorio donde se encuentra este archivo .bat
cd /d "%~dp0"

title Compilador de Traductor de Papers a EXE (Windows)
color 0A

echo ========================================================
echo    COMPILADOR DE EJECUTABLE WINDOWS (TraductorPapers)
echo ========================================================
echo.
echo Directorio de trabajo: %CD%
echo.

:: Verificar si python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python instalado en el sistema o en el PATH.
    echo Por favor instala Python 3.10+ y asegurate de marcar "Add Python to PATH".
    pause
    exit /b 1
)

echo [1/4] Creando / Verificando entorno virtual 'venv'...
if not exist "venv\Scripts\activate.bat" (
    python -m venv venv
)

echo [2/4] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [3/4] Instalando dependencias necesarias y PyInstaller...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo [4/4] Compilando la aplicacion con PyInstaller...
pyinstaller app.spec --clean --noconfirm

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo    COMPILACION EXITOSA!
    echo    El ejecutable se encuentra en: dist\TraductorPapers.exe
    echo ========================================================
    echo.
) else (
    echo.
    echo [ERROR] Hubo un problema durante la compilacion.
)

pause
