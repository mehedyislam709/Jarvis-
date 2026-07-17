import logging
from typing import Dict, Any
from core.plugin_manager import BasePlugin

# Centralized logger for this specific plugin
logger = logging.getLogger("PLUGIN.HELLO")

class Plugin(BasePlugin):
    """
    HelloPlugin: A robust, metadata-aware plugin for Jarvis.
    """
    name = "HelloPlugin"
    version = "1.1.0"
    author = "Jarvis-Core"
    
    def __init__(self):
        super().__init__()
        self._is_active = False

    def activate(self) -> bool:
        """
        Activates the plugin with safety checks.
        """
        try:
            self._is_active = True
            logger.info(f"{self.name} (v{self.version}) activated successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to activate {self.name}: {e}")
            return False

    def deactivate(self) -> bool:
        """
        Ensures graceful cleanup of resources.
        """
        self._is_active = False
        logger.info(f"{self.name} deactivated safely.")
        return True

    def execute(self, payload: Dict[str, Any] = None) -> str:
        """
        Handles execution with input validation and defensive programming.
        """
        if not self._is_active:
            logger.warning("Attempted to execute an inactive plugin.")
            return "Error: Plugin is not active."

        # Extract user_name safely from the payload dictionary
        user_name = payload.get("user_name", "User") if payload else "User"
        
        # Logic is now separated from printing
        response = f"Hello, {user_name}! I am Jarvis, your dedicated AI collaborator."
        
        logger.debug(f"Executed {self.name} for {user_name}")
        return response
