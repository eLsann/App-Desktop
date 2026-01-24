import os
import secrets
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, 
    QLabel, QSpinBox, QHBoxLayout, QMessageBox, QFrame, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class ModernInput(QLineEdit):
    def __init__(self, text="", password=False):
        super().__init__(text)
        if password:
            self.setEchoMode(QLineEdit.Password)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #334155;
                border-radius: 8px;
                padding: 10px;
                background: #1e293b; # Dark background
                color: #f8fafc;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background: #0f172a;
            }
        """)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, env_path=".env"):
        super().__init__(parent)
        self.setWindowTitle("Pengaturan Aplikasi")
        self.setFixedWidth(500)
        self.env_path = env_path
        
        # Styles
        self.setStyleSheet("""
            QDialog { background-color: #0f172a; color: #f8fafc; }
            QLabel { font-size: 14px; font-weight: 500; color: #cbd5e1; margin-bottom: 4px;}
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton[class="primary"] {
                background-color: #3b82f6;
                color: white;
                border: none;
            }
            QPushButton[class="primary"]:hover { background-color: #2563eb; }
            QPushButton[class="secondary"] {
                background-color: #334155;
                color: white;
                border: 1px solid #475569;
            }
            QPushButton[class="secondary"]:hover { background-color: #475569; }
            QFormLayout { spacing: 15px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QFrame()
        header.setStyleSheet("background: #1e293b; border-bottom: 1px solid #334155;")
        header_layout = QHBoxLayout(header)
        title = QLabel("Konfigurasi Sistem")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: white; border: none;")
        header_layout.addWidget(title)
        layout.addWidget(header)

        # Content Area (Scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        form_layout = QFormLayout(content_widget)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setVerticalSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # Initialize Inputs
        self.inputs = {}
        
        # Load current values
        current_config = self.load_env_values()

        # Add Fields
        self.add_section_title(form_layout, "Server & Koneksi")
        
        self.inputs['API_BASE_URL'] = ModernInput(current_config.get('API_BASE_URL', 'http://localhost:8000'))
        form_layout.addRow("URL API Server:", self.inputs['API_BASE_URL'])
        
        self.add_section_title(form_layout, "Perangkat (Device)")
        
        self.inputs['DEVICE_ID'] = ModernInput(current_config.get('DEVICE_ID', 'desktop-01'))
        form_layout.addRow("ID Perangkat:", self.inputs['DEVICE_ID'])
        
        self.inputs['DEVICE_TOKEN'] = ModernInput(current_config.get('DEVICE_TOKEN', ''), password=True)
        form_layout.addRow("Token Perangkat:", self.inputs['DEVICE_TOKEN'])
        
        # Camera
        self.add_section_title(form_layout, "Hardware")
        
        self.camera_idx = QSpinBox()
        self.camera_idx.setRange(0, 10)
        self.camera_idx.setValue(int(current_config.get('CAMERA_INDEX', 0)))
        self.camera_idx.setStyleSheet("""
            QSpinBox { 
                padding: 8px; border: 2px solid #334155; 
                border-radius: 8px; background: #1e293b; color: white;
                min-width: 80px;
            }
            QSpinBox::up-button, QSpinBox::down-button { width: 0px; border: none; }
        """)
        form_layout.addRow("Index Kamera:", self.camera_idx)

        # Add to main layout
        layout.addWidget(scroll_area)

        # Footer Actions
        footer = QFrame()
        footer.setStyleSheet("background: #1e293b; border-top: 1px solid #334155;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        
        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.setProperty("class", "secondary")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Simpan & Restart")
        self.btn_save.setProperty("class", "primary")
        self.btn_save.clicked.connect(self.save_config)
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_cancel)
        footer_layout.addWidget(self.btn_save)
        
        layout.addWidget(footer)

    def add_section_title(self, layout, text):
        lbl = QLabel(text.upper())
        lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 700; margin-top: 10px; margin-bottom: 5px;")
        layout.addRow(lbl)

    def load_env_values(self):
        config = {}
        if os.path.exists(self.env_path):
            with open(self.env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, val = line.strip().split('=', 1)
                        config[key.strip()] = val.strip()
        return config

    def save_config(self):
        # Update values
        new_values = {}
        for key, widget in self.inputs.items():
            new_values[key] = widget.text().strip()
        new_values['CAMERA_INDEX'] = str(self.camera_idx.value())

        try:
            # Read all lines to preserve comments
            lines = []
            if os.path.exists(self.env_path):
                with open(self.env_path, 'r') as f:
                    lines = f.readlines()
            
            # Map of updated keys
            written_keys = set()
            new_lines = []
            
            for line in lines:
                if '=' in line and not line.strip().startswith('#'):
                    key = line.split('=')[0].strip()
                    if key in new_values:
                        new_lines.append(f"{key}={new_values[key]}\n")
                        written_keys.add(key)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            # Append missing keys
            for key, val in new_values.items():
                if key not in written_keys:
                    new_lines.append(f"{key}={val}\n")
            
            # Write back
            with open(self.env_path, 'w') as f:
                f.writelines(new_lines)
            
            QMessageBox.information(self, "Berhasil", "Pengaturan disimpan. Aplikasi akan restart.")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan konfigurasi: {str(e)}")

