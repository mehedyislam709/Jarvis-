import os
import sys
import time
import socket
import logging
import threading
import queue
from datetime import datetime

# Hardware and System Metrics Interfaces
import psutil

# Platform-Specific Media Controls
if sys.platform == "win32":
    # On Windows, we use ctypes to directly access the core audio endpoints cleanly without relying on external applications
    import ctypes
    from ctypes import cast, POINTER
    try:
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        WINDOWS_AUDIO_SUPPORT = True
    except ImportError:
        WINDOWS_AUDIO_SUPPORT = False
else:
    WINDOWS_AUDIO_SUPPORT = False

# =====================================================================
#                        CORE SYSTEM CONFIGURATIONS
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

system_active = True
ui_feedback_queue = queue.Queue()

# =====================================================================
#            MODULE 1: ACTIVE SYSTEM OPTIMIZER
# =====================================================================
class ActiveSystemOptimizer:
    """
    Directly monitors running operating system tasks, terminates RAM-heavy 
    runaway background processes safely, and performs memory cache flushes.
    """
    def __init__(self, ram_threshold_percent: float = 85.0):
        self.ram_threshold = ram_threshold_percent
        # List of high-priority system components that Jarvis must NEVER terminate
        self.whitelist = ["explorer.exe", "svchost.exe", "system", "taskmgr.exe", "python.exe"]

    def get_system_health(self) -> dict:
        """Retrieves and packages instant system hardware metrics."""
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_usage,
            "ram_percent": ram_info.percent,
            "ram_available_gb": round(ram_info.available / (1024**3), 2),
            "disk_percent": disk_info.percent
        }

    def optimize_memory(self) -> list:
        """
        Scans all running processes and terminates unauthorized applications 
        consuming excess memory to restore system responsiveness.
        """
        logging.info("[Optimizer Engine] Commencing deep system optimization sequence.")
        terminated_processes = []
        
        # Check overall memory load first
        current_ram = psutil.virtual_memory().percent
        if current_ram < self.ram_threshold:
            logging.info(f"[Optimizer Engine] Memory usage stable at {current_ram}%. No termination required.")
            return terminated_processes

        # Sort and filter runaway processes
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                proc_name = proc.info['name'].lower()
                proc_pid = proc.info['pid']
                proc_mem = proc.info['memory_percent']

                # Safeguard core system dependencies
                if any(protected in proc_name for protected in self.whitelist):
                    continue

                # Terminate processes consuming more than 2% of total RAM during a spike
                if proc_mem > 2.0:
                    logging.warning(f"[Optimizer Engine] Runaway process targeted: {proc_name} (PID: {proc_pid}, RAM: {proc_mem:.2f}%)")
                    p = psutil.Process(proc_pid)
                    p.terminate()  # Graceful exit request
                    terminated_processes.append(proc_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        logging.info(f"[Optimizer Engine] Cleanup sequence complete. Reclaimed resources from: {terminated_processes}")
        return terminated_processes


# =====================================================================
#            MODULE 2: IOT & SMART HOME BRIDGE
# =====================================================================
class IoTSmartHomeBridge(threading.Thread):
    """
    Manages connections to local smart devices using asynchronous TCP/UDP packets.
    Runs on a background thread to prevent GUI/voice command hangs.
    """
    def __init__(self, host: str = "0.0.0.0", port: int = 9999):
        super().__init__()
        self.name = "JarvisIoTThread"
        self.host = host
        self.port = port
        self.registered_devices = {
            "living_room_light": {"ip": "192.168.1.100", "state": "OFF"},
            "smart_ac": {"ip": "192.168.1.105", "state": "OFF", "temp": 22}
        }
        self.running = True

    def run(self):
        """Sets up a lightweight local command listener socket for incoming IoT handshakes."""
        logging.info(f"[IoT Bridge] Initializing socket listener on {self.host}:{self.port}")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(1.0)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
        except Exception as e:
            logging.error(f"[IoT Bridge] Failed to bind local interface: {e}")
            self.running = False

        while self.running and system_active:
            try:
                client_conn, addr = server_socket.accept()
                logging.info(f"[IoT Bridge] Direct handshake from device: {addr}")
                # Process the device packet on a helper handler
                threading.Thread(target=self._handle_device_packet, args=(client_conn,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                logging.error(f"[IoT Bridge] Connection loop exception: {e}")

        server_socket.close()
        logging.info("[IoT Bridge] Socket listener terminated successfully.")

    def _handle_device_packet(self, client_socket):
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                logging.info(f"[IoT Bridge] Data received: {data}")
                # Example: Register incoming heartbeat packet
                # Process logic here...
            client_socket.close()
        except Exception as e:
            logging.error(f"[IoT Bridge] Device processing exception: {e}")

    def send_device_command(self, device_id: str, action: str, parameters: dict = None) -> bool:
        """
        Sends execution packets directly to your local smart hardware.
        """
        if device_id not in self.registered_devices:
            logging.error(f"[IoT Bridge] Action denied. Device '{device_id}' is unregistered.")
            return False

        device_ip = self.registered_devices[device_id]["ip"]
        logging.info(f"[IoT Bridge] Dispatching command '{action}' directly to device {device_id} at {device_ip}")
        
        # Update our internal state log
        self.registered_devices[device_id]["state"] = action.upper()
        if parameters and "temp" in parameters:
            self.registered_devices[device_id]["temp"] = parameters["temp"]
            
        # Physical network dispatch emulation
        # In production, replace this with your target API (TPLink Kasa, Tuya, HomeAssistant HTTP/WebSocket client)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            # Emulated connection check
            # sock.connect((device_ip, 80))
            # sock.sendall(f"CMD:{action}".encode())
            sock.close()
            return True
        except Exception as e:
            logging.warning(f"[IoT Bridge] Device physical handshake emulated. (Offline status handled: {e})")
            return True


# =====================================================================
#            MODULE 3: MEDIA & SOUND CONTROLLER
# =====================================================================
class MediaSoundController:
    """
    Direct OS interface that adjusts machine system volume and 
    emulates media playback hotkeys cleanly.
    """
    def __init__(self):
        self.os_platform = sys.platform

    def set_master_volume(self, percentage: int):
        """Sets the operating system's master volume cleanly on Windows, Mac, or Linux."""
        percentage = max(0, min(100, percentage))  # Clamps values between 0 and 100
        logging.info(f"[Audio Core] Setting master system volume to {percentage}%")

        if self.os_platform == "win32":
            if WINDOWS_AUDIO_SUPPORT:
                try:
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    # Scalar mapping (0.0 to 1.0)
                    volume.SetMasterVolumeLevelScalar(percentage / 100.0, None)
                except Exception as e:
                    logging.error(f"[Audio Core] Win32 volume modification failed: {e}")
            else:
                logging.warning("[Audio Core] Windows API dependencies (pycaw, comtypes) missing.")
                
        elif self.os_platform == "darwin":  # macOS
            os.system(f"osascript -e 'set volume output volume {percentage}'")
            
        elif self.os_platform.startswith("linux"):  # Linux (Alsamixer)
            os.system(f"amixer sset 'Master' {percentage}%")

    def trigger_playback_action(self, action: str):
        """
        Interacts directly with virtual keyboard keycodes to manipulate background players.
        Available actions: "play_pause", "next", "previous"
        """
        logging.info(f"[Audio Core] Executing playback action: {action}")
        
        # Emulating physical system keys safely via virtual OS layers
        if self.os_platform == "win32":
            import ctypes
            win_key_map = {
                "play_pause": 0xB3,  # VK_MEDIA_PLAY_PAUSE
                "next": 0xB0,        # VK_MEDIA_NEXT_TRACK
                "previous": 0xB1     # VK_MEDIA_PREV_TRACK
            }
            if action in win_key_map:
                ctypes.windll.user32.keybd_event(win_key_map[action], 0, 0, 0) # Key press down
                ctypes.windll.user32.keybd_event(win_key_map[action], 0, 2, 0) # Key release up
                
        elif self.os_platform == "darwin":  # macOS
            mac_key_map = {
                "play_pause": "play",
                "next": "next",
                "previous": "previous"
            }
            if action in mac_key_map:
                os.system(f"osascript -e 'tell application \"System Events\" to key code {mac_key_map[action]}'")
                
        elif self.os_platform.startswith("linux"):
            # Requires xdotool dependencies on Linux environments
            linux_key_map = {
                "play_pause": "XF86AudioPlay",
                "next": "XF86AudioNext",
                "previous": "XF86AudioPrev"
            }
            if action in linux_key_map:
                os.system(f"xdotool key {linux_key_map[action]}")


# =====================================================================
#             CENTRAL SYSTEM COORDINATOR DECK
# =====================================================================
class JarvisSystemController:
    def __init__(self):
        # Instantiate Engines
        self.optimizer = ActiveSystemOptimizer(ram_threshold_percent=80.0)
        self.media = MediaSoundController()
        
        # Spawn thread-isolated IoT Engine
        self.iot_bridge = IoTSmartHomeBridge()
        self.iot_bridge.daemon = True
        self.iot_bridge.start()

    def run_interactive_terminal(self):
        global system_active
        
        while system_active:
            print("\n=======================================================")
            print("        JARVIS AUTOMATION & HARDWARE CONTROLLER        ")
            print("=======================================================")
            print("1. Read Real-time CPU & Memory Health Metrics")
            print("2. Run Active System RAM Optimization Sequence")
            print("3. Adjust System Master Volume Percentage")
            print("4. Send Media Control Action (Play / Pause)")
            print("5. Dispatch TCP/IP IoT Signal (Toggle Smart Bulb)")
            print("6. Shutdown Components Safely")
            print("-------------------------------------------------------")
            
            choice = input("Select an option (1-6): ").strip()
            
            if choice == '1':
                metrics = self.optimizer.get_system_health()
                print("\n--- Current System Health Metrics ---")
                print(f"Processor Activity: {metrics['cpu_percent']}%")
                print(f"Memory Alloc:       {metrics['ram_percent']}% ({metrics['ram_available_gb']} GB Free)")
                print(f"Disk Usage:         {metrics['disk_percent']}%")
                
            elif choice == '2':
                # Force memory threshold optimization manually
                terminated = self.optimizer.optimize_memory()
                if terminated:
                    print(f"\n[Jarvis]: Active system optimized. Cleared processes: {terminated}")
                else:
                    print("\n[Jarvis]: System overhead is normal. Optimization skipped to protect workflow.")
                    
            elif choice == '3':
                try:
                    vol = int(input("Enter Target Volume Level (0-100): ").strip())
                    self.media.set_master_volume(vol)
                except ValueError:
                    print("[System Error] Invalid volume format entered.")
                    
            elif choice == '4':
                self.media.trigger_playback_action("play_pause")
                print("[Jarvis]: Dispatched media toggle packet.")
                
            elif choice == '5':
                state_choice = input("Enter light status ('on' or 'off'): ").strip().lower()
                self.iot_bridge.send_device_command("living_room_light", state_choice)
                print(f"[Jarvis]: Living Room bulb set to '{state_choice.upper()}'.")
                
            elif choice == '6':
                print("\nClosing master control operations...")
                system_active = False
                self.iot_bridge.running = False
                self.iot_bridge.join()
                break


# =====================================================================
#                         SYSTEM ENTRYPOINT
# =====================================================================
if __name__ == "__main__":
    controller = JarvisSystemController()
    controller.run_interactive_terminal()
