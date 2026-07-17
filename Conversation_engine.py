import logging
from typing import Optional

# Setup standard logging
logger = logging.getLogger(__name__)

class CompanyPlatform:
    def __init__(self, manager_instance):
        self.manager = manager_instance
        # Stronger: Initialize TTS once during startup to save system resources
        try:
            self.tts = TextToSpeechManager(offline_mode=True)
        except Exception as e:
            logger.error(f"Failed to initialize TTS system: {e}")
            self.tts = None

    def _sanitize_input(self, text: str, max_length: int = 200) -> str:
        """
        Secures the input string against command/prompt injection 
        and controls payload size.
        """
        if not text:
            return ""
        # Strip whitespace and truncate to prevent buffer/memory exhaustion attacks
        sanitized = text.strip()[:max_length]
        # Remove potentially dangerous characters depending on what TTS/Managers accept
        # e.g., avoiding characters that break shell commands or database queries
        return "".join(ch for ch in sanitized if ch.isalnum() or ch in " ,.-_?!")

    def run_business_logic(self, task: str) -> Optional[str]:
        """
        Executes business tasks securely with isolated error boundaries.
        """
        # 1. Input Validation & Sanitization (Security Enhancement)
        clean_task = self._sanitize_input(task)
        if not clean_task:
            logger.warning("Rejected execution: Task payload is empty or invalid.")
            return None

        # 2. Secure & Robust TTS Announcement
        if self.tts:
            try:
                # Announce sanitized string safely
                self.tts.speak(f"Manager David has received a new directive: {clean_task}")
            except Exception as tts_err:
                # Secure: Fail-silent for UI/audio. Don't crash the core business execution if audio fails.
                logger.error(f"TTS Announcement failed dynamically: {tts_err}")
        else:
            logger.warning("TTS system not available; skipping vocal announcement.")

        # 3. Robust Execution Flow with isolated Try-Except block
        try:
            logger.info(f"Executing business logic for task validation token hash: {hash(clean_task)}")
            report = self.manager.delegate_and_execute(clean_task)
            return report
            
        except AttributeError:
            logger.critical("Configuration Error: 'self.manager' or method does not exist.")
            raise
        except Exception as exec_err:
            # Secure: Catch and log internal failures without leaking stack traces to the end user
            logger.error(f"Business logic execution failed securely: {exec_err}")
            return "Execution failed due to an internal system error."

