import yaml
import logging
import threading
from pathlib import Path
from typing import Any, Optional

# Setup professional logging for system auditing
logger = logging.getLogger("JARVIS.CONFIG")

class ConfigManager:
    """
    Thread-safe, atomic Configuration Manager with nested key support.
    Uses temp-file swapping to ensure data integrity during disk I/O.
    """
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.data: dict = {}
        self._lock = threading.RLock()  # Prevents race conditions
        
        # Ensure directory structure exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def load(self) -> None:
        """Loads configuration from YAML with validation."""
        with self._lock:
            if not self.config_path.exists():
                logger.info(f"Configuration file not found at {self.config_path}. Initializing empty.")
                self.data = {}
                return

            try:
                with self.config_path.open("r", encoding="utf-8") as f:
                    self.data = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse YAML file: {e}")
                self.data = {}

    def get(self, keys: str, default: Any = None) -> Any:
        """Retrieves nested values using dot notation (e.g., 'voice.profile.male')."""
        with self._lock:
            value = self.data
            try:
                for key in keys.split("."):
                    if not isinstance(value, dict) or key not in value:
                        return default
                    value = value[key]
                return value if value is not None else default
            except (KeyError, TypeError):
                return default

    def set(self, keys: str, value: Any) -> None:
        """Sets nested values and triggers an atomic save."""
        with self._lock:
            current = self.data
            parts = keys.split(".")
            for key in parts[:-1]:
                current = current.setdefault(key, {})
            current[parts[-1]] = value
            self._atomic_save()

    def _atomic_save(self) -> None:
        """Writes to a temporary file, then renames to avoid file corruption."""
        temp_path = self.config_path.with_suffix(".tmp")
        try:
            with temp_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    self.data, f, 
                    default_flow_style=False, 
                    sort_keys=False, 
                    allow_unicode=True
                )
            # Atomic operation: replace existing file with the new one
            temp_path.replace(self.config_path)
        except Exception as e:
            logger.critical(f"Critical disk failure during config save: {e}")
            if temp_path.exists():
                temp_path.unlink()
            raise
