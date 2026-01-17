@echo off
title Absensi Desktop Launcher
cls

echo ==================================================
echo   ABSENSI DESKTOP APP - LAUNCHER
echo ==================================================
echo.

if not exist "app.venv" (
    echo [ERROR] Virtual environment 'app.venv' tidak ditemukan!
    echo Silakan install dulu dengan: python -m venv app.venv
    pause
    exit /b
)

echo [INFO] Mengaktifkan virtual environment...
call app.venv\Scripts\activate.bat

echo [INFO] Menjalankan aplikasi...
python app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Aplikasi berhenti dengan error code %errorlevel%
    pause
)
