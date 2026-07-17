import os
import sys
import time
import socket
import logging
import threading
import psutil
import queue
from datetime import datetime

# Logging: Thread-safe configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# =====================================================================
#            MODULE 1: ACTIVE SYSTEM OPTIMIZER (Hardened)
# =====================================================================
class ActiveSystemOptimizer:
    def __init__(self, ram_threshold_percent: float = 85.0):
        self.ram_threshold = ram_threshold_percent
        # সিকিউর হোয়াইটলিস্ট: সিস্টেমের মূল অংশগুলো সুরক্ষিত রাখা
        self.whitelist = {"explorer.exe", "svchost.exe", "system", "taskmgr.exe", "python.exe", "wininit.exe"}

    def optimize_memory(self) -> list:
        terminated_processes = []
        if psutil.virtual_memory().percent < self.ram_threshold:
            return terminated_processes

        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                # শুধুমাত্র ইউজারের প্রসেসগুলোই চেক করা হবে (সিস্টেম সিকিউরিটির জন্য)
                if proc.info['name'].lower() in self.whitelist or proc.username() == 'SYSTEM':
                    continue
                
                if proc.info['memory_percent'] > 5.0: # থ্রেশহোল্ড বাড়ানো হয়েছে
                    logging.warning(f"[Optimizer] Terminating high-mem process: {proc.info['name']}")
                    proc.terminate() 
                    terminated_processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return terminated_processes

# =====================================================================
#            MODULE 2: IOT BRIDGE (Socket Hardened)
# =====================================================================
class IoTSmartHomeBridge(threading.Thread):
    def __init__(self, host: str = "127.0.0.1", port: int = 9999): # 0.0.0.0 এর বদলে localhost নিরাপদ
        super().__init__(name="JarvisIoTThread", daemon=True)
        self.host = host
        self.port = port
        self.running = True

    def run(self):
        # সকেট সিকিউরিটি: শুধুমাত্র লোকালহোস্ট থেকে কানেকশন আশা করা হচ্ছে
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.settimeout(2.0)
            try:
                server_sock.bind((self.host, self.port))
                server_sock.listen(1)
                while self.running:
                    try:
                        conn, addr = server_sock.accept()
                        with conn:
                            conn.settimeout(1.0)
                            data = conn.recv(1024)
                            if data:
                                logging.info(f"[IoT] Secure packet from {addr}: {data[:50]}")
                    except socket.timeout:
                        continue
            except Exception as e:
                logging.error(f"[IoT Bridge] Fatal Socket Error: {e}")

# =====================================================================
#            MODULE 3: MEDIA & SOUND (Cross-Platform Fallback)
# =====================================================================
class MediaSoundController:
    def set_master_volume(self, percentage: int):
        percentage = max(0, min(100, percentage))
        try:
            if sys.platform == "win32":
                # Windows COM automation needs pycaw
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(percentage / 100.0, None)
            else:
                # Cross-platform fallback for Linux/Mac
                cmd = f"amixer sset 'Master' {percentage}%" if sys.platform.startswith("linux") else f"osascript -e 'set volume output volume {percentage}'"
                os.system(cmd)
        except Exception as e:
            logging.error(f"[Audio Core] Failed to set volume: {e}")

# =====================================================================
#             CENTRAL SYSTEM COORDINATOR DECK
# =====================================================================
class JarvisSystemController:
    def __init__(self):
        self.optimizer = ActiveSystemOptimizer()
        self.media = MediaSoundController()
        self.iot_bridge = IoTSmartHomeBridge()
        self.iot_bridge.start()

    def run(self):
        print("\n--- JARVIS CORE OPERATIONAL ---")
        try:
            while True:
                choice = input("\n[1: Health, 2: Optimize, 3: Volume, 4: Exit]: ").strip()
                if choice == '1':
                    mem = psutil.virtual_memory()
                    print(f"Memory: {mem.percent}% used. {round(mem.available/(1024**3), 2)}GB free.")
                elif choice == '2':
                    cleaned = self.optimizer.optimize_memory()
                    print(f"Optimized: {cleaned if cleaned else 'None needed'}")
                elif choice == '3':
                    vol = int(input("Volume level (0-100): "))
                    self.media.set_master_volume(vol)
                elif choice == '4':
                    break
        finally:
            logging.info("Shutting down Jarvis Core.")

if __name__ == "__main__":
    controller = JarvisSystemController()
    controller.run()
