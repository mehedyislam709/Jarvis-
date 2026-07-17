import logging
import os
import sys
from logging.handlers import RotatingFileHandler

class JarvisLogger:
    """
    JARVIS এন্টারপ্রাইজ-গ্রেড সেন্ট্রাল লগিং ফ্রেমওয়ার্ক।
    এটি থ্রেড-সেফ এবং মাল্টি-চ্যানেল আউটপুট সাপোর্ট করে।
    """
    LOG_DIR = "jarvis_vault/logs"

    def __init__(self):
        os.makedirs(self.LOG_DIR, exist_ok=True)
        
        # কেন্দ্রীয় ফরম্যাটার (যা সকল লগারের জন্য স্ট্যান্ডার্ড)
        self.formatter = logging.Formatter(
            "[%(asctime)s] | %(levelname)-8s | %(name)-10s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # বিভিন্ন মডিউলের জন্য ডেডিকেটেড লগার্স
        self.system = self._setup_logger("SYSTEM", "system.log")
        self.error  = self._setup_logger("ERROR", "error.log", level=logging.ERROR)
        self.voice  = self._setup_logger("VOICE", "voice.log")
        self.vision = self._setup_logger("VISION", "vision.log")
        self.brain  = self._setup_logger("BRAIN", "brain.log")

        # সিস্টেম ক্র্যাশ হ্যান্ডলার
        sys.excepthook = self._handle_uncaught_exception

    def _setup_logger(self, name, filename, level=logging.INFO):
        """লগার তৈরির ইন্টারনাল মেথড যা ফাইল এবং কনসোল উভয়কে হ্যান্ডেল করে।"""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if logger.handlers:
            return logger

        # ফাইল হ্যান্ডলার (Rotating: 5MB, 5 backups)
        file_path = os.path.join(self.LOG_DIR, filename)
        file_handler = RotatingFileHandler(
            file_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(self.formatter)
        
        # কনসোল হ্যান্ডলার (রিয়েল-টাইম মনিটরিংয়ের জন্য)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """সিস্টেম ক্র্যাশ করলে তা 'error.log'-এ অটোমেটিক রেকর্ড করবে।"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.error.critical("Uncaught Exception detected:", exc_info=(exc_type, exc_value, exc_traceback))

# সিঙ্গেলটন হিসেবে এক্সপোর্ট করা হচ্ছে
logger_hub = JarvisLogger()
