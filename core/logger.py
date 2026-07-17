import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

class JarvisLogger:
    """
    Centralized, thread-safe, rotating log management system.
    """
    _instance = None
    LOG_DIR = Path("logs")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JarvisLogger, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        self.LOG_DIR.mkdir(exist_ok=True)
        self.formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        # Initialize loggers
        self.system = self._get_logger("SYSTEM", "system.log")
        self.error = self._get_logger("ERROR", "error.log")
        self.voice = self._get_logger("VOICE", "voice.log")
        self.vision = self._get_logger("VISION", "vision.log")
        self.brain = self._get_logger("BRAIN", "brain.log")

    def _get_logger(self, name: str, filename: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Prevent adding handlers multiple times
        if not logger.handlers:
            # File Handler with rotation (5MB per file, 5 backups)
            file_handler = RotatingFileHandler(
                self.LOG_DIR / filename,
                maxBytes=5 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8"
            )
            file_handler.setFormatter(self.formatter)
            logger.addHandler(file_handler)

            # Console Handler (Optional: only for debugging)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            logger.addHandler(console_handler)

        return logger

# Access via: from logger import logger
logger = JarvisLogger()
