import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLineEdit, QFormLayout, QMessageBox, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QFileDialog, QSpinBox, QComboBox,
    QProgressBar, QDialog, QDialogButtonBox, QGridLayout, QGroupBox,
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPixmap, QFont, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from ui_components import AnimatedButton

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
    "text_primary": "#F1F5F9",
    "text_muted": "#94A3B8",
    "text_secondary": "#CBD5E1",
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
        self.setFixedHeight(105) # Increased slightly for lift effect
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['surface']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        
        # Shadow Effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
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
        
    def enterEvent(self, event):
        # Lift animation
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(200)
        self.anim.setStartValue(10)
        self.anim.setEndValue(20)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.start()
        
        self.shadow.setOffset(0, 5)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['surface_light']};
                border-radius: 12px;
                border: 1px solid {COLORS['primary']};
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(200)
        self.anim.setStartValue(20)
        self.anim.setEndValue(10)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.start()
        
        self.shadow.setOffset(0, 2)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['surface']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        super().leaveEvent(event)
    
    def set_value(self, value: str):
        self.value_label.setText(value)


class CameraCaptureDialog(QDialog):
    """Dialog for capturing face photos via camera"""
    
    def __init__(self, parent=None, person_name=""):
        super().__init__(parent)
        self.setWindowTitle(f"📷 Capture Wajah - {person_name}")
        self.setMinimumSize(700, 500)
        self.setStyleSheet(STYLESHEET)
        
        self.person_name = person_name
        self.captured_images = []
        self.camera = None
        self.timer = None
        
        self._setup_ui()
        self._start_camera()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Instructions
        instructions = QLabel(f"Capture foto wajah untuk: {self.person_name}")
        instructions.setStyleSheet("font-size: 14px; font-weight: 600;")
        instructions.setAlignment(Qt.AlignCenter)
        
        # Camera preview
        self.preview = QLabel("Memuat kamera...")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(480, 360)
        self.preview.setStyleSheet(f"background: #000; border-radius: 8px; color: {COLORS['text_muted']};")
        
        # Captured thumbnails
        thumb_layout = QHBoxLayout()
        thumb_layout.setSpacing(8)
        self.thumb_labels = []
        for i in range(5):
            thumb = QLabel(f"{i+1}")
            thumb.setFixedSize(80, 80)
            thumb.setAlignment(Qt.AlignCenter)
            thumb.setStyleSheet(f"background: {COLORS['surface']}; border-radius: 6px; border: 1px solid {COLORS['border']};")
            self.thumb_labels.append(thumb)
            thumb_layout.addWidget(thumb)
        thumb_layout.addStretch()
        
        # Status
        self.status_label = QLabel("Tekan tombol Capture untuk mengambil foto (max 5)")
        self.status_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_capture = AnimatedButton("📷 Capture", color=COLORS['success'])
        self.btn_capture.clicked.connect(self._capture)
        
        self.btn_done = AnimatedButton("✅ Selesai & Upload", color=COLORS['primary'])
        self.btn_done.clicked.connect(self.accept)
        self.btn_done.setEnabled(False)
        
        btn_cancel = QPushButton("❌ Batal")
        btn_cancel.setProperty("class", "secondary")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_capture)
        btn_layout.addWidget(self.btn_done)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        
        layout.addWidget(instructions)
        layout.addWidget(self.preview, 1)
        layout.addLayout(thumb_layout)
        layout.addWidget(self.status_label)
        layout.addLayout(btn_layout)
    
    def _start_camera(self):
        import cv2
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            self.preview.setText("❌ Kamera tidak tersedia")
            return
        
        from PySide6.QtCore import QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(33)  # ~30 FPS
    
    def _update_frame(self):
        import cv2
        if self.camera is None:
            return
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.flip(frame, 1)  # Mirror
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            from PySide6.QtGui import QImage
            img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            scaled = QPixmap.fromImage(img).scaled(
                self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.preview.setPixmap(scaled)
            self._current_frame = frame
    
    def _capture(self):
        if len(self.captured_images) >= 5:
            return
        
        if hasattr(self, '_current_frame'):
            import cv2
            frame = self._current_frame.copy()
            self.captured_images.append(frame)
            
            # Update thumbnail
            idx = len(self.captured_images) - 1
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            from PySide6.QtGui import QImage
            img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            thumb = QPixmap.fromImage(img).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.thumb_labels[idx].setPixmap(thumb)
            
            self.status_label.setText(f"Captured: {len(self.captured_images)}/5 foto")
            self.btn_done.setEnabled(True)
            
            if len(self.captured_images) >= 5:
                self.btn_capture.setEnabled(False)
                self.status_label.setText("Maksimum 5 foto tercapai. Klik Selesai untuk upload.")
    
    def get_captured_images(self):
        return self.captured_images
    
    def closeEvent(self, event):
        if self.timer:
            self.timer.stop()
        if self.camera:
            self.camera.release()
        super().closeEvent(event)


class MainUI(QWidget):
    """Modern Desktop App UI"""
    
    # Signals
    camera_changed = Signal(int)
    mirror_toggled = Signal(bool)
    dataset_upload_requested = Signal(int, list)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Absensi Desktop - Modern Dashboard")
        self.setMinimumSize(800, 500)  # Smaller minimum for flexibility
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
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        logo = QLabel()
        logo_path = "assets/logo.png"
        if not os.path.exists(logo_path):
            logo_path = "logo.png"  # Fallback to current dir if not found
            
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            if not pix.isNull():
                logo.setPixmap(pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        title_text = QLabel("Absensi Desktop")
        title_text.setStyleSheet("font-size: 18px; font-weight: 700;")
        
        title_layout.addWidget(logo)
        title_layout.addWidget(title_text)
        
        # Status Label
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500;")
        
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addWidget(self.lbl_status)
        
        # Settings Button
        self.btn_settings = QPushButton("⚙️")
        self.btn_settings.setFixedSize(40, 40)
        self.btn_settings.setCursor(Qt.PointingHandCursor)
        self.btn_settings.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 18px;
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg']};
                color: {COLORS['text_primary']};
                border-color: {COLORS['primary']};
            }}
        """)
        layout.addWidget(self.btn_settings)
        
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
        self.btn_quick_scan = AnimatedButton("▶ Mulai Scan", color=COLORS['primary'])
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
        """Create kiosk/scan tab - horizontal layout for flexibility"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)
        
        # Top bar: Logo + Title + Controls
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        
        # Logo
        import os
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        self.logo_label = QLabel()
        self.logo_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            self.logo_label.setPixmap(logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo_label.setText("🎓")
            self.logo_label.setStyleSheet("font-size: 28px;")
        
        # Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        title = QLabel("SISTEM ABSENSI WAJAH")
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        subtitle = QLabel("Politeknik Baja Tegal")
        subtitle.setStyleSheet(f"font-size: 10px; color: {COLORS['text_muted']};")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Controls
        self.btn_toggle = AnimatedButton("▶ Mulai", color=COLORS['success'])
        # self.btn_toggle.setStyleSheet(f"background: {COLORS['success']}; font-size: 11px; padding: 6px 12px;") # Handled by class
        
        self.btn_mirror = QPushButton("🔄")
        self.btn_mirror.setProperty("class", "secondary")
        self.btn_mirror.setToolTip("Mirror")
        
        self.btn_flip_camera = QPushButton("📷")
        self.btn_flip_camera.setProperty("class", "secondary")
        self.btn_flip_camera.setToolTip("Ganti Kamera")
        
        self.scan_status = QLabel("Siap")
        self.scan_status.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px;")
        
        top_bar.addWidget(self.logo_label)
        top_bar.addLayout(title_layout)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_toggle)
        top_bar.addWidget(self.btn_mirror)
        top_bar.addWidget(self.btn_flip_camera)
        top_bar.addWidget(self.scan_status)
        
        # Main content: Horizontal layout (Camera | Greeting)
        content = QHBoxLayout()
        content.setSpacing(10)
        
        # LEFT: Camera preview (expands)
        camera_frame = QFrame()
        camera_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        camera_frame.setStyleSheet(f"""
            background: {COLORS['surface']}; 
            border-radius: 8px;
            border: 2px solid {COLORS['border']};
        """)
        camera_layout = QVBoxLayout(camera_frame)
        camera_layout.setContentsMargins(6, 6, 6, 6)
        
        self.video = QLabel("📷 Arahkan wajah ke kamera")
        self.video.setAlignment(Qt.AlignCenter)
        self.video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video.setStyleSheet(f"""
            background: #000; 
            color: {COLORS['text_muted']}; 
            border-radius: 6px;
            font-size: 14px;
        """)
        camera_layout.addWidget(self.video)
        
        # RIGHT: Greeting panel (fixed width ratio)
        right_panel = QFrame()
        right_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        right_panel.setMinimumWidth(250)
        right_panel.setMaximumWidth(400)
        right_panel.setStyleSheet(f"""
            background: {COLORS['surface']};
            border-radius: 8px;
            border: 2px solid {COLORS['primary']};
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)
        
        # Name badge (large)
        self.badge = QLabel("Silakan absen...")
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setWordWrap(True)
        self.badge.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {COLORS['text']};
        """)
        
        # Greeting message
        self.greeting_msg = QLabel("Arahkan wajah Anda ke kamera untuk melakukan absensi")
        self.greeting_msg.setAlignment(Qt.AlignCenter)
        self.greeting_msg.setWordWrap(True)
        self.greeting_msg.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_muted']};
        """)
        
        # Spacer for mascot placeholder (later)
        mascot_placeholder = QLabel("")
        mascot_placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        right_layout.addWidget(self.badge)
        right_layout.addWidget(self.greeting_msg)
        right_layout.addWidget(mascot_placeholder)
        
        # Add to content layout (70:30 ratio)
        content.addWidget(camera_frame, 7)
        content.addWidget(right_panel, 3)
        
        # Hidden history for internal use
        self.history = QListWidget()
        self.history.setVisible(False)
        
        # Assemble main layout
        main_layout.addLayout(top_bar, 0)
        main_layout.addLayout(content, 1)
        main_layout.addWidget(self.history)
        
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
        
        self.btn_capture_enroll = QPushButton("📷 Capture Wajah")
        self.btn_capture_enroll.setStyleSheet(f"background: {COLORS['primary']};")
        
        self.btn_enroll = QPushButton("📁 Upload File")
        self.btn_enroll.setProperty("class", "secondary")
        
        self.btn_people_delete = QPushButton("🗑️ Hapus")
        self.btn_people_delete.setProperty("class", "danger")
        
        self.btn_rebuild_cache = QPushButton("🔧 Rebuild Cache")
        self.btn_rebuild_cache.setProperty("class", "secondary")
        
        action_layout.addWidget(self.btn_capture_enroll)
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
