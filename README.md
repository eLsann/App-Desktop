# Absensi Desktop

Aplikasi desktop untuk sistem absensi berbasis pengenalan wajah menggunakan PySide6.

## Fitur

- Pengenalan wajah real-time via kamera
- Text-to-Speech (TTS) sapaan natural dengan Edge TTS
- Dashboard statistik absensi
- Manajemen karyawan (CRUD)
- Export laporan CSV
- UI modern dengan dark theme

## Instalasi

```bash
# Clone repository
git clone <repo-url>
cd "Absensi Desktop"

# Buat virtual environment
python -m venv app.venv
app.venv\Scripts\activate  # Windows
source app.venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Konfigurasi (.env)

```env
API_BASE=http://localhost:8000
DEVICE_ID=stb-01
DEVICE_TOKEN=token123
CAMERA_INDEX=0
EDGE_VOICE=id-ID-GadisNeural
```

## Menjalankan

```bash
# Pastikan API server berjalan terlebih dahulu
python app.py
```

## Panduan Penggunaan

### 1. Login Admin
- Buka tab **Settings**
- Masukkan username dan password
- Klik **Login**

### 2. Tambah Karyawan
- Buka tab **People**
- Klik **+ Tambah**
- Masukkan nama karyawan
- Pilih karyawan, klik ** Enroll** untuk upload foto wajah

### 3. Mulai Absensi
- Buka tab **Kiosk**
- Klik ** Mulai Scan**
- Arahkan wajah ke kamera

### 4. Lihat Laporan
- Buka tab **Reports**
- Masukkan periode (YYYY-MM)
- Klik ** Load Report** atau ** Export CSV**

## Struktur File

```
Absensi Desktop/
├── app.py          # Main application
├── ui.py           # UI components
├── api_client.py   # API client
├── camera.py       # Camera handler
├── tts_engine.py   # TTS dengan caching
├── validators.py   # Input validation
└── logger_config.py
```

## Teknologi

- PySide6 (Qt6)
- OpenCV
- Edge TTS
- pygame (audio)
- requests

## Aturan Jam Absensi

| Waktu | Keterangan |
|-------|------------|
| < 08:00 | Masuk tepat waktu |
| > 08:00 | Masuk terlambat |
| 14:00 - 16:00 | Jam pulang |
