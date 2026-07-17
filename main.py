import sys
import signal
import logging
from core.assistant import Jarvis
from logger_hub import logger_hub  # Your centralized logging system

class JarvisMainframe:
    """
    Mainframe controller managing lifecycle, resource allocation, 
    and signal-based graceful shutdowns.
    """
    def __init__(self):
        self.jarvis = Jarvis()
        # Handle termination signals (Ctrl+C, etc.)
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def _handle_exit(self, signum, frame):
        logger_hub.system.info(f"Termination signal {signum} received. Initiating shutdown...")
        sys.exit(0)

    def boot(self):
        try:
            logger_hub.system.info("Initializing Jarvis Core Mainframe...")
            self.jarvis.start()
        except Exception as e:
            logger_hub.error.critical(f"FATAL SYSTEM FAILURE: {str(e)}", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    mainframe = JarvisMainframe()
    mainframe.boot()
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

class JarvisLogger:
    def __init__(self):
        self.LOG_DIR = "jarvis_vault/logs"
        os.makedirs(self.LOG_DIR, exist_ok=True)
        
        self.formatter = logging.Formatter(
            "[%(asctime)s] | %(levelname)-8s | %(name)-10s | %(message)s"
        )
        
        self.system = self._setup("SYSTEM", "system.log")
        self.error = self._setup("ERROR", "error.log", level=logging.ERROR)
        self.voice = self._setup("VOICE", "voice.log")
        self.vision = self._setup("VISION", "vision.log")

    def _setup(self, name, filename, level=logging.INFO):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        if logger.handlers: return logger

        file_handler = RotatingFileHandler(
            os.path.join(self.LOG_DIR, filename), maxBytes=5*1024*1024, backupCount=5
        )
        file_handler.setFormatter(self.formatter)
        
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(self.formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console)
        return logger

logger_hub = JarvisLogger()
