import cv2
import numpy as np
import pyautogui
from deepface import DeepFace
import time
import json
import os
import sys
import shutil
import webbrowser
import threading
import queue
import logging
from datetime import datetime
import psutil
from selenium import webdriver

# Optional Advanced Libraries with Graceful Fallbacks
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# =====================================================================
#                        GLOBAL LOGGING & QUEUE SYSTEM
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s",
    handlers=[
        logging.FileHandler("jarvis_mainframe.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

system_active = True
background_task_queue = queue.Queue()

# =====================================================================
#                  MODULE 1: VOICE & AUDIO SUBSYSTEM
# =====================================================================
class JarvisVoiceCore:
    def __init__(self):
        self.speech_engine = None
        self.recognizer = None
        self.mic = None
        
        # Initialize Text-to-Speech Engine
        if pyttsx3:
            try:
                self.speech_engine = pyttsx3.init()
                # Fine-tune vocal parameters (180 words per minute, neutral volume)
                self.speech_engine.setProperty('rate', 175)
                self.speech_engine.setProperty('volume', 0.9)
                logging.info("[Audio Engine] PyTTSx3 voice synthesis system successfully mapped.")
            except Exception as e:
                logging.warning(f"[Audio Engine] Voice synthesis failed to initialize: {e}")
        
        # Initialize Speech Recognition
        if sr:
            try:
                self.recognizer = sr.Recognizer()
                self.mic = sr.Microphone()
                logging.info("[Audio Engine] Speech Recognition interfaces operational.")
            except Exception as e:
                logging.warning(f"[Audio Engine] Microphone access failed: {e}")

    def speak(self, text: str):
        """Generates clear synthetic voice feedback synchronously."""
        logging.info(f"[Jarvis Audio] Vocalizing: '{text}'")
        if self.speech_engine:
            # Run in a loop-safe manner to prevent runtime collision with background loops
            self.speech_engine.say(text)
            self.speech_engine.runAndWait()
        else:
            print(f"\n[Jarvis Voice Emulation]: {text}")

    def listen_command(self) -> str:
        """Listens to ambient audio and translates it to clear string commands."""
        if not self.recognizer or not self.mic:
            logging.warning("[Audio Engine] Voice input requested but interface is offline.")
            return ""

        with self.mic as source:
            logging.info("[Audio Engine] Calibration for ambient room noise levels...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print("\n[Jarvis Engine] Listening for vocal command... Speak now.")
            try:
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
        pyautogui.FAILSAFE = True  # Drag mouse to any of the 4 screen corners to kill automation instantly
        pyautogui.PAUSE = 0.05

    def move_mouse_to(self, x: int, y: int, duration: float = 0.4):
        logging.info(f"[Peripheral Control] Cursor translation to X={x}, Y={y}")
        try:
            pyautogui.moveTo(x, y, duration=duration)
        except Exception as e:
            logging.error(f"Mouse movement fault: {e}")

    def execute_click(self, clicks: int = 1, button: str = 'left'):
        logging.info(f"[Peripheral Control] Triggering click: [{button}] x{clicks}")
        try:
            pyautogui.click(clicks=clicks, button=button)
        except Exception as e:
            logging.error(f"Mouse interaction fault: {e}")

    def virtual_type(self, text: str, delay: float = 0.03):
        logging.info(f"[Peripheral Control] Generating physical keystrokes: '{text}'")
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
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logging.info(f"[File System] Generated directory tree: '{dir_path}'")
        except Exception as e:
            logging.error(f"Failed directory generation: {e}")

    @staticmethod
    def write_text_file(file_path: str, content: str):
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            logging.info(f"[File System] Wrote dataset stream cleanly to: '{file_path}'")
        except Exception as e:
            logging.error(f"Failed raw stream write: {e}")

    @staticmethod
    def list_directory_contents(dir_path: str = "."):
        try:
            return os.listdir(dir_path)
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
        webbrowser.open(url)

    def launch_selenium_controller(self, url: str):
        logging.info("[Web Integration] Initializing deep Selenium automated engine...")
        try:
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            self.driver = webdriver.Chrome(options=options)
            self.driver.get(url)
        except Exception as e:
            logging.error(f"[Web Integration] Webdriver failed: {e}. Defaulting to standard system browser.")
            self.open_link(url)

    def close_selenium_session(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            logging.info("[Web Integration] Closed headless and automation environments cleanly.")


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
        self.detect_ui = False  # Set to True internally via control deck to analyze screen UI

    def capture_screen_and_detect_ui(self) -> int:
        """Performs on-screen contours matching to highlight interactive buttons."""
        logging.info("[Vision System] Extracting frame contours from current virtual viewport...")
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

    def run(self):
        logging.info("Vision processing pipeline threaded.")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("[Vision System] Primary camera hardware port offline.")
            return

        while self.running and system_active:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Face, Eye and Deep Emotion pipeline
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, "Human Core Focused", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

                # Target search optimized inside face bounding boundaries
                eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 1)

                try:
                    cropped_face = frame[y:y+h, x:x+w]
                    analysis = DeepFace.analyze(cropped_face, actions=['emotion'], enforce_detection=False)
                    dominant_emotion = analysis[0]['dominant_emotion']
                    cv2.putText(frame, f"Affiliation State: {dominant_emotion.upper()}", (x, y + h + 20), 
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
    def __init__(self, filename="jarvis_secure_memory.json"):
        self.filename = filename
        self.key = 42  # Simplified mathematical symmetric encryption
        self.data = self.load_memory()

    def _xor_cipher(self, data_str: str) -> str:
        return "".join(chr(ord(char) ^ self.key) for char in data_str)

    def load_memory(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as file:
                    encrypted_content = file.read()
                    if not encrypted_content.strip():
                        return {"users": {}, "tasks": [], "plans": [], "notes": []}
                    return json.loads(self._xor_cipher(encrypted_content))
            except Exception as e:
                logging.error(f"Error restoring cognitive parameters: {e}")
        return {"users": {}, "tasks": [], "plans": [], "notes": []}

    def save_memory(self):
        try:
            raw_json = json.dumps(self.data, indent=4)
            with open(self.filename, "w") as file:
                file.write(self._xor_cipher(raw_json))
        except Exception as e:
            logging.error(f"Cryptographic memory write fault: {e}")

    def update_user_profile(self, name: str, preference: str):
        name = name.lower()
        if name not in self.data["users"]:
            self.data["users"][name] = {}
        self.data["users"][name]["preferences"] = preference
        self.save_memory()

    def recursive_goal_planner(self, goal: str) -> list:
        """Heuristically segments high-level goals into granular steps."""
        goal_normalized = goal.lower()
        if "rebuild project" in goal_normalized:
            return ["Clean active build files", "Analyze compiler metrics", "Package binary outputs"]
        elif "audit security" in goal_normalized:
            return ["Check network socket rules", "Verify cryptography certificates", "Enforce boundary access control lists"]
        else:
            return [f"Phase 1: Structure approach parameters for target '{goal}'", "Phase 2: Deploy resources", "Phase 3: Validate metrics of target outcome"]

    def resolve_logical_conflict(self, conflict_a: str, conflict_b: str) -> str:
        """Resolves system state priority issues using logical rule hierarchies."""
        ca, cb = conflict_a.lower(), conflict_b.lower()
        if "user privacy" in ca and "cloud data" in cb:
            return "Resolution Decision: Quarantine dataset locally. Disallow external cloud network sync."
        elif "high performance" in ca and "overheating risk" in cb:
            return "Resolution Decision: Scale thermal performance limits. Enable dynamic micro-throttling."
        return "Resolution Decision: Override secondary branch logic in favor of root platform parameters."


# =====================================================================
#             MODULE 7: THE ASYNC TASK ENGINE (SCHEDULER)
# =====================================================================
class JarvisTaskEngine(threading.Thread):
    def __init__(self, memory_sys):
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
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.memory.data["tasks"].append(task_payload)
        self.memory.save_memory()
        background_task_queue.put(task_payload)
        logging.info(f"[Task Scheduler] Logged new task to queue pool: ID {task_id} -> '{description}'")

    def run(self):
        logging.info("Background dynamic scheduler thread successfully active.")
        while self.running and system_active:
            try:
                # Process background event loops asynchronously without lagging main CLI thread
                task = background_task_queue.get(timeout=2)
                logging.info(f"[Task Engine Process] Processing asynchronous execution node: '{task['description']}'")
                
                # Simulate core run cycles
                time.sleep(3)
                
                for item in self.memory.data["tasks"]:
                    if item["id"] == task["id"]:
                        item["status"] = "COMPLETED"
                self.memory.save_memory()
                logging.info(f"[Task Engine Process] Successfully completed async task ID: {task['id']}")
                background_task_queue.task_done()
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
        
        # Threads
        self.vision_thread = None
        self.scheduler_thread = JarvisTaskEngine(self.cognitive)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def process_natural_language(self, user_command: str):
        cmd = user_command.strip().lower()
        if not cmd:
            return

        # Voice commands
        if "say voice" in cmd:
            text_to_speak = user_command.replace("say voice ", "")
            self.voice.speak(text_to_speak)

        # Mouse & Keyboard peripheral commands
        elif "slide mouse to" in cmd or "move mouse to" in cmd:
            try:
                coords = cmd.replace("slide mouse to ", "").replace("move mouse to ", "").split()
                x, y = int(coords[0]), int(coords[1])
                self.peripherals.move_mouse_to(x, y)
            except Exception:
                self.voice.speak("Coordinate syntax misaligned. Provide horizontal and vertical points.")

        elif "trigger click" in cmd or "double click" in cmd:
            clicks = 2 if "double" in cmd else 1
            button = "right" if "right" in cmd else "left"
            self.peripherals.execute_click(clicks, button)

        elif "inject text" in cmd or "type" in cmd:
            text = user_command.replace("inject text ", "").replace("type ", "")
            self.peripherals.virtual_type(text)

        # Browser Automation
        elif "browse to" in cmd:
            url = cmd.split("browse to ")[1].strip()
            self.voice.speak(f"Accessing URL address {url}")
            self.browser.open_link(url)

        elif "deep browse to" in cmd:
            url = cmd.split("deep browse to ")[1].strip()
            self.voice.speak(f"Launching autonomous web navigation to {url}")
            self.browser.launch_selenium_controller(url)

        # File Management
        elif "build directory" in cmd:
            dir_name = cmd.split("build directory ")[1].strip()
            self.files.create_directory(dir_name)
            self.voice.speak(f"Generated physical directory structure for {dir_name}")

        elif "write file" in cmd:
            try:
                # Syntax: write file out.txt text: hello world
                parts = user_command.split("write file ")[1].split(" text: ")
                self.files.write_text_file(parts[0].strip(), parts[1].strip())
                self.voice.speak(f"File writing parameters mapped to {parts[0].strip()}")
            except Exception:
                self.voice.speak("Ensure command format matches path and text content indicators.")

        # Planning & Reasoning Engines
        elif "generate master plan" in cmd:
            goal = user_command.replace("generate master plan ", "")
            steps = self.cognitive.recursive_goal_planner(goal)
            print(f"\n[JARVIS GENERATED CORE SCHEMATIC FOR: {goal.upper()}]")
            for index, step in enumerate(steps, 1):
                print(f"  [{index}] -> {step}")
            self.voice.speak("System macro planning array constructed and outputted on command deck.")

        elif "resolve system deadlock" in cmd:
            try:
                # Syntax: resolve system deadlock security vs performance
                aspects = cmd.replace("resolve system deadlock ", "").split(" vs ")
                resolution = self.cognitive.resolve_logical_conflict(aspects[0], aspects[1])
                print(f"\n[RESOLVER OUTPUT]\n{resolution}")
                self.voice.speak("Logical balance resolve complete.")
            except Exception:
                self.voice.speak("Deadlock resolving parameters must compare two opposing profiles.")

        # Asynchronous Scheduled Task Management
        elif "schedule task" in cmd:
            task_desc = user_command.replace("schedule task ", "")
            self.scheduler_thread.add_delayed_task(task_desc)
            self.voice.speak("Added background async task.")

        else:
            self.voice.speak(f"Recieved request input: {user_command}. Executing command processing.")


# =====================================================================
#                         MAIN RUNTIME DECK
# =====================================================================
def main():
    global system_active
    mainframe = JarvisCoreMainframe()

    print("\n=======================================================================")
    print("             JARVIS ENTERPRISE COGNITIVE OPERATING SYSTEM             ")
    print("=======================================================================")
    print("Diagnostics: Secure encrypted memory loop online.")
    print("Diagnostics: Background multi-threaded scheduling thread online.")
    mainframe.voice.speak("Welcome Back. All peripheral systems are fully synced.")

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
            mainframe.voice.speak("Starting on screen button and menu contour scanning. Please keep the target area clear.")
            scanned_blocks_num = JarvisVisionSystem().capture_screen_and_detect_ui()
            print(f"[Jarvis Core Engine] UI element outline analysis complete. Detected potential elements: {scanned_blocks_num}")
            
        elif choice == '3':
            print("\nEntering Local Command Loop (Type 'exit' to return to Central Operations Deck)")
            print("Commands: 'move mouse to 400 300', 'type [text]', 'browse to [url]', 'write file test.txt text: [content]', 'generate master plan [goal]'")
            print("----------------------------------------------------------------------------------------------------")
            while True:
                cli_input = input("Jarvis Direct Instruction >> ").strip()
                if cli_input.lower() in ["exit", "back", "return"]:
                    break
                mainframe.process_natural_language(cli_input)
                
        elif choice == '4':
            if sr is None:
                mainframe.voice.speak("Speech recognition dependencies missing. Reinstall via Pip command options.")
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
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            print(f"\n--- MAIN COGNITIVE CORE HARDWARE DIAGNOSTIC ---")
            print(f"System Microprocessor Core Load: {cpu}% | Virtual Cache Allocation: {ram}% | Storage capacity: {disk}%")
            mainframe.voice.speak(f"CPU utilization reading is {int(cpu)} percent.")
            
        elif choice == '6':
            print("\n[Safe Shutdown Interface] Initializing security offline protocol...")
            mainframe.voice.speak("Shutting down core routines. Moving system components securely offline.")
            system_active = False
            
            # Safely shut down background loops
            if mainframe.vision_thread is not None:
                mainframe.vision_thread.running = False
                mainframe.vision_thread.join()
            
            mainframe.scheduler_thread.running = False
            mainframe.browser.close_selenium_session()
            print("[System Safe Shutdown] All processes and memory modules successfully offline. Goodbye.")
            break
        else:
            print("[Runtime Warning] Input choice index is not defined.")

if __name__ == "__main__":
    main()
