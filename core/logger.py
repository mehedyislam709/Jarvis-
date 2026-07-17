import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)


class JarvisLogger:

    def __init__(self):

        self.system = self.create_logger(
            "SYSTEM",
            "system.log"
        )

        self.error = self.create_logger(
            "ERROR",
            "error.log"
        )

        self.voice = self.create_logger(
            "VOICE",
            "voice.log"
        )

        self.vision = self.create_logger(
            "VISION",
            "vision.log"
        )

        self.screen = self.create_logger(
            "SCREEN",
            "screen.log"
        )

        self.brain = self.create_logger(
            "BRAIN",
            "brain.log"
        )

    def create_logger(self, name, filename):

        logger = logging.getLogger(name)

        logger.setLevel(logging.INFO)

        if logger.handlers:
            return logger

        filepath = os.path.join(LOG_DIR, filename)

        handler = RotatingFileHandler(
            filepath,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )

        formatter = logging.Formatter(

            "[%(asctime)s] "
            "[%(levelname)s] "
            "[%(name)s] "
            "%(message)s"

        )

        handler.setFormatter(formatter)

        logger.addHandler(handler)

        return logger


logger = JarvisLogger()
