"""
Absensi Desktop App - Main Application
Modern face attendance kiosk with admin dashboard
"""
import os
import time
import threading
import cv2
import queue
from dotenv import load_dotenv

from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap, QIcon
import sys

from ui import MainUI
from camera import CameraFaceCropper
from api_client import ApiClient
from tts_engine import TTSEngine, TTSConfig
from logger_config import get_logger
from settings_dialog import SettingsDialog

logger = get_logger("app")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller onefile
        base_path = sys._MEIPASS
    except Exception:
        # PyInstaller onedir or Dev
        base_path = os.path.abspath(".")
        
        # Check for _internal folder (PyInstaller 6+ onedir default)
        internal_path = os.path.join(base_path, "_internal")
        if os.path.exists(internal_path):
            base_path = internal_path

    return os.path.join(base_path, relative_path)


def bgr_to_qpixmap(frame_bgr):
    """Convert BGR frame to QPixmap"""
    if frame_bgr is None:
        return None
    try:
        h, w, ch = frame_bgr.shape
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        return QPixmap.fromImage(img)
    except Exception as e:
        logger.error(f"Frame conversion error: {e}")
        return None


class DesktopApp:
    """Main application controller"""
    
    def __init__(self):
        logger.info("Starting Absensi Desktop App")
        load_dotenv()
        
        # Load config
        self.api_base = os.getenv("API_BASE", "http://localhost:8000")
        self.device_id = os.getenv("DEVICE_ID", "stb-01")
        if self.device_id == "YOUR_DEVICE_ID":
             self.device_id = "stb-01"

        self.device_token = os.getenv("DEVICE_TOKEN") or "87654321"
        self.cam_index = int(os.getenv("CAM_INDEX", "0"))
        self.request_interval = float(os.getenv("REQUEST_INTERVAL", "1.5"))
        
        voice = os.getenv("EDGE_VOICE", "id-ID-GadisNeural")
        max_fps = int(os.getenv("MAX_FPS", "30"))
        api_timeout = float(os.getenv("API_TIMEOUT", "15"))
        
        logger.info(f"Config: API={self.api_base}, Device={self.device_id}, Token={self.device_token[:4]}***")
        
        # Initialize components

        self.ui = MainUI()
        
        # Set App Icon
        icon_path = resource_path("assets/icon.ico")
        if os.path.exists(icon_path):
            self.ui.setWindowIcon(QIcon(icon_path))
        
        self.cam = CameraFaceCropper(self.cam_index) # Initialize camera once, but don't open yet
        self.client = ApiClient(self.api_base, self.device_id, self.device_token, timeout=api_timeout)
        self.tts = TTSEngine(TTSConfig(edge_voice=voice))
        
        # State
        self.running = False
        self.camera_active = False
        self.last_sent = 0.0
        self._request_inflight = False
        self._lock = threading.Lock()
        self._scan_line_offset = 0  # For animated scanning line
        
        # Thread-safe result queue

        self._result_queue = queue.Queue()
        

        
        # Multi-face pending greeting (collect faces, trigger after 1.5s of no new faces)
        self._last_faces = {}     # Stores last recognition result per queue_id
        self._pending_faces = []  # Collected recognized faces
        self._last_face_time = 0.0

        self._greeting_triggered = False
        self.GREETING_DELAY = 1.5  # seconds
        
        # Stats
        self.stats = {"checkin": 0, "checkout": 0, "late": 0, "unknown": 0}
        
        # Connect signals
        self._connect_signals()
        
        # Camera timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000 // max_fps)
        
        # Result processing timer (check every 100ms)
        self.result_timer = QTimer()
        self.result_timer.timeout.connect(self._process_result_queue)
        self.result_timer.start(100)
        
        # Greeting delay timer (check every 500ms)
        self.greeting_timer = QTimer()
        self.greeting_timer.timeout.connect(self._check_greeting_delay)
        self.greeting_timer.start(500)
        
        # Update UI with config
        self.ui.api_url.setText(self.api_base)
        self.ui.device_id.setText(self.device_id)
        
        # Offline Queue Sync (every 60 sec)
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self._sync_offline_queue)
        self.sync_timer.start(60000)
        
        # Connection health check (every 10 sec when offline, 30 sec when online)
        self._health_check_interval = 10000  # Start with 10 sec
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self._check_connection_health)
        self.health_timer.start(self._health_check_interval)
        
        logger.info("App initialized successfully")
    
    def _connect_signals(self):
        """Connect UI signals to handlers"""
        # Kiosk
        self.ui.btn_toggle.clicked.connect(self.toggle_scan)
        self.ui.btn_quick_scan.clicked.connect(self.toggle_scan)
        self.ui.btn_mirror.clicked.connect(self.toggle_mirror)
        self.ui.btn_flip_camera.clicked.connect(self.flip_camera)
        
        # Admin
        self.ui.btn_login.clicked.connect(self.do_login)
        self.ui.btn_people_refresh.clicked.connect(self.load_people)
        self.ui.btn_people_add.clicked.connect(self.add_person)
        self.ui.btn_people_delete.clicked.connect(self.delete_person)
        self.ui.btn_capture_enroll.clicked.connect(self.capture_enroll)
        self.ui.btn_enroll.clicked.connect(self.enroll_person)
        self.ui.btn_rebuild_cache.clicked.connect(self.rebuild_cache)
        
        # Events
        self.ui.btn_ev_load.clicked.connect(self.load_events)
        self.ui.btn_correct.clicked.connect(self.correct_event)
        
        # Dashboard
        self.ui.btn_reset_attendance.clicked.connect(self.reset_attendance)
        
        # Reports
        self.ui.btn_report.clicked.connect(self.load_report)
        self.ui.btn_export_csv.clicked.connect(self.export_csv)
        
        # Settings
        self.ui.btn_settings.clicked.connect(self.open_settings)
        self.ui.btn_refresh_stats.clicked.connect(self.refresh_stats)
        
        logger.debug("Signals connected")
    
    def toggle_scan(self):
        """Toggle scanning mode - controls camera on/off"""
        self.running = not self.running
        if self.running:
            # Start camera if not active
            if not self.camera_active:
                if self.cam is None:
                    self.cam = CameraFaceCropper(self.cam_index)
                
                try:
                    self.cam.open(self.cam_index)
                    self.camera_active = True
                    logger.info("Camera started")
                except Exception as e:
                    self.ui.error("Camera", f"Gagal membuka kamera: {e}")
                    self.running = False
                    self.ui.btn_toggle.setChecked(False)
                    return
            
            self.ui.btn_toggle.setText("⏸ Stop")
            self.ui.btn_quick_scan.setText("⏸ Stop")
            self.ui.scan_status.setText("Scanning...")
            self.ui.btn_toggle.setStyleSheet("background: #EF4444;")
        else:
            # Stop camera to free resource
            if self.camera_active and self.cam:
                self.cam.release()
                self.camera_active = False
                logger.info("Camera stopped")
            
            self.ui.btn_toggle.setText("▶ Mulai")
            self.ui.btn_quick_scan.setText("▶ Mulai")
            self.ui.scan_status.setText("Siap")
            self.ui.btn_toggle.setStyleSheet("background: #10B981;")
            self.ui.set_badge("Silakan absen...", "idle")
            self.ui.video.setText("📷 Klik Mulai untuk scan")
    
    def toggle_mirror(self):
        """Toggle camera mirror mode"""
        new_mode = self.cam.toggle_mirror()
        self.ui.update_mirror_button(new_mode)
    
    def flip_camera(self):
        """Switch to next camera"""
        try:
            next_cam = self.cam.flip_next()
            self.ui.info("Kamera", f"Beralih ke Camera {next_cam}")
        except Exception as e:
            self.ui.error("Kamera", str(e))
    
    def tick(self):
        """Main camera tick - multi-face detection"""
        if not self.camera_active or self.cam is None:
            return
        
        try:
            frame = self.cam.read_frame()
            if frame is None:
                return
            
            # Multi-face detection
            faces = self.cam.find_all_faces(frame, max_faces=5)
            
            # Update scan line animation
            self._scan_line_offset = (self._scan_line_offset + 4) % 100
            
            # STATUS COLORS (BGR format)
            COLOR_SCANNING = (255, 255, 255)  # White - scanning/no match yet
            COLOR_VERIFYING = (0, 255, 255)   # Yellow - API request in flight
            COLOR_RECOGNIZED = (0, 255, 0)    # Green - recognized
            COLOR_UNKNOWN = (0, 0, 255)       # Red - unknown face
            
            # Draw bounding boxes with stored recognition results
            for face in faces:
                x1, y1, x2, y2 = face["bbox"]
                queue_id = face["queue_id"]
                box_h = y2 - y1
                
                # Determine status and color
                label = f"[{queue_id}] Scanning..."
                color = COLOR_SCANNING
                status = "scanning"
                
                # Check if API is processing
                if self._request_inflight:
                    label = f"[{queue_id}] Verifying..."
                    color = COLOR_VERIFYING
                    status = "verifying"
                
                # Check cached recognition results
                if hasattr(self, '_last_faces') and queue_id in self._last_faces:
                    cached = self._last_faces.get(queue_id, {})
                    if cached.get("name"):
                        label = f"[{queue_id}] {cached['name']}"
                        color = COLOR_RECOGNIZED
                        status = "recognized"
                    elif cached.get("status") == "unknown":
                        label = f"[{queue_id}] Unknown"
                        color = COLOR_UNKNOWN
                        status = "unknown"
                
                # Draw main bounding box (3px thick for visibility)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                
                # Draw corner accents for modern look
                corner_len = 15
                # Top-left
                cv2.line(frame, (x1, y1), (x1 + corner_len, y1), color, 4)
                cv2.line(frame, (x1, y1), (x1, y1 + corner_len), color, 4)
                # Top-right
                cv2.line(frame, (x2, y1), (x2 - corner_len, y1), color, 4)
                cv2.line(frame, (x2, y1), (x2, y1 + corner_len), color, 4)
                # Bottom-left
                cv2.line(frame, (x1, y2), (x1 + corner_len, y2), color, 4)
                cv2.line(frame, (x1, y2), (x1, y2 - corner_len), color, 4)
                # Bottom-right
                cv2.line(frame, (x2, y2), (x2 - corner_len, y2), color, 4)
                cv2.line(frame, (x2, y2), (x2, y2 - corner_len), color, 4)
                
                # Animated scan line (only for scanning/verifying states)
                if status in ["scanning", "verifying"]:
                    scan_y = y1 + int((self._scan_line_offset / 100.0) * box_h)
                    scan_y = max(y1 + 2, min(y2 - 2, scan_y))
                    cv2.line(frame, (x1 + 3, scan_y), (x2 - 3, scan_y), color, 2)
                
                # Draw label background with padding
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.55
                thickness = 2
                (tw, th), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                label_y = y1 - 8 if y1 > 30 else y2 + th + 8
                cv2.rectangle(frame, (x1, label_y - th - 4), (x1 + tw + 8, label_y + 4), color, -1)
                cv2.putText(frame, label, (x1 + 4, label_y), font, font_scale, (0, 0, 0), thickness)
            
            # Display frame
            pix = bgr_to_qpixmap(frame)
            if pix:
                self.ui.video.setPixmap(
                    pix.scaled(self.ui.video.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
            
            if not self.running:
                return
            
            if not faces:
                self.ui.set_badge("Tidak ada wajah", "idle")
                return
            
            # Rate limiting
            now = time.time()
            with self._lock:
                if (now - self.last_sent) < self.request_interval:
                    return
                if self._request_inflight:
                    return
                self.last_sent = now
                self._request_inflight = True
            
            # Encode for API: Resize large images to max 800px width for speed
            h, w = frame.shape[:2]
            upload_frame = frame
            if w > 800:
                scale = 800 / w
                new_h = int(h * scale)
                upload_frame = cv2.resize(frame, (800, new_h), interpolation=cv2.INTER_AREA)
            
            jpg = self.cam.encode_jpg(upload_frame, quality=85)
            if jpg:
                threading.Thread(target=self._recognize_multi, args=(jpg,), daemon=True).start()
            else:
                with self._lock:
                    self._request_inflight = False
                    
        except Exception as e:
            logger.error(f"Tick error: {e}")
    
    def _recognize_multi(self, jpg_bytes):
        """Background multi-face recognition thread"""
        try:
            result = self.client.recognize_multi(jpg_bytes)
            self._result_queue.put(("result_multi", result))
        except Exception as e:
            logger.error(f"Multi-face recognition error: {e}")
            self._result_queue.put(("error", str(e)))
        finally:
            with self._lock:
                self._request_inflight = False
    

    
    def _process_result_queue(self):
        """Process results from queue in main thread"""
        try:
            while not self._result_queue.empty():
                msg_type, data = self._result_queue.get_nowait()
                if msg_type == "result_multi":
                    self._handle_multi_result(data)
                elif msg_type == "error":
                    self._handle_error(data)
                elif msg_type == "connection_status":
                    self._handle_connection_status(data)
        except Exception as e:
            logger.error(f"Queue processing error: {e}")
    
    def _handle_connection_status(self, data: dict):
        """Update UI to show connection status (called from main thread)"""
        status = data.get("status", "offline")
        interval = data.get("interval", 10000)
        
        # Update UI label
        if status == "offline":
            self.ui.lbl_status.setText("⚠️ Offline")
            self.ui.lbl_status.setStyleSheet("color: #F59E0B; font-weight: bold;")
        else:
            self.ui.lbl_status.setText("✓ Online")
            self.ui.lbl_status.setStyleSheet("color: #10B981; font-weight: bold;")
        
        # Update timer interval from main thread (thread-safe)
        if self._health_check_interval != interval:
            self._health_check_interval = interval
            self.health_timer.setInterval(interval)
    
    def _handle_multi_result(self, data):
        """Handle multi-face recognition result - collect faces for delayed greeting"""
        faces = data.get("faces", [])
        recognized_names = data.get("recognized_names", [])
        combined_audio = data.get("combined_audio", "")
        
        # Store faces for bounding box labels
        self._last_faces = {}
        for face in faces:
            self._last_faces[face.get("queue_id", 0)] = {
                "name": face.get("name"),
                "status": face.get("status")
            }
        
        if not recognized_names:
            logger.info("Multi-face: no recognized faces")
            return
        
        # Collect faces for delayed greeting
        self._last_face_time = time.time()
        self._greeting_triggered = False
        
        # Add new faces to pending (avoid duplicates)
        for face in faces:
            if face.get("name") and face.get("status") == "ok":
                name = face["name"]
                # Check if already in pending
                if not any(p["name"] == name for p in self._pending_faces):
                    self._pending_faces.append({
                        "name": name,
                        "event_type": face.get("event_type", ""),
                        "late": face.get("late", False)
                    })
        
        # Update kiosk display immediately
        all_names = [p["name"] for p in self._pending_faces]
        names_str = ", ".join(all_names)
        self.ui.badge.setText(f"✓ {names_str}")
        self.ui.badge.setStyleSheet("""
            font-size: 22px; font-weight: 700; 
            color: #10B981; padding: 10px;
        """)
        
        # Update greeting message (waiting for more faces)
        self.ui.greeting_msg.setText(f"Menunggu wajah lainnya... ({len(all_names)} terdeteksi)")
        
        logger.info(f"Multi-face: collected {len(self._pending_faces)} faces, waiting...")
    
    def _check_greeting_delay(self):
        """Check if 3 seconds passed without new faces - trigger greeting"""
        if not self._pending_faces or self._greeting_triggered:
            return
        
        now = time.time()
        if (now - self._last_face_time) >= self.GREETING_DELAY:
            self._trigger_combined_greeting()
    
    def _trigger_combined_greeting(self):
        """Trigger the combined greeting after delay"""
        if not self._pending_faces or self._greeting_triggered:
            return
        
        self._greeting_triggered = True
        pending = self._pending_faces.copy()
        self._pending_faces = []
        
        # Generate greeting message
        names = [p["name"] for p in pending]
        
        # Natural naming (A, B, dan C)
        if len(names) == 1:
            names_str = names[0]
            sapaan_nama = f"Halo {names[0]}"
        elif len(names) == 2:
            names_str = f"{names[0]} dan {names[1]}"
            sapaan_nama = f"Halo {names[0]} dan {names[1]}"
        else:
            # > 2 names: A, B, dan C
            names_str = ", ".join(names[:-1]) + ", dan " + names[-1]
            sapaan_nama = f"Halo semuanya" # Shorten for many people to avoid robotic listing
        
        # Check event types
        has_late = any(p.get("late") for p in pending)
        has_out = any(p.get("event_type") == "OUT" for p in pending)
        
        hour = int(time.strftime("%H"))
        if hour < 10:
            waktu = "pagi"
        elif hour < 15:
            waktu = "siang"
        elif hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        # Natural conversational phrasing
        if has_out:
            combined_audio = f"Terima kasih {names_str}. Hati-hati di jalan, sampai jumpa besok!"
        elif has_late:
            combined_audio = f"Selamat {waktu} {names_str}. Absensi masuk sudah tercatat, tapi jangan terlambat lagi ya."
        else:
            combined_audio = f"Selamat {waktu} {names_str}. Absensi berhasil. Selamat beraktivitas!"
        
        # Update UI
        self.ui.badge.setText(f"✓ {names_str}")
        self.ui.animate_greeting(combined_audio)
        
        # Log to admin dashboard
        ts = time.strftime("%H:%M:%S")
        for p in pending:
            event_type = p.get("event_type", "")
            late = p.get("late", False)
            event_info = f" ({event_type})" if event_type else ""
            late_info = " [Terlambat]" if late else ""
            log_entry = f"[{ts}] {p['name']} - ok{event_info}{late_info}"
            self.ui.activity_list.insertItem(0, log_entry)
        
        # Keep activity list to 50 items
        while self.ui.activity_list.count() > 50:
            self.ui.activity_list.takeItem(self.ui.activity_list.count() - 1)
        
        # Update stats
        for p in pending:
            event_type = p.get("event_type", "")
            late = p.get("late", False)
            if event_type == "IN":
                self.stats["checkin"] += 1
                if late:
                    self.stats["late"] += 1
            elif event_type == "OUT":
                self.stats["checkout"] += 1
        self._update_stat_cards()
        
        # TTS - use speak_once with cooldown
        if self.tts:
            try:
                self.tts.speak_once("combined", combined_audio, cooldown=5.0)
            except Exception as e:
                logger.error(f"TTS error: {e}")
        
        logger.info(f"Combined greeting triggered: {names}")
    

    
    def _handle_error(self, error_msg):
        """Handle recognition error"""
        self.ui.set_badge("Error", "error")
        ts = time.strftime("%H:%M:%S")
        self.ui.push_history(f"[{ts}] Error: {error_msg}")
    
    def _update_stat_cards(self):
        """Update dashboard stat cards"""
        self.ui.stat_checkin.set_value(str(self.stats["checkin"]))
        self.ui.stat_checkout.set_value(str(self.stats["checkout"]))
        self.ui.stat_late.set_value(str(self.stats["late"]))
        self.ui.stat_total.set_value(str(self.stats.get("total_registered", 0)))
    
    def refresh_stats(self):
        """Refresh stats and get total registered from API"""
        self.stats = {"checkin": 0, "checkout": 0, "late": 0, "total_registered": 0}
        # Try to get total registered from API
        try:
            if self.client.admin_token:
                persons = self.client.admin_list_persons()
                self.stats["total_registered"] = len(persons)
        except Exception:
            pass
        self._update_stat_cards()
        self.ui.info("Stats", "Stats direset")
    
    def reset_attendance(self):
        """Reset all attendance data (API + local)"""
        if not self._ensure_admin():
            return
        
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self.ui, "Konfirmasi Reset",
            "Apakah Anda yakin ingin menghapus SEMUA data absensi?\n\nTindakan ini tidak dapat dibatalkan!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.client.admin_reset_attendance()
                events = result.get("events_deleted", 0)
                daily = result.get("daily_deleted", 0)
                
                # Reset local stats (keep total_registered)
                total = self.stats.get("total_registered", 0)
                self.stats = {"checkin": 0, "checkout": 0, "late": 0, "total_registered": total}
                self._update_stat_cards()
                
                # Clear activity list
                self.ui.activity_list.clear()
                self.ui.history.clear()
                
                self.ui.info("Reset", f"Berhasil menghapus {events} event dan {daily} record harian")
                logger.info(f"Attendance reset: {events} events, {daily} daily records")
            except Exception as e:
                self.ui.error("Reset", str(e))
    
    # Admin methods
    def _ensure_admin(self) -> bool:
        if not self.client.admin_token:
            self.ui.error("Admin", "Silakan login admin dulu")
            return False
        return True
    
    def do_login(self):
        """Admin login with auto-flow to kiosk"""
        username = self.ui.in_user.text().strip()
        password = self.ui.in_pass.text().strip()
        
        if not username or not password:
            self.ui.error("Login", "Username dan password harus diisi")
            return
        
        try:
            result = self.client.admin_login(username, password)
            if result and "access_token" in result:
                self.ui.lbl_login.setText(f"✓ Login sebagai: {username}")
                self.ui.lbl_login.setStyleSheet("color: #10B981;")
                self.ui.lbl_status.setText("● Connected")
                self.ui.lbl_status.setStyleSheet("color: #10B981;")
                logger.info(f"Admin login: {username}")
                
                # AUTO-FLOW: Load data and switch to kiosk
                self._auto_flow_after_login()
                
        except Exception as e:
            self.ui.error("Login", str(e))
    
    def _auto_flow_after_login(self):
        """Auto-flow setelah login: load data dan pindah ke kiosk"""
        try:
            # 1. Load people list
            people = self.client.admin_list_persons()
            self.ui.people_list.clear()
            for p in people:
                self.ui.people_list.addItem(f"{p['id']} | {p['name']}")
            
            # 2. Preload TTS greetings
            names = [p['name'] for p in people]
            if names and self.tts:
                logger.info(f"Preloading TTS for {len(names)} people...")
                self.tts.preload_common_greetings(names)
            
            # 3. Load today's stats
            self.refresh_stats()
            
            # 4. Switch to Kiosk tab (index 1)
            self.ui.tabs.setCurrentIndex(1)
            
            # Note: Scanning NOT started automatically - user must click button
            
            self.ui.info("Ready", f"Sistem siap dengan {len(people)} orang terdaftar")
            logger.info(f"Auto-flow complete: {len(people)} people loaded, kiosk active")
            
        except Exception as e:
            logger.error(f"Auto-flow error: {e}")
            self.ui.error("Auto-Flow", f"Gagal memuat data: {e}")
    
    def load_people(self):
        """Load people list and preload TTS greetings"""
        if not self._ensure_admin():
            return
        try:
            people = self.client.admin_list_persons()
            self.ui.people_list.clear()
            for p in people:
                self.ui.people_list.addItem(f"{p['id']} | {p['name']}")
            
            # Preload TTS greetings for all people (background thread)
            names = [p['name'] for p in people]
            if names and self.tts:
                logger.info(f"Preloading TTS for {len(names)} people...")
                self.tts.preload_common_greetings(names)
            
            self.ui.info("People", f"Loaded {len(people)} persons")
        except Exception as e:
            self.ui.error("People", str(e))
    
    def add_person(self):
        """Add new person"""
        if not self._ensure_admin():
            return
        name = self.ui.people_name.text().strip()
        if not name:
            self.ui.error("Add Person", "Nama harus diisi")
            return
        try:
            result = self.client.admin_create_person(name)
            self.ui.people_name.clear()
            self.load_people()
            self.ui.info("Add Person", f"Person '{name}' ditambahkan")
        except Exception as e:
            self.ui.error("Add Person", str(e))
    
    def delete_person(self):
        """Delete selected person"""
        if not self._ensure_admin():
            return
        item = self.ui.people_list.currentItem()
        if not item:
            self.ui.error("Delete", "Pilih person dulu")
            return
        try:
            pid = int(item.text().split("|")[0].strip())
            self.client.admin_delete_person(pid)
            self.load_people()
            self.ui.info("Delete", "Person dihapus")
        except Exception as e:
            self.ui.error("Delete", str(e))
    
    def capture_enroll(self):
        """Capture and enroll face photos via camera"""
        if not self._ensure_admin():
            return
        item = self.ui.people_list.currentItem()
        if not item:
            self.ui.error("Capture", "Pilih person dulu")
            return
        
        try:
            pid = int(item.text().split("|")[0].strip())
            name = item.text().split("|")[1].strip()
            
            # Open camera capture dialog
            from ui import CameraCaptureDialog
            dialog = CameraCaptureDialog(self.ui, person_name=name)
            
            from PySide6.QtWidgets import QDialog
            if dialog.exec() == QDialog.Accepted:
                images = dialog.get_captured_images()
                if not images:
                    self.ui.error("Capture", "Tidak ada foto yang dicapture")
                    return
                
                # Save captured images to temp files and upload
                import tempfile
                import os
                import cv2
                
                temp_files = []
                temp_dir = tempfile.mkdtemp()
                
                for i, img in enumerate(images):
                    filepath = os.path.join(temp_dir, f"capture_{i+1}.jpg")
                    cv2.imwrite(filepath, img)
                    temp_files.append(filepath)
                
                # Upload to API
                result = self.client.admin_enroll_person(pid, temp_files)
                added = result.get("embeddings_added", 0)
                
                # Cleanup temp files
                for f in temp_files:
                    try:
                        os.remove(f)
                    except:
                        pass
                try:
                    os.rmdir(temp_dir)
                except:
                    pass
                
                self.ui.info("Capture", f"Berhasil enroll {added} foto untuk {name}")
                logger.info(f"Camera enroll: {added} photos for {name} (pid={pid})")
            
        except Exception as e:
            self.ui.error("Capture", str(e))
            logger.error(f"Capture enroll error: {e}")
    
    def enroll_person(self):
        """Enroll face dataset from files for selected person"""
        if not self._ensure_admin():
            return
        item = self.ui.people_list.currentItem()
        if not item:
            self.ui.error("Enroll", "Pilih person dulu")
            return
        try:
            pid = int(item.text().split("|")[0].strip())
            name = item.text().split("|")[1].strip()
            files = self.ui.pick_images()
            if not files:
                return
            result = self.client.admin_enroll_person(pid, files)
            added = result.get("embeddings_added", 0)
            self.ui.info("Enroll", f"Enrolled {added} foto untuk {name}")
        except Exception as e:
            self.ui.error("Enroll", str(e))
    
    def rebuild_cache(self):
        """Rebuild face recognition cache"""
        if not self._ensure_admin():
            return
        try:
            self.client.admin_rebuild_cache()
            self.ui.info("Cache", "Cache rebuilt successfully")
        except Exception as e:
            self.ui.error("Cache", str(e))
    
    def load_events(self):
        """Load events log"""
        if not self._ensure_admin():
            return
        try:
            status = self.ui.ev_status.text().strip() or None
            name = self.ui.ev_name.text().strip() or None
            day = self.ui.ev_day.text().strip() or None
            limit = self.ui.ev_limit.value()
            
            events = self.client.admin_list_events(limit=limit, status=status, name=name, day=day)
            
            self.ui.ev_table.setRowCount(0)
            for ev in events:
                row = self.ui.ev_table.rowCount()
                self.ui.ev_table.insertRow(row)
                self.ui.ev_table.setItem(row, 0, QTableWidgetItem(str(ev.get("id", ""))))
                self.ui.ev_table.setItem(row, 1, QTableWidgetItem(ev.get("day", "")))
                
                # Format time to readable format (convert UTC to WIB +7)
                ts_raw = ev.get("ts", "")
                if ts_raw:
                    try:
                        from datetime import datetime, timedelta
                        # Parse datetime string (remove any trailing Z or timezone)
                        ts_clean = ts_raw.replace("Z", "").replace("+00:00", "")
                        if "T" in ts_clean:
                            ts_clean = ts_clean.split("T")[1]  # Get time part only
                        if "." in ts_clean:
                            ts_clean = ts_clean.split(".")[0]  # Remove microseconds
                        
                        # Parse as time, add 7 hours for WIB
                        parts = ts_clean.split(":")
                        hour = int(parts[0]) + 7  # UTC to WIB
                        if hour >= 24:
                            hour -= 24
                        ts_display = f"{hour:02d}:{parts[1]}:{parts[2] if len(parts) > 2 else '00'}"
                    except:
                        ts_display = ts_raw[:8]  # Fallback
                else:
                    ts_display = ""
                
                self.ui.ev_table.setItem(row, 2, QTableWidgetItem(ts_display))
                self.ui.ev_table.setItem(row, 3, QTableWidgetItem(ev.get("device_id", "") or ev.get("device", "")))
                self.ui.ev_table.setItem(row, 4, QTableWidgetItem(ev.get("final_name", "") or "-"))
                self.ui.ev_table.setItem(row, 5, QTableWidgetItem(ev.get("event_type", "") or "-"))
                self.ui.ev_table.setItem(row, 6, QTableWidgetItem(ev.get("status", "")))
                self.ui.ev_table.setItem(row, 7, QTableWidgetItem(str(round(ev.get("distance", 0) or 0, 2))))
            
            self.ui.info("Events", f"Loaded {len(events)} events")
        except Exception as e:
            self.ui.error("Events", str(e))
    
    def correct_event(self):
        """Correct event entry"""
        if not self._ensure_admin():
            return
        event_id = self.ui.c_event_id.text().strip()
        final_name = self.ui.c_final_name.text().strip()
        
        if not event_id or not final_name:
            self.ui.error("Correction", "Event ID dan nama harus diisi")
            return
        
        # TODO: Implement correction API call
        self.ui.info("Correction", "Koreksi berhasil (demo)")
    
    def load_report(self):
        """Load monthly report"""
        if not self._ensure_admin():
            return
        month = self.ui.r_month.text().strip()
        if not month:
            self.ui.error("Report", "Format bulan harus YYYY-MM")
            return
        try:
            report = self.client.admin_monthly_report(month)
            
            self.ui.report_table.setRowCount(0)
            for item in report.get("data", []):
                row = self.ui.report_table.rowCount()
                self.ui.report_table.insertRow(row)
                self.ui.report_table.setItem(row, 0, QTableWidgetItem(item.get("person_name", "")))
                self.ui.report_table.setItem(row, 1, QTableWidgetItem(str(item.get("days_present", 0))))
                self.ui.report_table.setItem(row, 2, QTableWidgetItem(str(item.get("late_count", 0))))
                self.ui.report_table.setItem(row, 3, QTableWidgetItem(str(item.get("missing_out", 0))))
            
            self.ui.info("Report", f"Report {month} loaded")
        except Exception as e:
            self.ui.error("Report", str(e))
    
    def export_csv(self):
        """Export attendance data to CSV"""
        if not self._ensure_admin():
            return
        
        month = self.ui.r_month.text().strip() or None
        
        from PySide6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self.ui, 
            "Simpan CSV", 
            f"absensi_{month or 'semua'}.csv",
            "CSV Files (*.csv)"
        )
        
        if not filename:
            return
        
        try:
            # Download CSV from API
            import requests
            headers = {"Authorization": f"Bearer {self.client.admin_token}"}
            params = {}
            if month:
                params["month"] = month
            
            response = requests.get(
                f"{self.api_base}/admin/reports/export/csv",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            # Save to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            self.ui.info("Export", f"CSV tersimpan: {filename}")
            logger.info(f"CSV exported to: {filename}")
        except Exception as e:
            self.ui.error("Export", str(e))
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # If accepted (saved), restart app to apply changes
            self.restart_app()

    def restart_app(self):
        """Restart the application"""
        import sys
        import os
        logger.info("Restarting application...")
        self.cleanup()
        # Re-execute the current process
        os.execl(sys.executable, sys.executable, *sys.argv)

    def _sync_offline_queue(self):
        """Sync offline queue in background"""
        def _sync():
            try:
                count = self.client.process_offline_queue()
                if count > 0:
                    logger.info(f"Synced {count} offline requests")
            except Exception as e:
                logger.error(f"Sync error: {e}")
                
        threading.Thread(target=_sync, daemon=True).start()
    
    def _check_connection_health(self):
        """Periodic connection health check with smart retry interval"""
        def _health_check():
            was_online = self.client.is_online
            is_online_now = self.client.check_health()
            
            # Send status and new interval to main thread via queue
            if is_online_now:
                self._result_queue.put(("connection_status", {"status": "online", "interval": 30000}))
            else:
                self._result_queue.put(("connection_status", {"status": "offline", "interval": 10000}))
            
            # Log state change
            if was_online and not is_online_now:
                logger.warning("Connection lost! API is offline.")
            elif not was_online and is_online_now:
                logger.info("Connection restored! API is back online.")
        
        threading.Thread(target=_health_check, daemon=True).start()

    def cleanup(self):
        """Cleanup resources"""
        self.timer.stop()
        self.cam.release()
        self.tts.cleanup()
        logger.info("App cleanup completed")


def main():
    import sys
    logger.info("Starting application...")
    
    app = QApplication(sys.argv)
    
    try:
        desktop = DesktopApp()
        desktop.ui.show()
        logger.info("Application window displayed")
        
        result = app.exec()
        desktop.cleanup()
        logger.info("Application closed")
        sys.exit(result)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()
