import importlib
import os
from pathlib import Path


class BasePlugin:
    name = "BasePlugin"
    version = "1.0"

    def activate(self):
        pass

    def deactivate(self):
        pass

    def execute(self, *args, **kwargs):
        pass


class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins = {}

    def load_plugins(self):
        for file in os.listdir(self.plugin_dir):
            if file.endswith("_plugin.py"):
                module_name = file[:-3]

                module = importlib.import_module(
                    f"{self.plugin_dir.name}.{module_name}"
                )

                plugin = module.Plugin()

                plugin.activate()

                self.plugins[plugin.name] = plugin

                print(f"Loaded plugin: {plugin.name}")

    def get_plugin(self, name):
        return self.plugins.get(name)

    def execute(self, name, *args, **kwargs):
        plugin = self.get_plugin(name)

        if plugin:
            return plugin.execute(*args, **kwargs)

        raise ValueError(f"Plugin {name} not found")

    def unload_plugin(self, name):
        plugin = self.plugins.get(name)

        if plugin:
            plugin.deactivate()
            del self.plugins[name]
            print(f"Unloaded plugin: {name}")

    def list_plugins(self):
        return list(self.plugins.keys())
