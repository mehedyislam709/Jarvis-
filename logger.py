import logging
import os
import sys
from logging.handlers import RotatingFileHandler

class JarvisLogger:
    """
    Jarvis Enterprise-Grade Central Logging Framework.
    Provides thread-safe, multi-channel output for all system modules.
    """
    LOG_DIR = "jarvis_vault/logs"

    def __init__(self):
        os.makedirs(self.LOG_DIR, exist_ok=True)
        
        # Centralized standard formatter
        self.formatter = logging.Formatter(
            "[%(asctime)s] | %(levelname)-8s | %(name)-10s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Dedicated loggers for each subsystem
        self.system = self._setup_logger("SYSTEM", "system.log")
        self.error  = self._setup_logger("ERROR", "error.log", level=logging.ERROR)
        self.voice  = self._setup_logger("VOICE", "voice.log")
        self.vision = self._setup_logger("VISION", "vision.log")
        self.brain  = self._setup_logger("BRAIN", "brain.log")

        # Global exception hook to capture system crashes
        sys.excepthook = self._handle_uncaught_exception

    def _setup_logger(self, name, filename, level=logging.INFO):
        """Internal method to initialize logging handlers for file and console."""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if logger.handlers:
            return logger

        # File handler with rotation (5MB per file, 5 backups)
        file_path = os.path.join(self.LOG_DIR, filename)
        file_handler = RotatingFileHandler(
            file_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(self.formatter)
        
        # Console handler for real-time monitoring
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Automatically records critical system crashes to 'error.log'."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.error.critical("Uncaught Exception detected:", exc_info=(exc_type, exc_value, exc_traceback))

# Exported as a singleton for global access
logger_hub = JarvisLogger()
