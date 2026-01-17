import logging
import os
from datetime import datetime
from typing import Optional

class LoggerSetup:
    """Centralized logging setup for the application"""
    
    @staticmethod
    def setup_logger(name: str = "absensi_app", log_level: str = "INFO") -> logging.Logger:
        """Setup logger with file and console handlers"""
        
        # Create logs directory if not exists
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler with rotation (max 10MB, keep 5 files)
        from logging.handlers import RotatingFileHandler
        log_file = os.path.join(log_dir, f"absensi.log")
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024, 
            backupCount=5, 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

# Global logger instance
logger = LoggerSetup.setup_logger()

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger instance"""
    if name:
        return logging.getLogger(f"absensi_app.{name}")
    return logger
