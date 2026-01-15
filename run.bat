@echo off
chcp 65001 >nul
cls
echo ========================================
echo    ABSENSI DESKTOP - KIOSK & ADMIN
echo ========================================
echo.

REM Check virtual environment
if exist "app.venv\Scripts\activate.bat" (
    echo 📦 Mengaktifkan virtual environment...
    call app.venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment tidak ditemukan
    echo Membuat virtual environment...
    python -m venv app.venv
    call app.venv\Scripts\activate.bat
    echo 📦 Menginstal dependencies...
    pip install -r requirements.txt
)

REM Verify .env configuration
if not exist ".env" (
    echo ⚠️  File .env tidak ditemukan
    echo Membuat .env dari template...
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ .env dibuat dari template
    ) else (
        echo Silakan buat file .env dengan konfigurasi yang sesuai
        pause
        exit /b 1
    )
)

REM Start application
echo.
echo 🚀 Memulai Aplikasi Absensi Desktop...
echo ========================================
echo.

python app.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Aplikasi gagal dijalankan
    echo.
    echo Troubleshooting:
    echo 1. Pastikan .env sudah dikonfigurasi dengan benar
    echo 2. Pastikan VLC terinstall: https://www.videolan.org/vlc/
    echo 3. Periksa koneksi ke API server
    echo 4. Lihat logs folder untuk informasi error
    echo.
    pause
)
