<p align="center">
  <img src="assets/logo.png" width="100" alt="Absensi Desktop Logo">
</p>

# Absensi Desktop

<p align="center">
  <strong>Sistem Absensi Kiosk Wajah Cerdas & Interaktif</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/release/eLsann/App-Desktop?style=for-the-badge&color=2563EB" alt="Release">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/Production-Ready-success?style=for-the-badge&logo=windows" alt="Status">
</p>

---

## ✨ Overview
**Absensi Desktop** adalah aplikasi kiosk modern yang dirancang untuk pencatatan kehadiran berbasis pengenalan wajah (*face recognition*). Dibangun dengan teknologi komputer visi terkini, aplikasi ini menawarkan pengalaman absensi yang cepat, akurat, dan futuristik.

Cocok untuk: **Kampus**, **Kantor**, dan **Event**.

---

## ⚡ Key Features

| Fitur Pro | Keunggulan |
|-----------|------------|
| 🧠 **AI Face Recognition** | Deteksi wajah presisi dengan bounding box & scanning animation. |
| 👥 **Multi-Face Support** | Mendeteksi hingga **5 orang sekaligus** dalam satu frame. |
| 🗣️ **Natural TTS** | Sapaan suara Indonesia yang natural (via Edge TTS). |
| 📊 **Real-Time Stats** | Dashboard analitik langsung untuk memantau kehadiran harian. |
| 🔌 **Offline First** | Tetap berfungsi tanpa internet (data disinkronisasi otomatis saat online). |
| 🎨 **Modern UI/UX** | Antarmuka *Dark Mode* yang bersih, responsif, dan profesional. |

---

## 📥 Installation

### Cara Mudah (Pengguna Umum)
Tidak perlu coding! Cukup download installer resmi kami:

1.  Kunjungi halaman **[Releases](../../releases)**.
2.  Download file **`AbsensiDesktop_Setup.exe`** terbaru.
3.  Install dan jalankan aplikasi.

### Cara Developer (Source Code)
Jika Anda ingin mengembangkan atau memodifikasi kode:

```bash
# 1. Clone Repository
git clone https://github.com/eLsann/App-Desktop.git
cd "Absensi Desktop"

# 2. Setup Virtual Environment
python -m venv app.venv
.\app.venv\Scripts\activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Config
copy .env.example .env
# (Isi DEVICE_TOKEN di file .env)

# 5. Run
python app.py
```

---

## 🖥️ User Interface

### Status Indikator
Aplikasi menggunakan kode warna visual yang intuitif pada bounding box kamera:

*   ⚪ **Putih**: *Scanning* (Mencari wajah)
*   🟡 **Kuning**: *Verifying* (Memverifikasi dengan server)
*   🟢 **Hijau**: *Verified* (Absensi berhasil)
*   🔴 **Merah**: *Unknown* (Wajah tidak terdaftar)

---

## 🛠️ Configuration (.env)

| Variable | Fungsi | Default |
|----------|--------|---------|
| `API_BASE` | URL Backend API | `http://localhost:8000` |
| `DEVICE_ID` | ID Unik Perangkat Kiosk | `stb-01` |
| `DEVICE_TOKEN` | Token Keamanan (**Wajib**) | - |
| `CAM_INDEX` | Indeks Kamera (0, 1, 2...) | `0` |
| `EDGE_VOICE` | Model Suara TTS | `id-ID-GadisNeural` |

---

## 🤝 Contribution
Project ini dikembangkan oleh **eLsann** untuk **Politeknik Baja Tegal**.
Pull requests are welcome!

<p align="center">
  <sub>Built with ❤️ using Python & PySide6</sub>
</p>
