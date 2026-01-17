# Absensi Desktop App

Aplikasi kiosk profesional untuk sistem absensi berbasis pengenalan wajah. Dibangun dengan **Python (PySide6)** dan terintegrasi dengan backend FastAPI.

## ✨ Fitur Utama

- **🎯 Real-time Face Detection** - Bounding box dengan animasi scan line
- **👥 Multi-Face Recognition** - Deteksi hingga 5 wajah sekaligus
- **🎤 Natural TTS** - Sapaan suara Indonesia (Microsoft Edge TTS)
- **📊 Dual Mode** - Kiosk Mode + Admin Dashboard
- **🔄 Offline Queue** - Data tersimpan saat offline, auto-sync saat online
- **📡 Smart Reconnection** - Deteksi koneksi otomatis dengan indikator status

## 📁 Struktur Folder

```
Absensi Desktop/
├── app.py              # Main application
├── ui.py               # UI layout & styling
├── ui_components.py    # Animated button components
├── api_client.py       # API communication
├── camera.py           # Camera & face detection
├── tts_engine.py       # Text-to-Speech
├── settings_dialog.py  # Settings UI
├── logger_config.py    # Logging config
├── run_app.bat         # 1-click launcher
├── requirements.txt    # Dependencies
└── .env                # Configuration (create from .env.example)
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
python -m venv app.venv
.\app.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
copy .env.example .env
# Edit .env - set API_BASE and DEVICE_TOKEN
```

### 3. Run
```bash
# Option A: Double-click run_app.bat
# Option B: Manual
.\app.venv\Scripts\activate
python app.py
```

## ⚙️ Configuration (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE` | Backend API URL | http://localhost:8000 |
| `DEVICE_ID` | Unique device identifier | stb-01 |
| `DEVICE_TOKEN` | Authentication token | - |
| `CAM_INDEX` | Camera index | 0 |
| `EDGE_VOICE` | TTS voice | id-ID-GadisNeural |

## 🖥️ System Requirements

- **OS**: Windows 10/11
- **Python**: 3.10+
- **Webcam**: USB or built-in
- **Internet**: Required for TTS (cached after first use)

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| No sound | Check internet (TTS needs connection first time) |
| Camera black | Close other apps using camera (Zoom, Meet) |
| API error | Ensure backend server is running |
| Offline indicator | Check network; data will sync when online |

---
*Frontend for Absensi Kiosk System - Tugas Akhir Project*
