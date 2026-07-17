import os
import time
from PIL import ImageGrab
import mss
import mss.tools

class JarvisScreenCapturer:
    def __init__(self, output_dir="jarvis_captures"):
        """Initializes the Jarvis Screen Capture system."""
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        print(f"[Jarvis] Screen capture system initialized. Saving to: {self.output_dir}")

    def capture_with_pillow(self):
        """
        Uses Pillow (ImageGrab) to take a standard screenshot of the entire screen.
        Best for general, non-urgent captures.
        """
        print("[Jarvis] Capturing standard screenshot using Pillow...")
        filename = os.path.join(self.output_dir, f"pillow_snapshot_{int(time.time())}.png")
        
        # Grab the entire screen
        screenshot = ImageGrab.grab()
        screenshot.save(filename)
        
        print(f"[Jarvis] Screenshot successfully saved: {filename}")
        return filename

    def capture_with_mss(self):
        """
        Uses the mss library for high-performance, ultra-fast screen capture.
        Ideal for real-time analysis, games, or high-frame-rate requirements.
        """
        print("[Jarvis] Capturing high-speed screenshot using mss...")
        filename = os.path.join(self.output_dir, f"mss_snapshot_{int(time.time())}.png")
        
        with mss.mss() as sct:
            # Select the primary monitor (Monitor 1)
            monitor = sct.monitors[1]
            
            # Fast screen grab
            sct_img = sct.grab(monitor)
            
            # Convert to PNG and save
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
            
        print(f"[Jarvis] High-speed screenshot successfully saved: {filename}")
        return filename

# Execution Example
if __name__ == "__main__":
    # Create the Jarvis capture object
    jarvis_cam = JarvisScreenCapturer()
    
    # Method 1: Standard Pillow Capture
    jarvis_cam.capture_with_pillow()
    
    time.sleep(1) # Brief pause
    
    # Method 2: High-Performance mss Capture
    jarvis_cam.capture_with_mss()
