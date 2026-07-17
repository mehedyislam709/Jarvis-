import importlib
import inspect
import logging
import sys
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("JARVIS.PLUGIN_MANAGER")

class BasePlugin:
    """Interface enforcing structural integrity and metadata."""
    name: str = "BasePlugin"
    version: str = "0.0.0"

    def __init__(self):
        self.is_active = False

    def activate(self) -> None: raise NotImplementedError
    def deactivate(self) -> None: raise NotImplementedError
    def execute(self, *args, **kwargs) -> Any: raise NotImplementedError

class PluginManager:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir).resolve()
        self.plugins: Dict[str, BasePlugin] = {}
        self._setup_environment()

    def _setup_environment(self):
        """Ensures the directory is a valid Python package."""
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        init_file = self.plugin_dir / "__init__.py"
        if not init_file.exists():
            init_file.touch()
        
        # Add plugin directory to sys.path if not present
        if str(self.plugin_dir.parent) not in sys.path:
            sys.path.insert(0, str(self.plugin_dir.parent))

    def load_plugins(self) -> None:
        """Dynamically scans, imports, and validates plugins."""
        for path in self.plugin_dir.glob("*_plugin.py"):
            module_name = f"{self.plugin_dir.name}.{path.stem}"
            try:
                # Reload module if it exists to allow hot-swapping
                module = importlib.import_module(module_name)
                importlib.reload(module)
                
                if hasattr(module, "Plugin"):
                    plugin_cls = getattr(module, "Plugin")
                    if inspect.isclass(plugin_cls) and issubclass(plugin_cls, BasePlugin) and plugin_cls is not BasePlugin:
                        plugin = plugin_cls()
                        plugin.activate()
                        plugin.is_active = True
                        self.plugins[plugin.name] = plugin
                        logger.info(f"Plugin '{plugin.name}' (v{plugin.version}) loaded successfully.")
                    else:
                        logger.error(f"Plugin at {path.stem} does not inherit from BasePlugin.")
            except Exception as e:
                logger.critical(f"Failed to initialize plugin {module_name}: {e}", exc_info=True)

    def execute(self, name: str, *args, **kwargs) -> Any:
        """Secure execution with state verification."""
        plugin = self.plugins.get(name)
        if not plugin or not plugin.is_active:
            logger.error(f"Attempted to execute inactive or missing plugin: {name}")
            raise RuntimeError(f"Plugin '{name}' is unavailable.")
        
        return plugin.execute(*args, **kwargs)

    def unload_all(self) -> None:
        """Graceful shutdown of all systems."""
        for name in list(self.plugins.keys()):
            self.unload_plugin(name)

    def unload_plugin(self, name: str) -> None:
        plugin = self.plugins.pop(name, None)
        if plugin:
            try:
                plugin.deactivate()
                plugin.is_active = False
                logger.info(f"Plugin '{name}' deactivated.")
            except Exception as e:
                logger.error(f"Error during deactivation of {name}: {e}")
