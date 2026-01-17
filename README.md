<p align="center">
  <h1 align="center">Absensi Desktop</h1>
  <p align="center">
    <strong>Aplikasi Kiosk untuk Sistem Absensi Berbasis Pengenalan Wajah</strong>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-6.4+-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-blue?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square" alt="Status">
</p>

---

## Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| **Real-time Detection** | Bounding box dengan animasi scan line |
| **Multi-Face** | Deteksi hingga 5 wajah sekaligus |
| **Natural TTS** | Sapaan suara Indonesia (Edge TTS) |
| **Smart Reconnection** | Auto-retry dengan status indicator |
| **Offline Queue** | Data tersimpan saat offline |
| **Modern UI** | Animated buttons & hover effects |

---

## Tech Stack

<table>
<tr>
<td align="center"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40"/><br>Python</td>
<td align="center"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/qt/qt-original.svg" width="40"/><br>PySide6</td>
<td align="center"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/opencv/opencv-original.svg" width="40"/><br>OpenCV</td>
</tr>
</table>

### Libraries

```
PySide6            # Modern Qt6 GUI framework
opencv-python      # Computer vision & camera
edge-tts           # Microsoft Edge Text-to-Speech
requests           # HTTP client for API
python-dotenv      # Environment configuration
```

---

## UI Features

### Status Colors (Bounding Box)
| Warna | Status |
|-------|--------|
| ⬜ **Putih** | Scanning... |
| 🟨 **Kuning** | Verifying... |
| 🟩 **Hijau** | Recognized ✓ |
| 🟥 **Merah** | Unknown |

### Animasi
- **Scanning Line** - Garis bergerak dalam bounding box
- **Corner Accents** - Aksen sudut modern
- **Animated Buttons** - Hover & click effects

---

## Quick Start

### Clone & Setup
```bash
git clone https://github.com/your-username/App-Desktop.git
cd "Absensi Desktop"
python -m venv app.venv
.\app.venv\Scripts\activate
pip install -r requirements.txt
```

### Configure
```bash
copy .env.example .env
# Edit .env - isi DEVICE_TOKEN dari admin
```

### Run
```bash
# Windows (1-click)
.\run_app.bat

# Manual
python app.py
```

---

## Struktur Project

```
Absensi Desktop/
├── 📄 app.py              # Main application
├── 📄 ui.py               # UI layout & styling
├── 📄 ui_components.py    # Animated components
├── 📄 api_client.py       # API communication
├── 📄 camera.py           # Camera & face detection
├── 📄 tts_engine.py       # Text-to-Speech
├── 📄 settings_dialog.py  # Settings UI
├── 📂 assets/             # Images & icons
├── 📂 logs/               # Application logs
├── 📄 .env.example        # Environment template
├── 📄 requirements.txt    # Dependencies
└── 📄 run_app.bat         # 1-click launcher
```

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE` | Backend API URL | http://localhost:8000 |
| `DEVICE_ID` | Unique device identifier | stb-01 |
| `DEVICE_TOKEN` | Authentication token (**REQUIRED**) | - |
| `CAM_INDEX` | Camera index | 0 |
| `EDGE_VOICE` | TTS voice | id-ID-GadisNeural |

---

## System Requirements

| Requirement | Minimum |
|-------------|---------|
| **OS** | Windows 10/11 |
| **Python** | 3.10+ |
| **RAM** | 4 GB |
| **Camera** | USB/Built-in Webcam |
| **Internet** | Required for TTS |

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| 🔇 Tidak ada suara | Cek koneksi internet (TTS butuh online pertama kali) |
| 📷 Kamera hitam | Tutup aplikasi lain yang pakai kamera |
| ❌ API Error | Pastikan backend server berjalan |
| ⚠️ Offline | Cek network; data akan sync saat online |

---
<p align="center">
  <sub>elsann</sub>
</p>
