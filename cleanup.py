import os
import time
import logging
from io import BytesIO
from typing import Optional, Tuple
from PIL import ImageGrab

# Configure advanced corporate-grade logging infrastructure
logging.basicConfig(level=logging.INFO, format="[Vision] %(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("JarvisCapture")

class SecureScreenCapturer:
    def __init__(self, output_dir: str = "jarvis_captures", keep_disk_copy: bool = False):
        """
        Initializes the hardened Screen Capture System.
        :param output_dir: Safe directory path to record screenshots locally if permitted.
        :param keep_disk_copy: Set to False (Default) to run entirely in RAM to avoid storage exhaustion.
        """
        self.keep_disk_copy = keep_disk_copy
        # Defend against path traversal vulnerability by resolving absolute structures securely
        self.output_dir = os.path.abspath(output_dir)
        
        if self.keep_disk_copy and not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except OSError as path_err:
                logger.critical(f"Failed to create secure storage vault allocation: {path_err}")
                self.keep_disk_copy = False

    def _write_to_storage(self, raw_bytes: bytes) -> Optional[str]:
        """Handles isolated disk mutations exclusively when permitted."""
        if not self.keep_disk_copy:
            return None
            
        # Standardize strict naming schemas to prevent directory namespace injection vectors
        safe_filename = f"snapshot_{int(time.time())}.png"
        secure_filepath = os.path.join(self.output_dir, safe_filename)
        
        try:
            with open(secure_filepath, "wb") as secure_file:
                secure_file.write(raw_bytes)
            logger.info(f"Visual asset securely synchronized to file system: {secure_filepath}")
            return secure_filepath
        except IOError as io_err:
            logger.error(f"Write operation aborted. Secure storage I/O pipeline blocked: {io_err}")
            return None

    def capture_frame(self) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Safely grabs the display boundary context into an in-memory buffer without disk bloating.
        :return: A tuple containing (raw_png_bytes, file_path_if_saved)
        """
        logger.info("Extracting display matrix signature utilizing isolated Pillow pipeline...")
        screenshot = None
        try:
            # Captures display frame parameters securely into system active memory
            screenshot = ImageGrab.grab()
            
            # Compress asset securely inside a RAM buffer to eliminate storage footprint overhead
            with BytesIO() as storage_buffer:
                screenshot.save(storage_buffer, format="PNG")
                png_bytes = storage_buffer.getvalue()
                
            # Safely delegate local storage synchronization mechanisms
            saved_path = self._write_to_storage(png_bytes)
            return png_bytes, saved_path
            
        except Exception as grab_err:
            logger.error(f"Graphic memory abstraction pipeline failed critically: {grab_err}")
            return None, None
        finally:
            # Enforce deterministic environment cleanup checks to resolve dangling resource handles
            if screenshot:
                screenshot.close()

# =====================================================================
# Main Execution Guard Context
# =====================================================================
if __name__ == "__main__":
    # Initialize the engine in pure secure RAM mode (No hard drive bloat or trail records left behind)
    capturer = SecureScreenCapturer(keep_disk_copy=False)
    
    print("\n--- Starting Hardened Screen Capture Verification ---")
    raw_frame_data, disk_path = capturer.capture_frame()
    
    if raw_frame_data:
        print(f"[Success] Captured {len(raw_frame_data)} bytes of visual matrix entirely in RAM.")
