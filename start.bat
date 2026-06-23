@echo off
title Backero Viral Video API
echo ====================================
echo  Backero - Viral Video Production API
echo ====================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.11+ from python.org
    pause
    exit /b
)

:: Create venv if missing
if not exist "venv" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install deps
echo [2/3] Installing dependencies...
pip install -r requirements.txt -q

:: Start server
echo [3/3] Starting server on http://localhost:8000
echo.
echo  API Docs:   http://localhost:8000/docs
echo  Health:     http://localhost:8000/health
echo  Frontend:   Open your frontend at http://localhost:5173
echo.
echo  Press Ctrl+C to stop
echo ====================================
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
