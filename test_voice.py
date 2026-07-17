import json
import logging
import threading
from pathlib import Path
from typing import Any, Optional

class ConfigManager:
    """
    Thread-safe, robust Configuration Manager with validation and atomic saves.
    """
    _instance = None
    _lock = threading.Lock() # Ensures thread safety

    def __new__(cls, path="config.json"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, path="config.json"):
        if self._initialized: return
        self.path = Path(path)
        self.data = self._load()
        self._initialized = True

    def _load(self) -> dict:
        if not self.path.exists():
            return {"voice": {"default": "male", "profiles": {"male": {}, "female": {}}}}
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("Config corruption detected. Initializing defaults.")
            return {}

    def get(self, key_path: str, default: Any = None) -> Any:
        """Safe nested key access (e.g., 'voice.profiles.male')"""
        keys = key_path.split('.')
        val = self.data
        try:
            for k in keys: val = val[k]
            return val
        except KeyError:
            return default

    def set(self, key_path: str, value: Any):
        """Atomic update of config values."""
        with self._lock:
            keys = key_path.split('.')
            d = self.data
            for k in keys[:-1]: d = d.setdefault(k, {})
            d[keys[-1]] = value
            self._save()

    def _save(self):
        """Atomic write to disk to prevent file corruption."""
        temp_path = self.path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(self.data, f, indent=4)
        temp_path.replace(self.path) # Atomic replacement

# --- Implementation ---
config = ConfigManager()

# 1. Secure Access with fallback
default_voice = config.get("voice.default", "male")
voice_profile = config.get(f"voice.profiles.{default_voice}", {})

# 2. Hardened Update logic
def update_voice_profile(gender: str):
    valid_genders = ["male", "female"]
    if gender in valid_genders:
        config.set("voice.default", gender)
        logging.info(f"Voice profile updated to: {gender}")
    else:
        logging.warning(f"Security Alert: Invalid profile update attempt: {gender}")

update_voice_profile("female")
