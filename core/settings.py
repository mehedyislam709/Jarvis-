from core.config import Config

config = Config()

SYSTEM_NAME = config.get("system.name")

VERSION = config.get("system.version")

LANGUAGE = config.get("system.language")

DEBUG = config.get("system.debug")

VOICE_RATE = config.get("voice.rate")

VOICE_VOLUME = config.get("voice.volume")

WAKE_WORD = config.get("voice.wake_word")

AUTO_SCROLL = config.get("screen.auto_scroll")

SCROLL_SPEED = config.get("screen.scroll_speed")

OCR_ENGINE = config.get("ocr.engine")

LLM_MODEL = config.get("llm.model")
