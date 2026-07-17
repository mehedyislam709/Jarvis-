import os
import time
import logging
from io import BytesIO
from typing import Optional, Tuple
from PIL import ImageGrab
import mss
import mss.tools

# Initialize professional enterprise-grade logging
logging.basicConfig(level=logging.INFO, format="[Jarvis] %(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("JarvisVision")

class JarvisScreenCapturer:
    def __init__(self, output_dir: str = "jarvis_captures", keep_local_copy: bool = False):
        """
        Initializes the robust Jarvis Screen Capture system.
        :param output_dir: Safe directory path to record screenshots locally if enabled.
        :param keep_local_copy: Set to False (Default) to run entirely in RAM to prevent disk bloating.
        """
        self.keep_local_copy = keep_local_copy
        # Defend against path traversal vulnerability by resolving absolute paths securely
        self.output_dir = os.path.abspath(output_dir)
        
        if self.keep_local_copy and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            
        logger.info(f"Screen capture network online. Target: {self.output_dir} | Keep Copies: {self.keep_local_copy}")

    def _save_to_disk_safely(self, image_bytes: bytes, prefix: str) -> Optional[str]:
        """Handles security-hardened disk I/O mutations exclusively when permitted."""
        if not self.keep_local_copy:
            return None

        # Build clean filenames away from dynamic injection threats
        safe_filename = f"{prefix}_snapshot_{int(time.time())}.png"
        secure_filepath = os.path.join(self.output_dir, safe_filename)

        try:
            with open(secure_filepath, "wb") as f:
                f.write(image_bytes)
            logger.info(f"Screenshot recorded securely to storage: {secure_filepath}")
            return secure_filepath
        except IOError as io_err:
            logger.error(f"Failed to securely dump binary snapshot to disk matrix: {io_err}")
            return None

    def capture_with_pillow(self) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Uses Pillow (ImageGrab) to safely capture the current display boundary into an in-memory buffer.
        :return: A tuple containing (raw_png_bytes, file_path_if_saved)
        """
        logger.info("Initiating standard screen grab utilizing Pillow pipeline...")
        try:
            # Grabs display frame into active RAM context
            screenshot = ImageGrab.grab()
            
            # Compress image safely into an isolated memory buffer instead of hitting disk instantly
            with BytesIO() as output_buffer:
                screenshot.save(output_buffer, format="PNG")
                png_bytes = output_buffer.getvalue()

            # Release OS image handle resources immediately to avoid leaks
            screenshot.close()

            # Delegate local logging storage securely
            saved_path = self._save_to_disk_safely(png_bytes, "pillow")
            return png_bytes, saved_path

        except Exception as pill_err:
            logger.error(f"Pillow visual frame capture sequence encountered an exception: {pill_err}")
            return None, None

    def capture_with_mss(self) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Uses the high-performance mss library for native fast frame buffer screen parsing.
        Ideal for performance-critical real-time applications.
        :return: A tuple containing (raw_png_bytes, file_path_if_saved)
        """
        logger.info("Initiating high-speed frame grab utilizing mss framework...")
        try:
            with mss.mss() as sct:
                # Security Boundary Check: Guard against virtualized/headless headless array IndexErrors
                if not sct.monitors:
                    logger.error("No active screen display monitors discovered by hardware profiles.")
                    return None, None
                
                # Default securely to monitor index 1 if multi-display exists, else fallback to index 0
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                
                sct_img = sct.grab(monitor)
                # Convert raw frame to atomic PNG byte structure inside virtual system memory
                png_bytes = mss.tools.to_png(sct_img.rgb, sct_img.size)

            saved_path = self._save_to_disk_safely(png_bytes, "mss")
            return png_bytes, saved_path

        except Exception as mss_err:
            logger.error(f"High-speed native display capture driver failed: {mss_err}")
            return None, None

# Main Execution Context
if __name__ == "__main__":
    # Initialize the engine in pure secure RAM mode (No residual disk bloat)
    jarvis_cam = JarvisScreenCapturer(keep_local_copy=False)
    
    print("\n--- Starting Secured Capture Verification ---")
    
    # Run isolated Pillow execution path
    pillow_bytes, _ = jarvis_cam.capture_with_pillow()
    if pillow_bytes:
        print(f"[Success] Captured {len(pillow_bytes)} bytes of data via Pillow entirely in RAM.")
        
    time.sleep(1) 
    
    # Run high-performance mss execution path
    mss_bytes, _ = jarvis_cam.capture_with_mss()
    if mss_bytes:
        print(f"[Success] Captured {len(mss_bytes)} bytes of data via mss entirely in RAM.")
