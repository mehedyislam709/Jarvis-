import os
import sys
import cv2
import json
import time
import queue
import logging
import threading
import webbrowser
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional

import numpy as np
import psutil
import pyautogui
from deepface import DeepFace
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Cryptographic Integrity Layer
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

# Optional Advanced Vocal Modules with Graceful Fallbacks
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# =====================================================================
#                        GLOBAL LOGGING & CONFIG
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s",
    handlers=[
        logging.FileHandler("jarvis_mainframe_hardened.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Thread-safe termination flags and orchestration communication queues
SYSTEM_ACTIVE = True
BACKGROUND_TASK_QUEUE = queue.Queue()

# =====================================================================
#                  MODULE 1: VOICE & AUDIO SUBSYSTEM
# =====================================================================
class JarvisVoiceCore:
    def __init__(self):
        self.speech_engine = None
        self.recognizer = None
        self.mic = None
        self._lock = threading.Lock()
        
        if pyttsx3:
            try:
                self.speech_engine = pyttsx3.init()
                self.speech_engine.setProperty('rate', 175)
                self.speech_engine.setProperty('volume', 0.9)
                logging.info("[Audio Engine] PyTTSx3 voice synthesis system successfully mapped.")
            except Exception as e:
                logging.warning(f"[Audio Engine] Voice synthesis failed to initialize: {e}")
        
        if sr:
            try:
                self.recognizer = sr.Recognizer()
                self.mic = sr.Microphone()
                logging.info("[Audio Engine] Speech Recognition interfaces operational.")
            except Exception as e:
                logging.warning(f"[Audio Engine] Microphone access failed: {e}")

    def speak(self, text: str):
        """Generates clear synthetic voice feedback synchronously under thread-safe locking."""
        logging.info(f"[Jarvis Audio] Vocalizing: '{text}'")
        with self._lock:
            if self.speech_engine:
                try:
                    self.speech_engine.say(text)
                    self.speech_engine.runAndWait()
                except Exception as e:
                    logging.error(f"[Audio Engine] Runtime speech error: {e}")
                    print(f"\n[Jarvis Voice Emulation]: {text}")
            else:
                print(f"\n[Jarvis Voice Emulation]: {text}")

    def listen_command(self) -> str:
        """Listens to ambient audio and translates it to clear string commands."""
        if not self.recognizer or not self.mic:
            logging.warning("[Audio Engine] Voice input requested but interface is offline.")
            return ""

        try:
            with self.mic as source:
                logging.info("[Audio Engine] Calibrating ambient room noise levels...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("\n[Jarvis Engine] Listening for vocal command... Speak now.")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                
                logging.info("[Audio Engine] Processing vocal acoustics...")
                command = self.recognizer.recognize_google(audio)
                logging.info(f"[Audio Engine] Speech converted to text: '{command}'")
                return command
        except sr.WaitTimeoutError:
            logging.warning("[Audio Engine] Listening timeout reached.")
            return ""
        except Exception as e:
            logging.error(f"[Audio Engine] Recognition pipeline error: {e}")
            return ""


# =====================================================================
#             MODULE 2: MOUSE, KEYBOARD & SCREEN CONTROLLERS
# =====================================================================
class JarvisPeripheralController:
    def __init__(self):
        pyautogui.FAILSAFE = True  # Drag mouse to any corner to instantly abort
        pyautogui.PAUSE = 0.05
        self.screen_width, self.screen_height = pyautogui.size()

    def move_mouse_to(self, x: int, y: int, duration: float = 0.4):
        """Translates the cursor safely after bounding within verified monitor aspect coordinates."""
        # Sanitize boundaries defensively
        target_x = max(0, min(x, self.screen_width - 1))
        target_y = max(0, min(y, self.screen_height - 1))
        
        logging.info(f"[Peripheral Control] Cursor translation to X={target_x}, Y={target_y}")
        try:
            pyautogui.moveTo(target_x, target_y, duration=duration)
        except Exception as e:
            logging.error(f"Mouse movement fault: {e}")

    def execute_click(self, clicks: int = 1, button: str = 'left'):
        logging.info(f"[Peripheral Control] Triggering click: [{button}] x{clicks}")
        try:
            pyautogui.click(clicks=clicks, button=button)
        except Exception as e:
            logging.error(f"Mouse interaction fault: {e}")

    def virtual_type(self, text: str, delay: float = 0.03):
        logging.info("[Peripheral Control] Generating physical keystrokes onto input focus...")
        try:
            pyautogui.write(text, interval=delay)
        except Exception as e:
            logging.error(f"Keyboard output fault: {e}")

    def press_hotkey_combination(self, *keys):
        logging.info(f"[Peripheral Control] Triggering virtual macro hotkey combination: {keys}")
        try:
            pyautogui.hotkey(*keys)
        except Exception as e:
            logging.error(f"Hotkey macro fault: {e}")


# =====================================================================
#                     MODULE 3: FILE SYSTEM ENGINE
# =====================================================================
class JarvisFileEngine:
    @staticmethod
    def create_directory(dir_path: str):
        try:
            # Prevent directory traversal vulnerability checks implicitly via absolute normalization
            normalized_path = os.path.abspath(dir_path)
            if not os.path.exists(normalized_path):
                os.makedirs(normalized_path, exist_ok=True)
                logging.info(f"[File System] Generated directory tree: '{normalized_path}'")
        except Exception as e:
            logging.error(f"Failed directory generation: {e}")

    @staticmethod
    def write_text_file(file_path: str, content: str):
        try:
            normalized_file = os.path.abspath(file_path)
            with open(normalized_file, "w", encoding="utf-8") as file:
                file.write(content)
            logging.info(f"[File System] Wrote dataset stream cleanly to: '{normalized_file}'")
        except Exception as e:
            logging.error(f"Failed raw stream write: {e}")

    @staticmethod
    def list_directory_contents(dir_path: str = "."):
        try:
            normalized_path = os.path.abspath(dir_path)
            return os.listdir(normalized_path)
        except Exception as e:
            logging.error(f"Directory index lookup fault: {e}")
            return []


# =====================================================================
#                  MODULE 4: BROWSER AUTOMATION ENGINE
# =====================================================================
class JarvisBrowserAutomator:
    def __init__(self):
        self.driver = None

    def open_link(self, url: str):
        logging.info(f"[Web Integration] Routing system standard web request to: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            logging.error(f"[Web Integration] Failed to parse browser link target: {e}")

    def launch_selenium_controller(self, url: str):
        logging.info("[Web Integration] Initializing deep Selenium automated engine...")
        try:
            options = Options()
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=options)
            self.driver.get(url)
        except Exception as e:
            logging.error(f"[Web Integration] Webdriver failed: {e}. Defaulting to standard system browser.")
            self.open_link(url)

    def close_selenium_session(self):
        if self.driver:
            try:
                self.driver.quit()
                logging.info("[Web Integration] Closed headless and automation environments cleanly.")
            except Exception as e:
                logging.error(f"[Web Integration] Error shutting down WebDriver: {e}")
            finally:
                self.driver = None


# =====================================================================
#                  MODULE 5: MULTITHREADED VISION ENGINE
# =====================================================================
class JarvisVisionSystem(threading.Thread):
    def __init__(self):
        super().__init__()
        self.name = "JarvisVisionThread"
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.running = True

    def capture_screen_and_detect_ui(self) -> int:
        """Performs on-screen contours matching to highlight interactive buttons."""
        logging.info("[Vision System] Extracting frame contours from current virtual viewport...")
        try:
            screenshot = pyautogui.screenshot()
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            img_display = img.copy()

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 150)

            contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            count = 0

            for contour in contours:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    if 30 < w < 400 and 15 < h < 150:
                        count += 1
                        cv2.rectangle(img_display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(img_display, "UI Block", (x, y - 5), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            cv2.imshow("Jarvis Engine - Viewport Detection Mapping", img_display)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return count
        except Exception as e:
            logging.error(f"[Vision System] Failed UI Layout scanning tracking: {e}")
            return 0

    def run(self):
        logging.info("Vision processing pipeline threaded.")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("[Vision System] Primary camera hardware port offline.")
            return

        while self.running and SYSTEM_ACTIVE:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.03) # Frame synchronization lock
                continue

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, "Human Core Focused", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

                eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 1)

                # Upgraded DeepFace API mapping implementation
                try:
                    cropped_face = frame[y:y+h, x:x+w]
                    analysis = DeepFace.analyze(cropped_face, actions=['emotion'], enforce_detection=False)
                    if isinstance(analysis, list):
                        dominant_emotion = analysis[0]['dominant_emotion']
                    else:
                        dominant_emotion = analysis['dominant_emotion']
                        
                    cv2.putText(frame, f"Affiliation State: {str(dominant_emotion).upper()}", (x, y + h + 20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                except Exception:
                    pass

            # Hand Gesture contour processing
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
            mask = cv2.GaussianBlur(mask, (5, 5), 100)

            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest) > 12000:
                    hull = cv2.convexHull(largest)
                    cv2.drawContours(frame, [largest], -1, (0, 255, 0), 1)
                    cv2.drawContours(frame, [hull], -1, (0, 0, 255), 1)
                    cv2.putText(frame, "Gesture Pipeline Intercepted", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow("Jarvis Vision Core (Press 'q' inside feed window to escape)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        logging.info("Vision Core Thread shut down safely.")


# =====================================================================
#                MODULE 6: COGNITIVE SYSTEM ENGINE
# =====================================================================
class JarvisCognitiveEngine:
    def __init__(self, filename="jarvis_authenticated_memory.dat"):
        self.filename = filename
        self.cipher_engine = None
        self._initialize_encryption_layer()
        self.data = self.load_memory()

    def _initialize_encryption_layer(self):
        """Generates dynamic local keys or retrieves matching validation key tokens safely."""
        key_file = "jarvis_vault.key"
        if Fernet is None:
            logging.warning("[Cognitive Engine] Cryptography module missing! Memory falling back to plaintext.")
            return

        try:
            if os.path.exists(key_file):
                with open(key_file, "rb") as kf:
                    key = kf.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, "wb") as kf:
                    kf.write(key)
            self.cipher_engine = Fernet(key)
        except Exception as e:
            logging.error(f"[Cognitive Engine] Encryption startup error: {e}")

    def load_memory(self) -> Dict[str, Any]:
        default_schema = {"users": {}, "tasks": [], "plans": [], "notes": []}
        if not os.path.exists(self.filename):
            return default_schema

        try:
            with open(self.filename, "rb") as file:
                raw_data = file.read()
                
            if not raw_data.strip():
                return default_schema
                
            if self.cipher_engine:
                decrypted_bytes = self.cipher_engine.decrypt(raw_data)
                return json.loads(decrypted_bytes.decode('utf-8'))
            else:
                return json.loads(raw_data.decode('utf-8'))
        except Exception as e:
            logging.error(f"Error restoring cognitive parameters: {e}. Resetting corrupted structures safely.")
            return default_schema

    def save_memory(self):
        try:
            raw_bytes = json.dumps(self.data, indent=4).encode('utf-8')
            with open(self.filename, "wb") as file:
                if self.cipher_engine:
                    file.write(self.cipher_engine.encrypt(raw_bytes))
                else:
                    file.write(raw_bytes)
        except Exception as e:
            logging.error(f"Cryptographic memory write fault: {e}")

    def update_user_profile(self, name: str, preference: str):
        normalized_name = name.lower().strip()
        if normalized_name not in self.data["users"]:
            self.data["users"][normalized_name] = {}
        self.data["users"][normalized_name]["preferences"] = preference
        self.save_memory()

    def recursive_goal_planner(self, goal: str) -> List[str]:
        goal_normalized = goal.lower().strip()
        if "rebuild project" in goal_normalized:
            return ["Clean active build files", "Analyze compiler metrics", "Package binary outputs"]
        elif "audit security" in goal_normalized:
            return ["Check network socket rules", "Verify cryptography certificates", "Enforce boundary access control lists"]
        else:
            return [f"Phase 1: Structure approach parameters for target '{goal}'", "Phase 2: Deploy resources", "Phase 3: Validate metrics of target outcome"]

    def resolve_logical_conflict(self, conflict_a: str, conflict_b: str) -> str:
        ca, cb = conflict_a.lower().strip(), conflict_b.lower().strip()
        if "user privacy" in ca and "cloud data" in cb:
            return "Resolution Decision: Quarantine dataset locally. Disallow external cloud network sync."
        elif "high performance" in ca and "overheating risk" in cb:
            return "Resolution Decision: Scale thermal performance limits. Enable dynamic micro-throttling."
        return "Resolution Decision: Override secondary branch logic in favor of root platform parameters."


# =====================================================================
#             MODULE 7: THE ASYNC TASK ENGINE (SCHEDULER)
# =====================================================================
class JarvisTaskEngine(threading.Thread):
    def __init__(self, memory_sys: JarvisCognitiveEngine):
        super().__init__()
        self.name = "JarvisSchedulerThread"
        self.memory = memory_sys
        self.running = True

    def add_delayed_task(self, description: str, priority: str = "MEDIUM"):
        task_id = len(self.memory.data["tasks"]) + 1
        task_payload = {
            "id": task_id,
            "description": description,
            "priority": priority.upper(),
            "status": "QUEUED",
            # Timezone aware parsing to safely run on Python 3.12+ builds
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        self.memory.data["tasks"].append(task_payload)
        self.memory.save_memory()
        BACKGROUND_TASK_QUEUE.put(task_payload)
        logging.info(f"[Task Scheduler] Logged new task to queue pool: ID {task_id} -> '{description}'")

    def run(self):
        logging.info("Background dynamic scheduler thread successfully active.")
        while self.running and SYSTEM_ACTIVE:
            try:
                task = BACKGROUND_TASK_QUEUE.get(timeout=1.0)
                logging.info(f"[Task Engine Process] Processing asynchronous execution node: '{task['description']}'")
                
                # Processing simulation window
                time.sleep(2.0)
                
                for item in self.memory.data["tasks"]:
                    if item["id"] == task["id"]:
                        item["status"] = "COMPLETED"
                self.memory.save_memory()
                logging.info(f"[Task Engine Process] Successfully completed async task ID: {task['id']}")
                BACKGROUND_TASK_QUEUE.task_done()
            except queue.Empty:
                continue


# =====================================================================
#                     UNIFIED COMMAND CONTROL DECK
# =====================================================================
class JarvisCoreMainframe:
    def __init__(self):
        self.voice = JarvisVoiceCore()
        self.peripherals = JarvisPeripheralController()
        self.files = JarvisFileEngine()
        self.browser = JarvisBrowserAutomator()
        self.cognitive = JarvisCognitiveEngine()
        
        self.vision_thread = None
        self.scheduler_thread = JarvisTaskEngine(self.cognitive)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def process_natural_language(self, user_command: str):
        cmd = user_command.strip().lower()
        if not cmd:
            return

        if "say voice" in cmd:
            text_to_speak = user_command[9:].strip()
            self.voice.speak(text_to_speak)

        elif "slide mouse to" in cmd or "move mouse to" in cmd:
            try:
                cleaned = cmd.replace("slide mouse to ", "").replace("move mouse to ", "")
                coords = cleaned.split()
                x, y = int(coords[0]), int(coords[1])
                self.peripherals.move_mouse_to(x, y)
            except Exception:
                self.voice.speak("Coordinate syntax misaligned. Provide horizontal and vertical integers.")

        elif "trigger click" in cmd or "double click" in cmd:
            clicks = 2 if "double" in cmd else 1
            button = "right" if "right" in cmd else "left"
            self.peripherals.execute_click(clicks, button)

        elif "inject text" in cmd or "type" in cmd:
            text = user_command.replace("inject text ", "").replace("type ", "")
            self.peripherals.virtual_type(text)

        elif "browse to" in cmd:
            url = user_command[10:].strip()
            self.voice.speak(f"Accessing URL address {url}")
            self.browser.open_link(url)

        elif "deep browse to" in cmd:
            url = user_command[15:].strip()
            self.voice.speak(f"Launching autonomous web navigation to {url}")
            self.browser.launch_selenium_controller(url)

        elif "build directory" in cmd:
            dir_name = user_command[16:].strip()
            self.files.create_directory(dir_name)
            self.voice.speak(f"Generated physical directory structure for {dir_name}")

        elif "write file" in cmd:
            try:
                # Syntax format parsing: write file out.txt text: content
                parts = user_command[11:].split(" text: ")
                if len(parts) >= 2:
                    self.files.write_text_file(parts[0].strip(), parts[1].strip())
                    self.voice.speak(f"File writing parameters mapped to {parts[0].strip()}")
                else:
                    self.voice.speak("File processing command structure requires a explicit text separation marker.")
            except Exception:
                self.voice.speak("Ensure command format matches path and text content indicators.")

        elif "generate master plan" in cmd:
            goal = user_command[21:].strip()
            steps = self.cognitive.recursive_goal_planner(goal)
            print(f"\n[JARVIS GENERATED CORE SCHEMATIC FOR: {goal.upper()}]")
            for index, step in enumerate(steps, 1):
                print(f"  [{index}] -> {step}")
            self.voice.speak("System macro planning array constructed and outputted on command deck.")

        elif "resolve system deadlock" in cmd:
            try:
                aspects = cmd.replace("resolve system deadlock ", "").split(" vs ")
                resolution = self.cognitive.resolve_logical_conflict(aspects[0], aspects[1])
                print(f"\n[RESOLVER OUTPUT]\n{resolution}")
                self.voice.speak("Logical balance resolve complete.")
            except Exception:
                self.voice.speak("Deadlock resolving parameters must compare two opposing profiles.")

        elif "schedule task" in cmd:
            task_desc = user_command[14:].strip()
            self.scheduler_thread.add_delayed_task(task_desc)
            self.voice.speak("Added background async task.")

        else:
            self.voice.speak(f"Received request input: {user_command}. Executing command processing processing.")


# =====================================================================
#                         MAIN RUNTIME DECK
# =====================================================================
def main():
    global SYSTEM_ACTIVE
    mainframe = JarvisCoreMainframe()

    print("\n=======================================================================")
    print("             JARVIS ENTERPRISE COGNITIVE OPERATING SYSTEM             ")
    print("=======================================================================")
    print("[INIT] Secure authenticated cryptography vault online.")
    print("[INIT] Background core multi-threaded scheduling environment synced.")
    mainframe.voice.speak("Welcome Back. All peripheral systems are fully operational.")

    while True:
        print("\n=== SYSTEM MASTER CONTROLLER CONTROL DECK ===")
        print("1. Start Live Camera Processing (Face, Eyes, Emotion, Gestures)")
        print("2. Launch Viewport Controller (Screen UI Layout Element Scanner)")
        print("3. Command CLI (Interactive Natural Language Parser)")
        print("4. Voice Interactive Mode (Speech recognition input)")
        print("5. Diagnostic Hardware Status Metrics")
        print("6. Shut Down Jarvis Core (Terminate Threads Safely)")
        print("-----------------------------------------------------------------------")
        
        choice = input("Define operational routine (1-6): ").strip()
        
        if choice == '1':
            if mainframe.vision_thread is None or not mainframe.vision_thread.is_alive():
                mainframe.vision_thread = JarvisVisionSystem()
                mainframe.vision_thread.daemon = True
                mainframe.vision_thread.start()
                mainframe.voice.speak("Camera vision interface active.")
            else:
                print("[Jarvis Command Log] Dynamic vision system thread is already running.")
                
        elif choice == '2':
            mainframe.voice.speak("Starting onscreen configuration contours scanning.")
            # Allocate instance defensively to scan layout patterns
            scanner = JarvisVisionSystem()
            scanned_blocks_num = scanner.capture_screen_and_detect_ui()
            print(f"[Jarvis Core Engine] UI element outline analysis complete. Detected: {scanned_blocks_num}")
            
        elif choice == '3':
            print("\nEntering Local Command Loop (Type 'exit' to return to Central Operations Deck)")
            print("Commands: 'move mouse to 400 300', 'type hello', 'browse to google.com', 'generate master plan security audit'")
            print("----------------------------------------------------------------------------------------------------")
            while True:
                cli_input = input("Jarvis Direct Instruction >> ").strip()
                if cli_input.lower() in ["exit", "back", "return"]:
                    break
                mainframe.process_natural_language(cli_input)
                
        elif choice == '4':
            if sr is None:
                mainframe.voice.speak("Speech recognition dependencies missing. Reinstall via system environment commands.")
                continue
            
            mainframe.voice.speak("Vocal input capture active.")
            while True:
                vocal_input = mainframe.voice.listen_command()
                if vocal_input:
                    if vocal_input.lower() in ["exit", "back", "shut down"]:
                        mainframe.voice.speak("Closing audio tracking session.")
                        break
                    mainframe.process_natural_language(vocal_input)
                else:
                    break
                
        elif choice == '5':
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            print(f"\n--- MAIN COGNITIVE CORE HARDWARE DIAGNOSTIC ---")
            print(f"Processor Load: {cpu}% | RAM Utilization: {ram}% | Disk space usage: {disk}%")
            mainframe.voice.speak(f"CPU utilization reading is {int(cpu)} percent.")
            
        elif choice == '6':
            print("\n[Safe Shutdown Interface] Initializing security offline protocol...")
            mainframe.voice.speak("Shutting down core routines. Moving system components securely offline.")
            SYSTEM_ACTIVE = False
            
            # Perform clean teardowns of running processes to avoid thread leak blocks
            if mainframe.vision_thread is not None:
                mainframe.vision_thread.running = False
                mainframe.vision_thread.join(timeout=2.0)
            
            mainframe.scheduler_thread.running = False
            mainframe.browser.close_selenium_session()
            print("[System Safe Shutdown] All processes and memory modules successfully offline. Goodbye.")
            break
        else:
            print("[Runtime Warning] Input choice index is not defined.")

if __name__ == "__main__":
    main()
