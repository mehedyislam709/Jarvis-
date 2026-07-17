import os
import time
import logging
from typing import Optional
from io import BytesIO
from PIL import Image
import mss
import mss.tools
import pytesseract

# Initialize professional logging framework
logging.basicConfig(level=logging.INFO, format="[Jarvis] %(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("JarvisVision")

class JarvisVisionSystem:
    def __init__(self, output_dir: str = "jarvis_captures", keep_local_copy: bool = False):
        """
        Initializes the Jarvis Screen Capture and OCR system.
        :param output_dir: Folder to save raw snapshots if local copying is enabled.
        :param keep_local_copy: Set to True if you want to save PNGs on disk. Default is False (In-Memory).
        """
        self.keep_local_copy = keep_local_copy
        # Sanitize and resolve secure path structures
        self.output_dir = os.path.abspath(output_dir)
        
        if self.keep_local_copy and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            
        logger.info(f"Vision system initialized securely. In-memory processing active. Local copying: {self.keep_local_copy}")

    def capture_screen_raw(self) -> Optional[bytes]:
        """Uses mss to capture screen quickly and returns raw BGRA/RGBA pixels."""
        try:
            with mss.mss() as sct:
                # Use primary monitor securely
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                # Convert raw pixels directly to PNG format in bytes via mss tools
                return mss.tools.to_png(sct_img.rgb, sct_img.size)
        except Exception as e:
            logger.error(f"Screen capture sequence failed: {e}")
            return None

    def perform_ocr_from_bytes(self, image_bytes: bytes) -> str:
        """
        Reads raw image bytes dynamically using context managers and extracts text via OCR.
        Secure against Local File Inclusion (LFI) since it circumvents disk I/O vulnerabilities.
        """
        logger.info("Scanning raw memory buffer for text via OCR...")
        try:
            # Use BytesIO and context manager to isolate memory allocation safely
            with BytesIO(image_bytes) as img_stream:
                with Image.open(img_stream) as img:
                    # Enforce secure configurations to prevent Tesseract from running indefinitely
                    # Capping processing timeout at 10 seconds
                    extracted_text = pytesseract.image_to_string(img, timeout=10)
                    logger.info("OCR Memory Scan complete.")
                    return extracted_text.strip()
        except pytesseract.TesseractTimeoutError:
            logger.error("OCR execution timed out securely to protect CPU thresholds.")
            return ""
        except Exception as e:
            logger.error(f"OCR Pipeline processing failed: {e}")
            return ""

    def save_snapshot_log(self, image_bytes: bytes) -> None:
        """Safely dumps local file to disk only if explicit logging permission is given."""
        if not self.keep_local_copy:
            return
        
        # Prevent arbitrary path navigation by avoiding dynamic input strings
        safe_filename = f"mss_snapshot_{int(time.time())}.png"
        secure_filepath = os.path.join(self.output_dir, safe_filename)
        
        try:
            with open(secure_filepath, "wb") as f:
                f.write(image_bytes)
        except IOError as e:
            logger.error(f"Could not log file copy to disk safely: {e}")

    def scan_screen_now(self) -> str:
        """Helper method to take a quick capture and instantly read the text on screen without filling up storage."""
        # 1. Capture raw byte signature from the active display buffer
        image_bytes = self.capture_screen_raw()
        if not image_bytes:
            return ""
        
        # 2. Log fallback copy to disk if system configuration requires it
        self.save_snapshot_log(image_bytes)
        
        # 3. Process image data strictly out of volatile memory (RAM)
        return self.perform_ocr_from_bytes(image_bytes)

# Execution Context
if __name__ == "__main__":
    # Initialize the secured Jarvis vision engine without disk footprint leakage
    jarvis_vision = JarvisVisionSystem(keep_local_copy=False)
    
    print("\n--- Starting Secured Screen OCR Test ---")
    screen_text = jarvis_vision.scan_screen_now()
    
    print("\n[Jarvis] Text discovered on screen:")
    print("-" * 40)
    print(screen_text if screen_text else "[No readable text found]")
    print("-" * 40)
