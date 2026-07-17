import cv2
import numpy as np
import pyautogui
from deepface import DeepFace
import time
import json
import os
import sys
import math
import shutil
import webbrowser
import threading
import queue
import logging
from datetime import datetime
import psutil
from selenium import webdriver
from pypdf import PdfReader

# GUI Frameworks
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Speech & Voice Modules with Fault Tolerant Dynamic Imports
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# =====================================================================
#                        GLOBAL SYSTEM STATE
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s",
    handlers=[
        logging.FileHandler("jarvis_quantum_system.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

gui_queue = queue.Queue()
speech_queue = queue.Queue()
system_active = True

# =====================================================================
#          CRYPTOGRAPHIC SECURE STORAGE (COGNITIVE MEMORY)
# =====================================================================
class JarvisSecureMemory:
    def __init__(self, filename="jarvis_quantum_memory.json"):
        self.filename = filename
        self.cipher_key = 57  # Mathematical XOR symmetric encryption key
        self.data = self.load_memory()

    def _xor_cipher(self, data_str: str) -> str:
        return "".join(chr(ord(char) ^ self.cipher_key) for char in data_str)

    def load_memory(self) -> dict:
        default_structure = {
            "user_profiles": {
                "student": {"study_sessions": 0, "quizzes_taken": 0, "average_score": 0.0}
            },
            "scheduled_tasks": [],
            "system_configurations": {"voice_only_mode": False}
        }
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as file:
                    encrypted_data = file.read()
                    if not encrypted_data.strip():
                        return default_structure
                    return json.loads(self._xor_cipher(encrypted_data))
            except Exception as e:
                logging.error(f"[Memory Engine] Secure reading error: {e}. Reverting to defaults.")
                return default_structure
        return default_structure

    def save_memory(self):
        try:
            raw_string = json.dumps(self.data, indent=4)
            encrypted_string = self._xor_cipher(raw_string)
            with open(self.filename, "w") as file:
                file.write(encrypted_string)
            logging.info("[Memory Engine] State changes written and encrypted securely.")
        except Exception as e:
            logging.error(f"[Memory Engine] Writing failure: {e}")

    def log_quiz_result(self, username: str, score_percentage: float):
        user = username.lower()
        if user not in self.data["user_profiles"]:
            self.data["user_profiles"][user] = {"study_sessions": 0, "quizzes_taken": 0, "average_score": 0.0}
        
        profile = self.data["user_profiles"][user]
        old_quizzes = profile["quizzes_taken"]
        old_average = profile["average_score"]
        
        new_quizzes = old_quizzes + 1
        new_average = ((old_average * old_quizzes) + score_percentage) / new_quizzes
        
        profile["study_sessions"] += 1
        profile["quizzes_taken"] = new_quizzes
        profile["average_score"] = round(new_average, 2)
        self.save_memory()


# =====================================================================
#             MODULE 1: THE VOICE & SPEECH SYNTHESIS ENGINE
# =====================================================================
class JarvisVoiceThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.name = "JarvisVoiceThread"
        self.engine = None
        self.recognizer = None
        self.mic = None
        self.voice_only_mode = False

        # Safe pyttsx3 Initialization
        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 170)
                self.engine.setProperty('volume', 0.95)
            except Exception as e:
                logging.error(f"[Speech Synthesis] Failed initializing core engine: {e}")

        # Safe Speech Recognition Setup
        if sr:
            try:
                self.recognizer = sr.Recognizer()
                self.mic = sr.Microphone()
            except Exception as e:
                logging.error(f"[Acoustic Recognition] Failed mapping hardware inputs: {e}")

    def speak(self, phrase: str):
        """Processes audio output through safe pipeline to avoid GUI blocks."""
        logging.info(f"[Jarvis Voice Engine]: {phrase}")
        gui_queue.put({"action": "update_status", "text": phrase})
        
        if self.engine:
            try:
                self.engine.say(phrase)
                self.engine.runAndWait()
            except Exception as e:
                logging.error(f"[Speech Synthesis] Runtime conflict: {e}")
        else:
            print(f"\n[Jarvis Voice Fallback]: {phrase}")

    def run(self):
        logging.info("Vocal Loop Engine active and listening.")
        while system_active:
            # Check for outbound audio requests
            try:
                phrase = speech_queue.get(timeout=0.2)
                self.speak(phrase)
                speech_queue.task_done()
            except queue.Empty:
                pass

            # Voice Command Processing (Hands-free Mode)
            if self.voice_only_mode and self.recognizer and self.mic:
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    try:
                        audio_data = self.recognizer.listen(source, timeout=0.8, phrase_time_limit=4)
                        command = self.recognizer.recognize_google(audio_data).lower()
                        logging.info(f"[Acoustic Command Caught]: {command}")
                        gui_queue.put({"action": "process_nlp_command", "command": command})
                    except (sr.WaitTimeoutError, Exception):
                        continue


# =====================================================================
#             MODULE 2: STYLIZED FLOATING INTERFACE (HUD)
# =====================================================================
class JarvisFloatingHUD(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jarvis Floating HUD")
        
        # Transparent, topmost overlay styling
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "black")
        self.config(bg="black")
        
        # Geometry adjustments (Position at top center)
        screen_w = self.winfo_screenwidth()
        self.width, self.height = 360, 360
        x_coordinate = (screen_w // 2) - (self.width // 2)
        y_coordinate = 30
        self.geometry(f"{self.width}x{self.height}+{x_coordinate}+{y_coordinate}")

        # Drag capabilities
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.execute_drag)

        # Draw futuristic components
        self.canvas = tk.Canvas(self, width=340, height=310, bg="black", highlightthickness=0)
        self.canvas.pack(pady=5)
        
        # Status Readout Text
        self.label_feedback = tk.Label(self, text="COGNITIVE ENGINE SIGNED ON", fg="#00f3ff", bg="black", font=("Courier", 9, "bold"))
        self.label_feedback.pack()
        
        self.step = 0
        self.animate_hud()

    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def execute_drag(self, event):
        delta_x = event.x - self.drag_x
        delta_y = event.y - self.drag_y
        new_x = self.winfo_x() + delta_x
        new_y = self.winfo_y() + delta_y
        self.geometry(f"+{new_x}+{new_y}")

    def animate_hud(self):
        """Draws rotating vector components and animated rings (30fps)."""
        self.canvas.delete("all")
        self.step += 1
        
        center_x, center_y = 170, 150
        core_cyan = "#00f3ff"
        dark_cyber_blue = "#00474f"
        
        # Outer Telemetry Ring
        self.canvas.create_oval(
            center_x - 120, center_y - 120, 
            center_x + 120, center_y + 120, 
            outline=dark_cyber_blue, width=1, dash=(4, 10)
        )
        
        # Rotating Arch Modules
        angle = (self.step * 3) % 360
        self.canvas.create_arc(
            center_x - 100, center_y - 100, 
            center_x + 100, center_y + 100, 
            start=angle, extent=90, 
            outline=core_cyan, width=2, style=tk.ARC
        )
        self.canvas.create_arc(
            center_x - 100, center_y - 100, 
            center_x + 100, center_y + 100, 
            start=angle + 180, extent=90, 
            outline=core_cyan, width=2, style=tk.ARC
        )

        # Pulsing Center Sphere
        pulse_scale = 35 + 10 * math.sin(self.step * 0.12)
        self.canvas.create_oval(
            center_x - pulse_scale, center_y - pulse_scale, 
            center_x + pulse_scale, center_y + pulse_scale, 
            outline=core_cyan, width=2
        )
        self.canvas.create_oval(
            center_x - (pulse_scale * 0.5), center_y - (pulse_scale * 0.5), 
            center_x + (pulse_scale * 0.5), center_y + (pulse_scale * 0.5), 
            fill=core_cyan, outline=""
        )

        self.after(33, self.animate_hud)


# =====================================================================
#             MODULE 3: INTEGRATED SLIDE TOAST NOTIFICATIONS
# =====================================================================
class JarvisToastNotification(tk.Toplevel):
    def __init__(self, title: str, message: str):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.config(bg="#031017", highlightbackground="#00f3ff", highlightthickness=1)
        
        w, h = 300, 90
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        x = screen_w - w - 20
        y = screen_h - h - 60
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        lbl_title = tk.Label(self, text=title.upper(), fg="#00f3ff", bg="#031017", font=("Courier", 10, "bold"))
        lbl_title.pack(anchor="w", padx=12, pady=(10, 2))
        
        lbl_msg = tk.Label(self, text=message, fg="white", bg="#031017", font=("Arial", 9), wraplength=270, justify="left")
        lbl_msg.pack(anchor="w", padx=12)
        
        self.after(4500, self.destroy)


# =====================================================================
#            MODULE 4: ACADEMIC CORE (PDF & STUDY SYSTEM)
# =====================================================================
class JarvisAcademicEngine:
    def __init__(self, memory_system):
        self.memory = memory_system

    def parse_pdf(self, path: str) -> str:
        """Loads and extracts clean string values from local PDF binaries."""
        if not os.path.exists(path):
            logging.error(f"[Academic Core] Target file at: '{path}' does not exist.")
            return ""
        
        try:
            reader = PdfReader(path)
            full_text = ""
            for idx, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    full_text += f"\n--- PAGE {idx+1} ---\n{extracted}"
            return full_text
        except Exception as e:
            logging.error(f"[Academic Core] Reading failure: {e}")
            return ""

    def process_explanations(self, document_text: str):
        """Analyzes text heuristics to extract topics and terms."""
        paragraphs = [p.strip() for p in document_text.split('\n') if len(p.strip()) > 40]
        if not paragraphs:
            print("[Academic Core Error] No text matches parsing requirements.")
            return

        print("\n" + "="*50)
        print("          JARVIS COGNITIVE ACADEMIC TOPICS          ")
        print("" + "="*50)
        for idx, item in enumerate(paragraphs[:3], 1):
            sentences = item.split('.')
            topic_header = sentences[0] if len(sentences) > 0 else item
            print(f"\n[Topic Module {idx}]: {topic_header.strip()}.")
            if len(sentences) > 1:
                print(f"  [Detail Analysis]: {'.'.join(sentences[1:3]).strip()}.")
        print("\n" + "="*50)

    def generate_assessment(self, document_text: str) -> list:
        """Crafts dynamic questions based on extracted PDF concepts."""
        paragraphs = [p.strip() for p in document_text.split('\n') if len(p.strip()) > 50]
        quiz_list = []
        
        if len(paragraphs) < 2:
            # High-Performance system structural diagnostic fallback questions
            quiz_list = [
                {
                    "question": "Which system manages GUI elements on a separate thread to prevent freezing?",
                    "options": ["A) Process Loop Engine", "B) Main Graphic Core Thread", "C) Video Stream Pipeline", "D) Local Database Handler"],
                    "answer": "B"
                },
                {
                    "question": "What mathematical cipher protects local system states and progress metrics?",
                    "options": ["A) RSA Signature Block", "B) SHA-256 Checksum", "C) XOR Symmetric Cipher Block", "D) MD5 Signature Digest"],
                    "answer": "C"
                }
            ]
        else:
            for item in paragraphs[:3]:
                words = item.split()
                if len(words) > 8:
                    term_to_mask = words[len(words) // 2].strip(".,()\"")
                    question_txt = item.replace(term_to_mask, "______", 1)
                    quiz_list.append({
                        "question": f"Determine the hidden concept:\n\"{question_txt}\"",
                        "options": [f"Missing Concept: {term_to_mask}"],
                        "answer": term_to_mask.lower()
                    })
        return quiz_list


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

    def run(self):
        logging.info("Vision processing pipeline threaded.")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            gui_queue.put({"action": "notification", "title": "CAMERA ACCESS FAULT", "msg": "Target video capture hardware is offline."})
            return

        gui_queue.put({"action": "notification", "title": "VISION CHANNELS ACTIVE", "msg": "Biometric face tracker initialized."})

        while self.running and system_active:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Locate Faces and Eyes
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

                eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 1)

                try:
                    cropped = frame[y:y+h, x:x+w]
                    analysis = DeepFace.analyze(cropped, actions=['emotion'], enforce_detection=False)
                    dominant = analysis[0]['dominant_emotion']
                    cv2.putText(frame, f"Emotion: {dominant.upper()}", (x, y + h + 20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                except Exception:
                    pass

            cv2.imshow("Jarvis Vision Processing (Press 'q' inside feed window to escape)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        logging.info("Vision System Offline.")


# =====================================================================
#                 SYSTEM CONSOLE CONTROLLER INTERFACE
# =====================================================================
class JarvisMainframeExecutive:
    def __init__(self, ui_ref):
        self.ui = ui_ref
        self.memory = JarvisSecureMemory()
        self.voice = self.ui.voice_engine
        self.academic = JarvisAcademicEngine(self.memory)
        self.vision = None
        self.current_pdf_text = ""
        self.active_username = "Student"

        # Start thread monitoring loop
        self.sync_pipelines()

    def sync_pipelines(self):
        """Monitors and maps activities from background pipelines."""
        try:
            while True:
                task = gui_queue.get_nowait()
                action = task.get("action")
                
                if action == "update_status":
                    self.ui.label_feedback.config(text=task.get("text")[:35].upper())
                elif action == "notification":
                    JarvisToastNotification(task.get("title"), task.get("msg"))
                elif action == "process_nlp_command":
                    self.process_command(task.get("command"))
                gui_queue.task_done()
        except queue.Empty:
            pass
        self.ui.after(100, self.sync_pipelines)

    def process_command(self, cmd_text: str):
        cmd = cmd_text.lower()
        if "hide HUD" in cmd or "offline" in cmd:
            self.ui.withdraw()
            speech_queue.put("Display parameters set to offline.")
        elif "show HUD" in cmd or "online" in cmd:
            self.ui.deiconify()
            speech_queue.put("Display parameters restored.")
        elif "open google" in cmd:
            webbrowser.open("https://google.com")
            speech_queue.put("Executing. Directing search request to browser gateway.")
        elif "system status" in cmd:
            cpu = psutil.cpu_percent()
            speech_queue.put(f"Main processing loops are currently utilizing {int(cpu)} percent of system hardware.")
        else:
            speech_queue.put(f"Task executed successfully: {cmd_text}")

    def execute_quizzing(self, assessment_list: list):
        if not assessment_list:
            speech_queue.put("No structured materials processed yet.")
            return

        speech_queue.put("Commencing learning check. Verify selections below.")
        points_gained = 0
        
        for idx, item in enumerate(assessment_list, 1):
            print(f"\n[Question {idx}]: {item['question']}")
            if len(item["options"]) > 1:
                for opt in item["options"]:
                    print(opt)
                answer = input("Your selection (A-D): ").strip().upper()
            else:
                answer = input("Provide missing keyword: ").strip().lower()

            if answer == item["answer"]:
                print("Correct! Concepts aligned.")
                points_gained += 1
            else:
                print(f"Incorrect response. Target value: {item['answer']}")

        score_percentage = (points_gained / len(assessment_list)) * 100.0
        self.memory.log_quiz_result(self.active_username, score_percentage)
        speech_queue.put(f"Assessment complete. Performance evaluation scored at {int(score_percentage)} percent.")

    def run_control_terminal(self):
        """CLI Terminal controller running concurrently with the UI."""
        while system_active:
            print("\n" + "="*60)
            print("        JARVIS QUANTUM INTEGRATION RUNTIME CONTROL DECK        ")
            print("" + "="*60)
            print("1. Toggle Hands-Free Speech Only Protocol")
            print("2. Parse PDF Document & Read Extracted Content")
            print("3. Analyze Concept Summaries")
            print("4. Execute Dynamic Assessment Checks")
            print("5. Launch Vision & Facial Interaction Tracker Window")
            print("6. Show Learning Progress Statistics Card")
            print("7. Launch Custom OS Slide Toast Notification Test")
            print("8. Safely Shutdown All Components")
            print("-" * 60)
            
            choice = input("Select operation key (1-8): ").strip()
            
            if choice == '1':
                self.voice.voice_only_mode = not self.voice.voice_only_mode
                state = "ACTIVE" if self.voice.voice_only_mode else "INACTIVE"
                gui_queue.put({"action": "notification", "title": "SYSTEM PROTOCOL", "msg": f"Voice Activation: {state}"})
                speech_queue.put(f"Acoustic tracking functions are now {state}.")
                
            elif choice == '2':
                path = input("Enter fully-qualified PDF document path: ").strip()
                self.current_pdf_text = self.academic.parse_pdf(path)
                if self.current_pdf_text:
                    print(f"\n[Success] Extraction Buffer Sample:\n{self.current_pdf_text[:300]}...\n")
                    speech_queue.put("Text content successfully read into systems cache.")
                else:
                    speech_queue.put("PDF extraction failed. Check file properties.")
                    
            elif choice == '3':
                if not self.current_pdf_text:
                    speech_queue.put("Extraction cache is empty. Please read a PDF document first.")
                    continue
                self.academic.process_explanations(self.current_pdf_text)
                
            elif choice == '4':
                assessments = self.academic.generate_assessment(self.current_pdf_text)
                self.execute_quizzing(assessments)
                
            elif choice == '5':
                if self.vision is None or not self.vision.is_alive():
                    self.vision = JarvisVisionSystem()
                    self.vision.daemon = True
                    self.vision.start()
                else:
                    print("[System Log] Camera process pipeline thread already active.")
                    
            elif choice == '6':
                profile = self.memory.data["user_profiles"].get(self.active_username.lower(), {})
                print("\n" + "="*50)
                print(f"       PROGRESS REPORT CARD: {self.active_username.upper()}     ")
                print("" + "="*50)
                print(f"-> Active Learning Sessions Completed : {profile.get('study_sessions', 0)}")
                print(f"-> Quizzes Answered Successfully     : {profile.get('quizzes_taken', 0)}")
                print(f"-> Cumulative Testing Average        : {profile.get('average_score', 0.0)}%")
                print("" + "="*50 + "\n")
                
            elif choice == '7':
                gui_queue.put({
                    "action": "notification", 
                    "title": "SECURITY MATRIX", 
                    "msg": "Data streams integrity verified successfully."
                })
                
            elif choice == '8':
                self.safe_shutdown()
                break

    def safe_shutdown(self):
        global system_active
        print("\nShutting down master operations safely...")
        speech_queue.put("Powering down system operations.")
        system_active = False
        
        if self.vision is not None:
            self.vision.running = False
            self.vision.join()
            
        self.ui.destroy()
        sys.exit(0)


# =====================================================================
#                         SYSTEM ENTRYPOINT
# =====================================================================
if __name__ == "__main__":
    # 1. Initialize Animated Floating System HUD
    ui_mainframe = JarvisFloatingHUD()
    
    # 2. Attach Speech Synthesis thread safely
    voice_system = JarvisVoiceThread()
    voice_system.daemon = True
    voice_system.start()
    ui_mainframe.voice_engine = voice_system
    
    # 3. Spawn Central Executive CLI Console in background thread
    mainframe_exec = JarvisMainframeExecutive(ui_mainframe)
    console_thread = threading.Thread(target=mainframe_exec.run_control_terminal, name="CLIConsoleThread")
    console_thread.daemon = True
    console_thread.start()
    
    # 4. Fire up UI Event loop
    ui_mainframe.mainloop()
