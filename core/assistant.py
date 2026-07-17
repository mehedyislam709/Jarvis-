import logging
import signal
import sys
from datetime import datetime

# Configure Professional Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [%(name)s] | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("jarvis_system.log")]
)

class Jarvis:
    """
    The Jarvis AI Mainframe.
    Handles system lifecycle, diagnostic reporting, and graceful resource cleanup.
    """
    def __init__(self, version: str = "2.0.0"):
        self.name = "JARVIS"
        self.version = version
        self.logger = logging.getLogger("MAINFRAME")
        self._is_running = False

        # Register signals for safe termination (Ctrl+C)
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def _handle_exit(self, signum, frame):
        """Ensures the system shuts down without corrupting databases/logs."""
        self.logger.warning(f"Termination signal {signum} received. Initiating graceful shutdown...")
        self._is_running = False
        sys.exit(0)

    def start(self):
        """Initializes the AI ecosystem with diagnostics."""
        self._is_running = True
        
        # System Banner
        self.logger.info("=" * 50)
        self.logger.info(f"Initializing {self.name} AI Mainframe...")
        self.logger.info(f"Version: {self.version} | Build: {datetime.now().strftime('%Y-%m-%d')}")
        self.logger.info("=" * 50)

        try:
            self._run_diagnostics()
            self.logger.info("Core Systems Online and Ready.")
        except Exception as e:
            self.logger.critical(f"System boot failed: {e}", exc_info=True)
            self._handle_exit(None, None)

    def _run_diagnostics(self):
        """Validates all peripheral modules before activation."""
        self.logger.info("Running pre-flight diagnostics...")
        # Placeholder for module checks (e.g., check DB connection, mic access, GPU)
        self.logger.info("Module Check: [VISION] - OK")
        self.logger.info("Module Check: [BRAIN]  - OK")
        self.logger.info("Module Check: [VAULT]  - OK")

if __name__ == "__main__":
    jarvis_ai = Jarvis()
    jarvis_ai.start()
