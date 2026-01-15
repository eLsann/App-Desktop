from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLineEdit, QFormLayout, QMessageBox, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QFileDialog, QSpinBox, QComboBox,
    QProgressBar, QDialog, QDialogButtonBox, QGridLayout, QGroupBox,
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont

# Modern color scheme
COLORS = {
    "primary": "#3B82F6",
    "primary_hover": "#2563EB",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "bg": "#0F172A",
    "surface": "#1E293B",
    "surface_light": "#334155",
    "text": "#F1F5F9",
    "text_muted": "#94A3B8",
    "border": "#475569",
}

STYLESHEET = f"""
QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}}

QLabel {{
    background: transparent;
    color: {COLORS['text']};
}}

QLineEdit {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLORS['text']};
}}
QLineEdit:focus {{
    border-color: {COLORS['primary']};
}}

QPushButton {{
    background: {COLORS['primary']};
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    color: white;
    font-weight: 600;
}}
QPushButton:hover {{
    background: {COLORS['primary_hover']};
}}
QPushButton:disabled {{
    background: {COLORS['surface_light']};
    color: {COLORS['text_muted']};
}}

QPushButton[class="secondary"] {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
}}
QPushButton[class="secondary"]:hover {{
    background: {COLORS['surface_light']};
}}

QPushButton[class="success"] {{
    background: {COLORS['success']};
}}
QPushButton[class="danger"] {{
    background: {COLORS['error']};
}}

QListWidget {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px;
}}
QListWidget::item {{
    padding: 8px;
    border-radius: 4px;
}}
QListWidget::item:selected {{
    background: {COLORS['primary']};
}}
QListWidget::item:hover {{
    background: {COLORS['surface_light']};
}}

QTableWidget {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    gridline-color: {COLORS['border']};
}}
QTableWidget::item {{
    padding: 8px;
}}
QHeaderView::section {{
    background: {COLORS['surface_light']};
    padding: 10px;
    border: none;
    font-weight: 600;
}}

QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    background: {COLORS['bg']};
}}
QTabBar::tab {{
    background: {COLORS['surface']};
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}
QTabBar::tab:selected {{
    background: {COLORS['primary']};
}}
QTabBar::tab:hover:!selected {{
    background: {COLORS['surface_light']};
}}

QGroupBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}}

QSpinBox {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px;
}}

QScrollBar:vertical {{
    background: {COLORS['surface']};
    width: 12px;
    border-radius: 6px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['surface_light']};
    border-radius: 6px;
    min-height: 30px;
}}
"""


class StatCard(QFrame):
    """Modern stat card widget"""
    def __init__(self, title: str, value: str, icon: str = "", color: str = "primary"):
        super().__init__()
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['surface']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Title
        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {COLORS[color]}; font-size: 28px; font-weight: 700;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        self.value_label = value_label
    
    def set_value(self, value: str):
        self.value_label.setText(value)


class MainUI(QWidget):
    """Modern Desktop App UI"""
    
    # Signals
    camera_changed = Signal(int)
    mirror_toggled = Signal(bool)
    dataset_upload_requested = Signal(int, list)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Absensi Desktop - Modern Dashboard")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(STYLESHEET)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup main UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_dashboard_tab(), "🏠 Dashboard")
        self.tabs.addTab(self._create_kiosk_tab(), "📷 Kiosk")
        self.tabs.addTab(self._create_people_tab(), "👥 People")
        self.tabs.addTab(self._create_events_tab(), "📋 Events")
        self.tabs.addTab(self._create_reports_tab(), "📊 Reports")
        self.tabs.addTab(self._create_settings_tab(), "⚙️ Settings")
        
        main_layout.addWidget(self.tabs)
    
    def _create_header(self) -> QFrame:
        """Create app header"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet(f"background: {COLORS['surface']}; border-bottom: 1px solid {COLORS['border']};")
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo/Title
        title = QLabel("📊 Absensi Desktop")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        
        # Status indicator
        self.lbl_status = QLabel("● Disconnected")
        self.lbl_status.setStyleSheet(f"color: {COLORS['error']};")
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.lbl_status)
        
        return header
    
    def _create_dashboard_tab(self) -> QWidget:
        """Create dashboard tab with stats"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.stat_checkin = StatCard("Check-in Hari Ini", "0", "✓", "success")
        self.stat_checkout = StatCard("Check-out", "0", "📤", "primary")
        self.stat_late = StatCard("Terlambat", "0", "⚠", "warning")
        self.stat_unknown = StatCard("Unknown", "0", "❓", "error")
        
        stats_layout.addWidget(self.stat_checkin)
        stats_layout.addWidget(self.stat_checkout)
        stats_layout.addWidget(self.stat_late)
        stats_layout.addWidget(self.stat_unknown)
        
        # Recent activity section
        activity_group = QGroupBox("Aktivitas Terkini")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        self.activity_list.setMaximumHeight(300)
        activity_layout.addWidget(self.activity_list)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        self.btn_quick_scan = QPushButton("▶ Mulai Scan")
        self.btn_quick_scan.setMinimumWidth(150)
        
        self.btn_refresh_stats = QPushButton("🔄 Refresh Stats")
        self.btn_refresh_stats.setProperty("class", "secondary")
        
        self.btn_reset_attendance = QPushButton("🗑️ Reset Semua Absensi")
        self.btn_reset_attendance.setStyleSheet(f"background: {COLORS['error']};")
        
        actions_layout.addWidget(self.btn_quick_scan)
        actions_layout.addWidget(self.btn_refresh_stats)
        actions_layout.addWidget(self.btn_reset_attendance)
        actions_layout.addStretch()
        
        layout.addLayout(stats_layout)
        layout.addWidget(activity_group)
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        return tab
    
    def _create_kiosk_tab(self) -> QWidget:
        """Create kiosk/scan tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Left: Camera preview
        camera_frame = QFrame()
        camera_frame.setStyleSheet(f"background: {COLORS['surface']}; border-radius: 12px;")
        camera_layout = QVBoxLayout(camera_frame)
        
        self.video = QLabel("📷 Camera Preview")
        self.video.setAlignment(Qt.AlignCenter)
        self.video.setMinimumSize(640, 480)
        self.video.setStyleSheet(f"background: #000; color: {COLORS['text_muted']}; border-radius: 8px;")
        
        # Camera controls
        cam_controls = QHBoxLayout()
        self.btn_toggle = QPushButton("▶ Mulai Scan")
        self.btn_toggle.setMinimumHeight(50)
        self.btn_toggle.setStyleSheet(f"background: {COLORS['success']}; font-size: 16px;")
        
        self.btn_mirror = QPushButton("🔄 Mirror")
        self.btn_mirror.setProperty("class", "secondary")
        
        self.btn_flip_camera = QPushButton("📷 Ganti Kamera")
        self.btn_flip_camera.setProperty("class", "secondary")
        
        cam_controls.addWidget(self.btn_toggle)
        cam_controls.addWidget(self.btn_mirror)
        cam_controls.addWidget(self.btn_flip_camera)
        
        camera_layout.addWidget(self.video)
        camera_layout.addLayout(cam_controls)
        
        # Right: Status and history
        right_panel = QFrame()
        right_panel.setFixedWidth(350)
        right_layout = QVBoxLayout(right_panel)
        
        # Status badge
        self.badge = QLabel("—")
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setMinimumHeight(80)
        self.badge.setStyleSheet(f"""
            background: {COLORS['surface']};
            border-radius: 12px;
            font-size: 24px;
            font-weight: 700;
        """)
        
        self.scan_status = QLabel("Status: Idle")
        self.scan_status.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 14px;")
        
        # History
        history_label = QLabel("Riwayat Scan (10 terakhir)")
        history_label.setStyleSheet("font-weight: 600; margin-top: 16px;")
        
        self.history = QListWidget()
        
        right_layout.addWidget(self.badge)
        right_layout.addWidget(self.scan_status)
        right_layout.addWidget(history_label)
        right_layout.addWidget(self.history)
        
        layout.addWidget(camera_frame, 2)
        layout.addWidget(right_panel, 1)
        
        return tab
    
    def _create_people_tab(self) -> QWidget:
        """Create people management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Add person form
        form_layout = QHBoxLayout()
        self.people_name = QLineEdit()
        self.people_name.setPlaceholderText("Masukkan nama person...")
        
        self.btn_people_add = QPushButton("➕ Tambah Person")
        self.btn_people_refresh = QPushButton("🔄 Refresh")
        self.btn_people_refresh.setProperty("class", "secondary")
        
        form_layout.addWidget(self.people_name, 1)
        form_layout.addWidget(self.btn_people_add)
        form_layout.addWidget(self.btn_people_refresh)
        
        # People list
        self.people_list = QListWidget()
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.btn_enroll = QPushButton("📸 Enroll Dataset")
        self.btn_enroll.setStyleSheet(f"background: {COLORS['success']};")
        
        self.btn_people_delete = QPushButton("🗑️ Hapus")
        self.btn_people_delete.setProperty("class", "danger")
        
        self.btn_rebuild_cache = QPushButton("🔧 Rebuild Cache")
        self.btn_rebuild_cache.setProperty("class", "secondary")
        
        action_layout.addWidget(self.btn_enroll)
        action_layout.addWidget(self.btn_people_delete)
        action_layout.addWidget(self.btn_rebuild_cache)
        action_layout.addStretch()
        
        layout.addLayout(form_layout)
        layout.addWidget(self.people_list)
        layout.addLayout(action_layout)
        
        return tab
    
    def _create_events_tab(self) -> QWidget:
        """Create events/logs tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        self.ev_status = QLineEdit()
        self.ev_status.setPlaceholderText("Filter status...")
        self.ev_status.setMaximumWidth(150)
        
        self.ev_name = QLineEdit()
        self.ev_name.setPlaceholderText("Filter nama...")
        self.ev_name.setMaximumWidth(200)
        
        self.ev_day = QLineEdit()
        self.ev_day.setPlaceholderText("YYYY-MM-DD")
        self.ev_day.setMaximumWidth(120)
        
        self.ev_limit = QSpinBox()
        self.ev_limit.setRange(10, 500)
        self.ev_limit.setValue(50)
        self.ev_limit.setMaximumWidth(80)
        
        self.btn_ev_load = QPushButton("🔍 Load Events")
        
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.ev_status)
        filter_layout.addWidget(QLabel("Nama:"))
        filter_layout.addWidget(self.ev_name)
        filter_layout.addWidget(QLabel("Tanggal:"))
        filter_layout.addWidget(self.ev_day)
        filter_layout.addWidget(QLabel("Limit:"))
        filter_layout.addWidget(self.ev_limit)
        filter_layout.addWidget(self.btn_ev_load)
        filter_layout.addStretch()
        
        # Events table
        self.ev_table = QTableWidget(0, 8)
        self.ev_table.setHorizontalHeaderLabels(["ID", "Day", "Time", "Device", "Name", "Type", "Status", "Distance"])
        self.ev_table.horizontalHeader().setStretchLastSection(True)
        
        # Correction section
        correct_group = QGroupBox("Koreksi Event")
        correct_layout = QHBoxLayout(correct_group)
        
        self.c_event_id = QLineEdit()
        self.c_event_id.setPlaceholderText("Event ID")
        self.c_event_id.setMaximumWidth(100)
        
        self.c_final_name = QLineEdit()
        self.c_final_name.setPlaceholderText("Nama yang benar")
        
        self.c_note = QLineEdit()
        self.c_note.setPlaceholderText("Catatan (opsional)")
        
        self.btn_correct = QPushButton("✅ Koreksi")
        self.btn_correct.setStyleSheet(f"background: {COLORS['warning']};")
        
        correct_layout.addWidget(self.c_event_id)
        correct_layout.addWidget(self.c_final_name)
        correct_layout.addWidget(self.c_note)
        correct_layout.addWidget(self.btn_correct)
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.ev_table)
        layout.addWidget(correct_group)
        
        return tab
    
    def _create_reports_tab(self) -> QWidget:
        """Create reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Month selector
        month_layout = QHBoxLayout()
        
        self.r_month = QLineEdit()
        self.r_month.setPlaceholderText("YYYY-MM (contoh: 2026-01)")
        self.r_month.setMaximumWidth(200)
        
        self.btn_report = QPushButton("📊 Load Report")
        self.btn_export_csv = QPushButton("📥 Export CSV")
        self.btn_export_csv.setStyleSheet(f"background: {COLORS['success']};")
        
        month_layout.addWidget(QLabel("Periode:"))
        month_layout.addWidget(self.r_month)
        month_layout.addWidget(self.btn_report)
        month_layout.addWidget(self.btn_export_csv)
        month_layout.addStretch()
        
        # Report table
        self.report_table = QTableWidget(0, 4)
        self.report_table.setHorizontalHeaderLabels(["Nama", "Hari Hadir", "Terlambat", "Missing Out"])
        self.report_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addLayout(month_layout)
        layout.addWidget(self.report_table)
        
        return tab
    
    def _create_settings_tab(self) -> QWidget:
        """Create settings/login tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Login section
        login_group = QGroupBox("🔐 Admin Login")
        login_layout = QFormLayout(login_group)
        
        self.in_user = QLineEdit()
        self.in_user.setPlaceholderText("Username admin...")
        
        self.in_pass = QLineEdit()
        self.in_pass.setPlaceholderText("Password...")
        self.in_pass.setEchoMode(QLineEdit.Password)
        
        self.btn_login = QPushButton("Login")
        self.btn_login.setMinimumWidth(120)
        
        self.lbl_login = QLabel("Belum login")
        self.lbl_login.setStyleSheet(f"color: {COLORS['text_muted']};")
        
        login_layout.addRow("Username:", self.in_user)
        login_layout.addRow("Password:", self.in_pass)
        login_layout.addRow("", self.btn_login)
        login_layout.addRow("Status:", self.lbl_login)
        
        # API Settings
        api_group = QGroupBox("🌐 API Configuration")
        api_layout = QFormLayout(api_group)
        
        self.api_url = QLineEdit()
        self.api_url.setPlaceholderText("http://localhost:8000")
        
        self.device_id = QLineEdit()
        self.device_id.setPlaceholderText("Device ID")
        
        api_layout.addRow("API URL:", self.api_url)
        api_layout.addRow("Device ID:", self.device_id)
        
        layout.addWidget(login_group)
        layout.addWidget(api_group)
        layout.addStretch()
        
        return tab
    
    # UI Helper Methods
    def set_badge(self, text: str, kind: str):
        """Update status badge"""
        colors = {
            "ok": COLORS['success'],
            "late": COLORS['warning'],
            "unknown": COLORS['text_muted'],
            "error": COLORS['error'],
            "idle": COLORS['surface_light'],
            "cooldown": COLORS['primary'],
            "duplicate": COLORS['text_muted'],
        }
        bg = colors.get(kind, COLORS['surface_light'])
        self.badge.setText(text)
        self.badge.setStyleSheet(f"""
            background: {bg};
            border-radius: 12px;
            font-size: 24px;
            font-weight: 700;
            padding: 16px;
        """)
    
    def push_history(self, text: str):
        """Add item to history list"""
        item = QListWidgetItem(text)
        self.history.insertItem(0, item)
        while self.history.count() > 10:
            self.history.takeItem(self.history.count() - 1)
        
        # Also add to activity list on dashboard
        self.activity_list.insertItem(0, QListWidgetItem(text))
        while self.activity_list.count() > 20:
            self.activity_list.takeItem(self.activity_list.count() - 1)
    
    def update_mirror_button(self, mirror_enabled: bool):
        """Update mirror button state"""
        if mirror_enabled:
            self.btn_mirror.setText("🔄 Mirror: ON")
            self.btn_mirror.setStyleSheet(f"background: {COLORS['success']};")
        else:
            self.btn_mirror.setText("🔄 Mirror: OFF")
            self.btn_mirror.setProperty("class", "secondary")
    
    def info(self, title: str, msg: str):
        QMessageBox.information(self, title, msg)

    def error(self, title: str, msg: str):
        QMessageBox.critical(self, title, msg)
    
    def show_notification(self, title: str, message: str, success: bool = True):
        """Show notification message box"""
        if success:
            QMessageBox.information(self, title, message)
        else:
            QMessageBox.warning(self, title, message)
    
    def pick_images(self) -> list[str]:
        """Open file dialog to pick images"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Pilih Foto", "", 
            "Images (*.jpg *.jpeg *.png *.webp)"
        )
        return files
    
    def show_dataset_upload_dialog(self, person_name: str, person_id: int = None):
        """Show dataset upload dialog"""
        files = self.pick_images()
        if files and person_id:
            self.dataset_upload_requested.emit(person_id, files)
        return files
    
    def show_camera_selection_dialog(self, cameras: list):
        """Show camera selection (simplified)"""
        if not cameras:
            self.error("Kamera", "Tidak ada kamera terdeteksi")
            return None
        
        # For now, just return first alternative camera
        current = cameras[0]['index'] if cameras else 0
        for cam in cameras:
            if cam['index'] != current:
                return cam['index']
        return current
