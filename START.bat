@echo off
chcp 65001 >nul
echo Starting Dreamforge: Эхо Бездны...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

REM Try to run
python run.py
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start. Trying alternative installation...
    python install_deps.py
    echo.
    echo Retrying...
    python run.py
)

pause

