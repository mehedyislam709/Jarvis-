import logging
from typing import Dict, Any, Optional

class VoiceManager:
    """
    Manages voice profiles with strict validation, state consistency, 
    and secure fallbacks.
    """
    def __init__(self, config_manager: Any):
        self.config = config_manager
        self.logger = logging.getLogger("VOICE.MANAGER")

    def get_current_profile(self) -> Dict[str, Any]:
        """
        Retrieves the active profile with a mandatory security fallback.
        """
        try:
            profile_name = self.config.get("voice.default", "default")
            profile = self.config.get(f"voice.profiles.{profile_name}")
            
            if profile is None:
                self.logger.warning(f"Profile '{profile_name}' not found. Falling back to default.")
                return self.config.get("voice.profiles.default", {})
            
            return profile
        except Exception as e:
            self.logger.error(f"Failed to retrieve voice profile: {e}")
            return {}

    def switch_profile(self, profile_name: str) -> bool:
        """
        Switches the voice profile after verifying its existence.
        Implements atomic update logic.
        """
        if not isinstance(profile_name, str):
            self.logger.error("Invalid profile name type.")
            return False

        # Validate existence before switching
        if self.config.get(f"voice.profiles.{profile_name}") is not None:
            try:
                self.config.set("voice.default", profile_name)
                self.logger.info(f"Voice profile successfully switched to: {profile_name}")
                return True
            except Exception as e:
                self.logger.critical(f"Atomic update failed for profile '{profile_name}': {e}")
                return False
        
        self.logger.warning(f"Attempted to switch to non-existent profile: {profile_name}")
        return False
