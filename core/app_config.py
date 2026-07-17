import yaml
import logging
import threading
from pathlib import Path
from typing import Any, Optional

# Setup professional logging
logger = logging.getLogger("JARVIS.CONFIG")

class ConfigManager:
    """
    A thread-safe, atomic configuration manager for Jarvis.
    Supports nested keys, atomic saves, and safe memory synchronization.
    """
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.data: dict = {}
        self._lock = threading.RLock()  # Re-entrant lock for thread safety
        
        # Ensure directory existence
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def load(self):
        """Loads configuration from YAML with error handling."""
        with self._lock:
            try:
                if not self.config_path.exists():
                    logger.warning(f"Config file not found at {self.config_path}. Creating new.")
                    self.save()
                    return

                with self.config_path.open("r", encoding="utf-8") as f:
                    self.data = yaml.safe_load(f) or {}
            except Exception as e:
                logger.critical(f"Failed to load configuration: {e}")
                self.data = {}

    def get(self, *keys: str, default: Any = None) -> Any:
        """Thread-safe retrieval of nested keys."""
        with self._lock:
            value = self.data
            for key in keys:
                if not isinstance(value, dict) or key not in value:
                    return default
                value = value.get(key)
            return value if value is not None else default

    def set(self, *keys: str, value: Any):
        """Thread-safe atomic update and disk sync."""
        with self._lock:
            current = self.data
            for key in keys[:-1]:
                current = current.setdefault(key, {})
            current[keys[-1]] = value
            self.save()

    def save(self):
        """Writes configuration to a temporary file, then swaps to ensure atomicity."""
        temp_path = self.config_path.with_suffix(".tmp")
        try:
            with temp_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    self.data, f, 
                    default_flow_style=False, 
                    sort_keys=False, 
                    allow_unicode=True
                )
            # Atomic swap (prevents file corruption if process crashes mid-write)
            temp_path.replace(self.config_path)
        except Exception as e:
            logger.error(f"Critical error while saving config: {e}")
            if temp_path.exists():
                temp_path.unlink()
            raise

# --- Production Usage ---
# config = ConfigManager()
# config.set("voice", "profiles", "male", "volume", 0.8)
# vol = config.get("voice", "profiles", "male", "volume", default=1.0)
