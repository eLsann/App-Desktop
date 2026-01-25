# Absensi Desktop

<div align="center">

[![Release](https://img.shields.io/github/v/release/eLsann/App-Desktop?style=for-the-badge&color=2563EB&label=Stable%20Release)](https://github.com/eLsann/App-Desktop/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)](https://github.com/eLsann/App-Desktop/releases)
[![Python](https://img.shields.io/badge/Python-3.10-EF4444?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

**Intelligent Face Recognition Attendance System**
<br>
*Fast. Secure. Seamless.*

[📥 **Download for Windows**](https://github.com/eLsann/App-Desktop/releases/latest)
·
[🐛 **Report Bug**](https://github.com/eLsann/App-Desktop/issues)

</div>

---

## Overview

**Absensi Desktop** reinvents attendance tracking by combining advanced computer vision with a modern, frictionless user experience. Designed for efficiency, it allows users to check in simply by looking at the camera—no touching, no cards, no hassle.

---

## Key Features

<table>
  <tr>
    <td align="center" width="33%">
      <h1>👁️</h1>
      <h3>Smart Vision</h3>
      <p>High-speed face detection and recognition powered by OpenCV.</p>
    </td>
    <td align="center" width="33%">
      <h1>🎨</h1>
      <h3>Modern UX</h3>
      <p>Beautiful dark-themed interface built with PySide6 (Qt).</p>
    </td>
    <td align="center" width="33%">
      <h1>📊</h1>
      <h3>Live Stats</h3>
      <p>Real-time analytics dashboard for daily attendance metrics.</p>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <h1>🎙️</h1>
      <h3>Voice AI</h3>
      <p>Interactive Text-to-Speech greetings for a personal touch.</p>
    </td>
    <td align="center" width="33%">
      <h1>🔐</h1>
      <h3>Secure Admin</h3>
      <p>Protected area for user management and data export.</p>
    </td>
    <td align="center" width="33%">
      <h1>⚙️</h1>
      <h3>Flexible</h3>
      <p>Customizable settings for cameras, APIs, and device identity.</p>
    </td>
  </tr>
</table>

---

## Technology Stack

We use industry-standard technologies to ensure reliability and performance:

<div align="center">

| Core | GUI | Vision | Tools |
| :---: | :---: | :---: | :---: |
| ![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white) | ![Qt](https://img.shields.io/badge/Qt-PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white) | ![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white) | ![Git](https://img.shields.io/badge/Git-Versioning-F05032?style=for-the-badge&logo=git&logoColor=white) |

</div>

---

## Installation Guide

<details open>
<summary><b>🔥 Quick Install (Recommended)</b></summary>

1.  **Download**
    <br>
    <a href="https://github.com/eLsann/App-Desktop/releases/latest">
      <img src="https://img.shields.io/badge/Download_Installer-v1.0.1-2563EB?style=for-the-badge&logo=windows&logoColor=white" height="50">
    </a>

2.  **Install**
    Double-click `AbsensiDesktop_Setup.exe` and follow the wizard.

3.  **Configure (Wajib)**
    Saat pertama kali diinstall, aplikasi belum memiliki akses ke server.
    *   Buka folder instalasi (biasanya di `AppData\Local\Programs\Absensi Desktop` atau lokasi yang Anda pilih).
    *   Cari file bernama `.env` (jika tidak terlihat, aktifkan "Hidden Items" di View Explorer).
    *   Buka file `.env` dengan Notepad.
    *   Ubah bagian berikut:
        ```ini
        DEVICE_ID=nama-perangkat-anda
        DEVICE_TOKEN=token-rahasia-dari-admin
        ```
    *   Simpan file.

4.  **Run**
    Buka **Absensi Desktop** dari start menu. Jika konfigurasi benar, status akan berubah menjadi **Online**.

</details>

<details>
<summary><b>🛠️ Developer Setup (Build from Source)</b></summary>

Prerequisites: Python 3.10+, Git.

```bash
# 1. Clone Repository
git clone https://github.com/eLsann/App-Desktop.git
cd App-Desktop

# 2. Setup Environment
python -m venv app.venv
app.venv\Scripts\activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your API details

# 5. Run Application
python app.py
```
</details>

<details>
<summary><b>⁉️ Troubleshooting</b></summary>

**Q: Aplikasi error "401 Unauthorized" di logs?**
A: Ini berarti **DEVICE_TOKEN** Anda salah atau belum diisi. Ikuti langkah ke-3 di "Quick Install" di atas untuk memperbaikinya.

**Q: Wajah tidak terdeteksi?**
A: Pastikan pencahayaan cukup dan wajah menghadap kamera. Coba restart aplikasi jika kamera tidak muncul.

**Q: Kamera terbalik (Mirror)?**
A: Gunakan tombol "🔄" di header aplikasi untuk membalikkan tampilan kamera.

</details>

---

<div align="center">

**Developed with by eLsann**
<br>
&copy; 2026 All Rights Reserved.

</div>
