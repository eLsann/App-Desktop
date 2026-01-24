# 📸 Absensi Desktop

<div align="center">

[![Release](https://img.shields.io/github/v/release/eLsann/App-Desktop?style=for-the-badge&color=2563EB&label=Stable%20Release)](https://github.com/eLsann/App-Desktop/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)](https://github.com/eLsann/App-Desktop/releases)
[![Python](https://img.shields.io/badge/Python-3.10-EF4444?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Intelligent Face Recognition Attendance System**
<br>
*Fast. Secure. Touchless.*

[📥 **Download & Install (Windows)**](https://github.com/eLsann/App-Desktop/releases/latest)
<br>
<a href="#-developer-setup">View Developer Guide</a>

</div>

---

## ✨ Overview
**Absensi Desktop** is an enterprise-grade attendance solution designed for the modern era. Leveraging advanced computer vision, it provides a seamless, touch-free check-in experience. Built with performance and user experience in mind, it combines robust backend processing with a sleek, dark-themed interface.

![Preview](https://via.placeholder.com/800x400.png?text=Dashboard+Preview+Placeholder)
*(Add your application screenshot here)*

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **👁️ Smart Vision** | Detects and identifies faces in milliseconds with high accuracy. |
| **🎨 Modern UI/UX** | Dark-themed, responsive interface built with PySide6 for optimal readability. |
| **📊 Live Analytics** | Real-time dashboard usage stats, daily check-ins, and late arrivals. |
| **🎙️ Voice Interaction** | Natural CLI-based Text-to-Speech (TTS) for personalized greetings. |
| **🔐 Admin Suite** | Secure area for managing personnel, reviewing logs, and exporting data. |
| **⚙️ Custom Config** | Adjustable camera settings, API endpoints, and device IDs. |

---

## 📦 Installation Guide (For Users)

Get started in 3 simple steps:

1.  **Download**
    Click the button below to get accompanying installer from our Releases page:
    <br>
    <a href="https://github.com/eLsann/App-Desktop/releases/latest">
      <img src="https://img.shields.io/badge/Download_v1.0.0-2563EB?style=for-the-badge&logo=windows&logoColor=white" height="45">
    </a>

2.  **Install**
    *   Run `AbsensiDesktop_Setup.exe`.
    *   Follow the setup wizard.
    *   (Optional) If Windows SmartScreen appears, click **More info** > **Run anyway**.

3.  **Launch**
    *   Open **Absensi Desktop** from your Desktop shortcut.
    *   Enjoy seamless attendance!

---

## 🛠️ Developer Setup

If you want to contribute or build from source, follow these steps:

### Prerequisites
*   Python 3.10+
*   Git

### 1. Clone Repository
```bash
git clone https://github.com/eLsann/App-Desktop.git
cd App-Desktop
```

### 2. Virtual Environment
```bash
python -m venv app.venv
# Activate:
# Windows:
app.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Rename `.env.example` to `.env` and configure your settings:
```ini
API_BASE=http://localhost:8000
DEVICE_ID=my-device-01
CAM_INDEX=0
```

### 5. Run
```bash
python app.py
```

---

## 🧩 Technology Stack

*   **Core**: Python 3.10
*   **GUI Framework**: PySide6 (Qt)
*   **Computer Vision**: OpenCV, MediaPipe
*   **Networking**: Requests (REST API)
*   **Distribution**: PyInstaller, Inno Setup 6

---

<div align="center">

**Developed with ❤️ by eLsann**
<br>
&copy; 2026 All Rights Reserved.

</div>
