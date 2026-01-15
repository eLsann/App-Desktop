"""
Absensi Desktop App - Main Application
Modern face attendance kiosk with admin dashboard
"""
import os
import time
import threading
import cv2
from dotenv import load_dotenv

from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap

from ui import MainUI
from camera import CameraFaceCropper
from api_client import ApiClient
from tts_engine import TTSEngine, TTSConfig
from logger_config import get_logger

logger = get_logger("app")


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
        self.device_token = os.getenv("DEVICE_TOKEN", "")
        self.cam_index = int(os.getenv("CAM_INDEX", "0"))
        self.request_interval = float(os.getenv("REQUEST_INTERVAL", "1.5"))
        
        voice = os.getenv("EDGE_VOICE", "id-ID-GadisNeural")
        max_fps = int(os.getenv("MAX_FPS", "30"))
        api_timeout = float(os.getenv("API_TIMEOUT", "15"))
        
        logger.info(f"Config: API={self.api_base}, Device={self.device_id}")
        
        # Initialize components
        self.ui = MainUI()
        self.cam = CameraFaceCropper(self.cam_index)
        self.client = ApiClient(self.api_base, self.device_id, self.device_token, timeout=api_timeout)
        self.tts = TTSEngine(TTSConfig(edge_voice=voice))
        
        # State
        self.running = False
        self.last_sent = 0.0
        self._request_inflight = False
        self._lock = threading.Lock()
        
        # Thread-safe result queue
        import queue
        self._result_queue = queue.Queue()
        
        # Local face cooldown tracking (prevent repeated API calls for same face)
        self._face_cooldowns = {}  # {name: last_recognized_time}
        self.FACE_COOLDOWN_SECONDS = 10  # Skip same face for 30 seconds
        
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
        
        # Update UI with config
        self.ui.api_url.setText(self.api_base)
        self.ui.device_id.setText(self.device_id)
        
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
        self.ui.btn_refresh_stats.clicked.connect(self.refresh_stats)
        
        logger.debug("Signals connected")
    
    def toggle_scan(self):
        """Toggle scanning mode"""
        self.running = not self.running
        if self.running:
            self.ui.btn_toggle.setText("⏸ Stop Scan")
            self.ui.btn_quick_scan.setText("⏸ Stop Scan")
            self.ui.scan_status.setText("Status: Scanning...")
            self.ui.btn_toggle.setStyleSheet("background: #EF4444;")
        else:
            self.ui.btn_toggle.setText("▶ Mulai Scan")
            self.ui.btn_quick_scan.setText("▶ Mulai Scan")
            self.ui.scan_status.setText("Status: Idle")
            self.ui.btn_toggle.setStyleSheet("background: #10B981;")
            self.ui.set_badge("—", "idle")
    
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
        """Main camera tick"""
        try:
            frame = self.cam.read_frame()
            if frame is None:
                return
            
            # Face detection and draw box
            crop, box = self.cam.find_face_crop(frame)
            if box:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Display frame
            pix = bgr_to_qpixmap(frame)
            if pix:
                self.ui.video.setPixmap(
                    pix.scaled(self.ui.video.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
            
            if not self.running:
                return
            
            if crop is None:
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
            
            # Encode and send
            jpg = self.cam.encode_jpg(crop, quality=80)
            if jpg:
                threading.Thread(target=self._recognize, args=(jpg,), daemon=True).start()
            else:
                with self._lock:
                    self._request_inflight = False
                    
        except Exception as e:
            logger.error(f"Tick error: {e}")
    
    def _recognize(self, jpg_bytes):
        """Background recognition thread - sends face to API"""
        try:
            result = self.client.recognize(jpg_bytes)
            self._result_queue.put(("result", result))
        except Exception as e:
            logger.error(f"Recognition error: {e}")
            self._result_queue.put(("error", str(e)))
        finally:
            with self._lock:
                self._request_inflight = False
    
    def _process_result_queue(self):
        """Process results from queue in main thread"""
        try:
            while not self._result_queue.empty():
                msg_type, data = self._result_queue.get_nowait()
                if msg_type == "result":
                    self._handle_result(data)
                elif msg_type == "error":
                    self._handle_error(data)
        except Exception as e:
            logger.error(f"Queue processing error: {e}")
    
    def _handle_result(self, data):
        """Handle recognition result - update UI, stats, and TTS"""
        status = data.get("status", "unknown")
        name = data.get("name", "")
        event_type = data.get("event_type", "")
        late = data.get("late", False)
        audio_text = data.get("audio_text", "")
        
        # Skip cooldown/duplicate status entirely (no UI update, no history, no TTS)
        if status in ("cooldown", "duplicate"):
            # Just update badge briefly, no history or TTS
            self.ui.set_badge(name or "—", "cooldown")
            return
        
        logger.info(f"Recognition: {name or 'Unknown'} - {status} ({event_type})")
        
        # Track local cooldown for this face
        if name and status == "ok":
            self._face_cooldowns[name] = time.time()
        
        # Update badge
        display = name if name else status
        badge_status = "late" if late else status
        self.ui.set_badge(display, badge_status)
        
        # Update history (only for meaningful events)
        ts = time.strftime("%H:%M:%S")
        event_info = f" ({event_type})" if event_type else ""
        late_info = " [Late]" if late else ""
        history = f"[{ts}] {name or 'Unknown'} - {status}{event_info}{late_info}"
        self.ui.push_history(history)
        
        # Update stats
        if status == "ok":
            if event_type == "IN":
                self.stats["checkin"] += 1
                if late:
                    self.stats["late"] += 1
            elif event_type == "OUT":
                self.stats["checkout"] += 1
        elif status == "unknown":
            self.stats["unknown"] += 1
        
        self._update_stat_cards()
        
        # TTS feedback for successful recognition
        if audio_text and status == "ok":
            key = f"{name}_{status}_{event_type}"
            self.tts.speak_once(key, audio_text)
    
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
        self.ui.stat_unknown.set_value(str(self.stats["unknown"]))
    
    def refresh_stats(self):
        """Refresh stats (reset for demo)"""
        self.stats = {"checkin": 0, "checkout": 0, "late": 0, "unknown": 0}
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
                
                # Reset local stats
                self.stats = {"checkin": 0, "checkout": 0, "late": 0, "unknown": 0}
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
        """Admin login"""
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
                self.ui.info("Login", "Login berhasil!")
                logger.info(f"Admin login: {username}")
        except Exception as e:
            self.ui.error("Login", str(e))
    
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
    
    def enroll_person(self):
        """Enroll face dataset for selected person"""
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
