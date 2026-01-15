import re
from typing import Optional, List
from logger_config import get_logger

logger = get_logger("validators")

class InputValidator:
    """Centralized input validation and sanitization"""
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username input"""
        if not username:
            return False, "Username wajib diisi"
        
        username = username.strip()
        
        if len(username) < 3:
            return False, "Username minimal 3 karakter"
        
        if len(username) > 50:
            return False, "Username maksimal 50 karakter"
        
        # Allow alphanumeric, underscore, and dash
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username hanya boleh mengandung huruf, angka, underscore, dan dash"
        
        return True, username
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password input"""
        if not password:
            return False, "Password wajib diisi"
        
        if len(password) < 4:
            return False, "Password minimal 4 karakter"
        
        if len(password) > 100:
            return False, "Password maksimal 100 karakter"
        
        return True, password
    
    @staticmethod
    def validate_person_name(name: str) -> tuple[bool, str]:
        """Validate person name input"""
        if not name:
            return False, "Nama wajib diisi"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "Nama minimal 2 karakter"
        
        if len(name) > 100:
            return False, "Nama maksimal 100 karakter"
        
        # Allow letters, spaces, dots, and common Indonesian characters
        if not re.match(r'^[a-zA-Z\s\.\-\']+$', name):
            return False, "Nama hanya boleh mengandung huruf, spasi, titik, dan tanda hubung"
        
        return True, name.title()
    
    @staticmethod
    def validate_event_id(event_id: str) -> tuple[bool, int]:
        """Validate event ID input"""
        if not event_id:
            return False, 0
        
        event_id = event_id.strip()
        
        if not event_id.isdigit():
            return False, 0
        
        try:
            eid = int(event_id)
            if eid <= 0:
                return False, 0
            return True, eid
        except ValueError:
            return False, 0
    
    @staticmethod
    def validate_month(month: str) -> tuple[bool, str]:
        """Validate month input (YYYY-MM format)"""
        if not month:
            return False, "Format bulan wajib diisi"
        
        month = month.strip()
        
        if not re.match(r'^\d{4}-\d{2}$', month):
            return False, "Format harus YYYY-MM (contoh: 2026-01)"
        
        year, month_num = month.split('-')
        
        try:
            year_int = int(year)
            month_int = int(month_num)
            
            if year_int < 2020 or year_int > 2030:
                return False, "Tahun harus antara 2020-2030"
            
            if month_int < 1 or month_int > 12:
                return False, "Bulan harus antara 1-12"
            
            return True, month
        except ValueError:
            return False, "Format bulan tidak valid"
    
    @staticmethod
    def validate_day(day: str) -> tuple[bool, str]:
        """Validate day input (YYYY-MM-DD format)"""
        if not day:
            return True, ""  # Optional field
        
        day = day.strip()
        
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', day):
            return False, "Format harus YYYY-MM-DD (contoh: 2026-01-15)"
        
        try:
            from datetime import datetime
            datetime.strptime(day, '%Y-%m-%d')
            return True, day
        except ValueError:
            return False, "Tanggal tidak valid"
    
    @staticmethod
    def validate_status(status: str) -> tuple[bool, str]:
        """Validate status input"""
        if not status:
            return True, ""  # Optional field
        
        status = status.strip()
        
        valid_statuses = ['ok', 'duplicate', 'unknown', 'reject', 'cooldown', 'error']
        if status.lower() not in valid_statuses:
            return False, f"Status harus salah dari: {', '.join(valid_statuses)}"
        
        return True, status.lower()
    
    @staticmethod
    def validate_limit(limit: int) -> tuple[bool, int]:
        """Validate limit input"""
        if limit < 10:
            return False, 10
        if limit > 500:
            return False, 500
        return True, limit
    
    @staticmethod
    def validate_image_paths(paths: List[str]) -> tuple[bool, List[str], str]:
        """Validate image file paths"""
        if not paths:
            return False, [], "Tidak ada file yang dipilih"
        
        if len(paths) > 10:
            return False, [], "Maksimal 10 file yang diperbolehkan"
        
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
        valid_paths = []
        
        for i, path in enumerate(paths):
            if not path or not isinstance(path, str):
                return False, [], f"Path file tidak valid pada index {i}"
            
            # Security: validate file path
            if ".." in path or path.startswith("/") or ":" not in path:
                return False, [], f"Path file tidak aman: {path}"
            
            if not path.lower().endswith(valid_extensions):
                return False, [], f"File {path} bukan gambar yang valid"
            
            import os
            if not os.path.exists(path):
                return False, [], f"File tidak ditemukan: {path}"
            
            # Check file size (max 5MB)
            file_size = os.path.getsize(path)
            if file_size > 5 * 1024 * 1024:
                return False, [], f"File {path} terlalu besar (maks 5MB)"
            
            valid_paths.append(path)
        
        return True, valid_paths, ""

class Sanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 100) -> str:
        """Sanitize string input"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\';]', '', text)
        
        # Trim whitespace
        text = text.strip()
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename"""
        if not filename:
            return ""
        
        # Remove path traversal and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\.\.', '', filename)
        
        return filename.strip()
