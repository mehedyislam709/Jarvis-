from pathlib import Path
import yaml

class ConfigManager:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = Path(config_path)
        self.data = {}

    def load(self):
        if not self.config_path.exists():
            self.data = {}
            return

        with self.config_path.open("r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f) or {}

    def get(self, *keys, default=None):
        value = self.data
        for key in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(key)
            if value is None:
                return default
        return value

    def set(self, *keys, value):
        current = self.data
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value

    def save(self):
        with self.config_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                self.data,
                f,
                sort_keys=False,
                allow_unicode=True
      )
