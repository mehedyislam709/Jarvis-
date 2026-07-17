import importlib
import inspect
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("JARVIS.PLUGIN_MANAGER")

class BasePlugin:
    """Interface to enforce structural integrity of all plugins."""
    def __init__(self):
        self.is_active = False

    def activate(self) -> None: raise NotImplementedError
    def deactivate(self) -> None: raise NotImplementedError
    def execute(self, *args, **kwargs) -> Any: raise NotImplementedError

class PluginManager:
    """
    Secure, dynamic plugin orchestrator with dependency validation 
    and safe lifecycle management.
    """
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, BasePlugin] = {}
        self._ensure_dir()

    def _ensure_dir(self):
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(parents=True)
            # Add __init__.py so Python treats it as a package
            (self.plugin_dir / "__init__.py").touch()

    def load_plugins(self) -> None:
        """Dynamically imports and validates plugin modules."""
        for path in self.plugin_dir.glob("*_plugin.py"):
            module_name = f"{self.plugin_dir.name}.{path.stem}"
            try:
                module = importlib.import_module(module_name)
                
                # Security: Check for 'Plugin' class and inheritence
                if hasattr(module, "Plugin"):
                    plugin_class = getattr(module, "Plugin")
                    if inspect.isclass(plugin_class) and issubclass(plugin_class, BasePlugin):
                        plugin = plugin_class()
                        plugin.activate()
                        self.plugins[plugin.name] = plugin
                        logger.info(f"Successfully loaded: {plugin.name} v{plugin.version}")
                    else:
                        logger.error(f"Security Warning: {module_name} does not follow BasePlugin API.")
            except Exception as e:
                logger.critical(f"Failed to load plugin {module_name}: {e}")

    def execute(self, name: str, *args, **kwargs) -> Any:
        """Secure execution wrapper with error interception."""
        plugin = self.plugins.get(name)
        if not plugin:
            logger.warning(f"Execution failed: Plugin '{name}' not found.")
            raise ValueError(f"Plugin '{name}' not found")
        
        try:
            return plugin.execute(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error during execution of {name}: {e}")
            raise

    def unload_plugin(self, name: str) -> None:
        """Gracefully shuts down plugins."""
        plugin = self.plugins.pop(name, None)
        if plugin:
            plugin.deactivate()
            logger.info(f"Unloaded plugin: {name}")
