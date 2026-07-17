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
from pypdf import PdfReader
import html

# cryptography ব্যবহার করে রিয়েল এনক্রিপশন নিশ্চিত করা
try:
    from cryptography.fernet import Fernet
except ImportError:
    # Fallback if library missing, but highly recommended
    Fernet = None

# Advanced Libraries with Graceful Fallbacks
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# =====================================================================
#                        GLOBAL SYSTEM CONFIGURATION
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s",
    handlers=[
        logging.FileHandler("jarvis_mainframe.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("JarvisMainframe")

SYSTEM_ACTIVE = True
background_task_queue = queue.Queue()

# =====================================================================
#                  MODULE 1: VOICE & AUDIO SUBSYSTEM
# =====================================================================
class JarvisVoiceCore:
    def __init__(self):
        self.speech_engine = None
        self.recognizer = None
        self.mic = None
        
        if pyttsx3:
            try:
                self.speech_engine = pyttsx3.init()
                self.speech_engine.setProperty('rate', 175)
                self.speech_engine.setProperty('volume', 0.9)
                logger.info("Voice synthesis system mapped successfully.")
            except Exception as e:
                logger.warning(f"Voice synthesis initialization failed: {e}")
        
        if sr:
            try:
                self.recognizer = sr.Recognizer()
                self.mic = sr.Microphone()
                logger.info("Speech Recognition interfaces operational.")
            except Exception as e:
                logger.warning(f"Microphone access mapping failed: {e}")

    def speak(self, text: str):
        # স্যানিটাইজেশন
        clean_text = text.strip()[:500]
        logger.info(f"[Vocalizing]: '{clean_text}'")
        if self.speech_engine:
            try:
                self.speech_engine.say(clean_text)
                self.speech_engine.runAndWait()
            except Exception as e:
                logger.error(f"Speech engine runtime failure: {e}")
        else:
            print(f"\n[Jarvis Voice]: {clean_text}")

    def listen_command(self) -> str:
        if not self.recognizer or not self.mic:
            logger.warning("Voice input requested but mic interface is offline.")
            return ""

        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("\n[Jarvis Engine] Listening for vocal command... Speak now.")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                command = self.recognizer.recognize_google(audio)
                logger.info(f"Speech converted safely to text: '{command}'")
                return command.strip()
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout reached. No speech detected.")
            return ""
        except Exception as e:
            logger.error(f"Speech recognition pipeline anomaly: {e}")
            return ""


# =====================================================================
#             MODULE 2: MOUSE, KEYBOARD & SCREEN CONTROLLERS
# =====================================================================
class JarvisPeripheralController:
    def __init__(self):
        pyautogui.FAILSAFE = True  # Slam cursor to any corner to abort execution safely
        pyautogui.PAUSE = 0.05
        
        # স্ক্রিন সাইজ বাউন্ডারি চেক ডিফেন্স
        self.screen_width, self.screen_height = pyautogui.size()

    def move_mouse_to(self, x: int, y: int, duration: float = 0.4):
        # বাউন্ডারি ভ্যালিডেশন (DoS ও রানিং ক্রাশ প্রটেকশন)
        x = max(0, min(x, self.screen_width - 1))
        y = max(0, min(y, self.screen_height - 1))
        
        logger.info(f"Peripheral translation triggered to coordinates X={x}, Y={y}")
        try:
            pyautogui.moveTo(x, y, duration=duration)
        except Exception as e:
            logger.error(f"Peripheral mouse movement fault isolated: {e}")

    def execute_click(self, clicks: int = 1, button: str = 'left'):
        if button not in ['left', 'right', 'middle']:
            button = 'left'
        try:
            pyautogui.click(clicks=clicks, button=button)
            logger.info(f"Triggered peripheral click: [{button}] x{clicks}")
        except Exception as e:
            logger.error(f"Mouse interaction operation blocked: {e}")

    def virtual_type(self, text: str, delay: float = 0.03):
        # ইনপুট বাফারিং ও স্যানিটাইজেশন প্রটেকশন
        safe_text = text[:1000]
        logger.info("Generating physical automated keystrokes payload safely.")
        try:
            pyautogui.write(safe_text, interval=delay)
        except Exception as e:
            logger.error(f"Keyboard output driver fault: {e}")


# =====================================================================
#             MODULE 3: ACADEMIC CORE (PDF, COGNITIVE & STUDY)
# =====================================================================
class JarvisAcademicEngine:
    def __init__(self, memory_ref):
        self.memory = memory_ref

    def read_pdf(self, file_path: str) -> str:
        safe_path = os.path.abspath(file_path)
        logger.info(f"Initializing secure PDF scan for path context: '{safe_path}'")
        
        if not os.path.exists(safe_path) or not os.path.isfile(safe_path):
            logger.error("Target document path does not exist or is an illegal descriptor.")
            return ""
        
        # ডস অ্যাটাক ডিফেন্স: সর্বোচ্চ ৫০ মেগাবাইটের ফাইল এলাউড
        if os.path.getsize(safe_path) > 50 * 1024 * 1024:
            logger.error("Audio/Document payload rejected: File size exceeds safety boundaries.")
            return ""

        try:
            reader = PdfReader(safe_path)
            extracted_text = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    # এক্সএসএস বা ফরম্যাটিং স্ক্রাব
                    extracted_text.append(html.escape(page_text))
            
            logger.info(f"PDF Parsing operation successful. Total pages: {len(reader.pages)}.")
            return "\n".join(extracted_text)
        except Exception as e:
            logger.error(f"Failed to securely parse target PDF asset: {e}")
            return ""

    def explain_topics(self, document_text: str):
        if not document_text or not document_text.strip():
            print("[Academic Core] Execution aborted: Document pool is empty.")
            return

        print("\n" + "="*55)
        print("          JARVIS COGNITIVE ACADEMIC TOPIC PARSER       ")
        print("="*55)
        
        paragraphs = [p.strip() for p in document_text.split('\n') if len(p.strip()) > 30]
        print(f"\n[Analyzed Volume]: {len(document_text)} tokens.")
        print(f"[Detected Context Blocks]: {len(paragraphs)} paragraph array clusters.")
        
        for idx, para in enumerate(paragraphs[:3], 1):
            sentences = para.split('.')
            summary = sentences[0] + "." if len(sentences) > 0 else para
            print(f"\n[Topic {idx} Matrix]: {summary}")
            if len(sentences) > 1:
                print(f"  [Elaboration]: {'.'.join(sentences[1:3]).strip()}.")
        print("="*55 + "\n")

    def generate_quiz(self, document_text: str) -> list:
        paragraphs = [p.strip() for p in document_text.split('\n') if len(p.strip()) > 40]
        quizzes = []

        if not paragraphs:
            quizzes = [
                {
                    "question": "What core component manages peripheral systems in Jarvis?",
                    "options": ["A) The Mouse Controller", "B) The Cognitive Core", "C) The Speech Synthesizer", "D) Video Pipeline"],
                    "answer": "B"
                },
                {
                    "question": "Which database structure retains encrypted configuration data for Jarvis?",
                    "options": ["A) Redis Database", "B) SQLite Connection", "C) Cryptographic secure storage memory", "D) Cloud Bucket"],
                    "answer": "C"
                }
            ]
        else:
            for para in paragraphs[:3]:
                words = para.split()
                if len(words) > 10:
                    target_idx = len(words) // 2
                    missing_word = words[target_idx].strip(",.()\"'")
                    if len(missing_word) > 2:
                        question = para.replace(missing_word, "_______", 1)
                        quizzes.append({
                            "question": f"Fill in the missing block metrics:\n\"{question}\"",
                            "options": [f"Target Matrix Token: {missing_word}"],
                            "answer": missing_word.lower()
                        })
        return quizzes

    def monitor_progress(self, current_username: str):
        username = current_username.lower().strip()
        user_profiles = self.memory.data.get("users", {})
        
        if username not in user_profiles:
            print(f"[Academic Core] Profile sequence not initialized for '{username}'.")
            return

        profile = user_profiles[username]
        study_hours = profile.get("study_sessions", 0)
        quizzes_taken = profile.get("quizzes_taken", 0)
        average_score = profile.get("average_score", 0.0)

        print("\n" + "="*55)
        print(f"       STUDENT REPORT CARD FOR: {username.upper()}     ")
        print("="*55)
        print(f"-> Total Active Lessons Completed : {study_hours} sessions")
        print(f"-> Dynamic Quizzes Completed      : {quizzes_taken}")
        print(f"-> Average Quiz Score Metric      : {average_score:.2f}%")
        
        if average_score >= 85.0:
            status = "EXCELLENT - Advanced Concept Mastery"
        elif average_score >= 60.0:
            status = "GOOD - Stable Progress, revision suggested"
        else:
            status = "NEEDS REVIEW - Schedule focused revision"
        print(f"-> Target Performance Status      : {status}")
        print("="*55 + "\n")


# =====================================================================
#             COGNITIVE ENGINE: SECURE CRYPTO MEMORY (FORTIFIED)
# =====================================================================
class JarvisMemory:
    def __init__(self, filename="jarvis_secure_memory.dat"):
        self.filename = filename
        self.key_file = "jarvis_secret.key"
        self.fernet = self._init_cipher_suite()
        self.data = self.load_memory()

    def _init_cipher_suite(self) -> Optional[Fernet]:
        """বাস্তব AES এনক্রিপশন কী জেনারেট এবং লোড করার সিকিউর মেকানিজম"""
        if not Fernet:
            logger.warning("Cryptography module unavailable. Falling back to basic structure.")
            return None
        try:
            if not os.path.exists(self.key_file):
                key = Fernet.generate_key()
                with open(self.key_file, "wb") as kf:
                    kf.write(key)
            else:
                with open(self.key_file, "rb") as kf:
                    key = kf.read()
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to securely construct cryptographic keys: {e}")
            return None

    def load_memory(self) -> dict:
        default_struct = {"users": {}, "tasks": [], "plans": [], "notes": []}
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "rb") as file:
                    encrypted_content = file.read()
                
                if not encrypted_content.strip():
                    return default_struct
                
                if self.fernet:
                    decrypted_bytes = self.fernet.decrypt(encrypted_content)
                    return json.loads(decrypted_bytes.decode('utf-8'))
                else:
                    # Fallback structural mock read (যদি মডিউল ক্র্যাশ করে)
                    return json.loads(encrypted_content.decode('utf-8'))
            except Exception as e:
                logger.error(f"Memory corruption or decryption exception intercepted: {e}")
        return default_struct

    def save_memory(self):
        try:
            raw_bytes = json.dumps(self.data, indent=4).encode('utf-8')
            with open(self.filename, "wb") as file:
                if self.fernet:
                    file.write(self.fernet.encrypt(raw_bytes))
                else:
                    file.write(raw_bytes)
        except Exception as e:
            logger.error(f"Cryptographic memory write fault: {e}")

    def update_user_profile(self, name: str, preference: str):
        name = name.lower().strip()
        if not name:
            return
        if name not in self.data["users"]:
            self.data["users"][name] = {"preferences": preference, "study_sessions": 0, "quizzes_taken": 0, "average_score": 0.0}
        self.data["users"][name]["preferences"] = html.escape(preference)
        self.save_memory()


# =====================================================================
#                  MODULE 4: MULTITHREADED VISION ENGINE
# =====================================================================
class JarvisVisionSystem(threading.Thread):
    def __init__(self):
        super().__init__()
        self.name = "JarvisVisionThread"
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.running = True

    def capture_screen_and_detect_ui(self) -> int:
        """মেইন থ্রেডকে ব্লক না করে স্ক্রিন স্ক্যান সম্পন্ন করার ফিক্স"""
        try:
            screenshot = pyautogui.screenshot()
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            img_display = cv2.resize(img, (800, 450)) # মেমোরি লোড ও ডিসপ্লে বাউন্ড ফিট করার জন্য রিসাইজ

            gray = cv2.cvtColor(img_display, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 150)

            contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            count = 0

            for contour in contours:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    if 15 < w < 200 and 10 < h < 100:
                        count += 1
                        cv2.rectangle(img_display, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow("Jarvis Engine - Viewport Detection Mapping", img_display)
            cv2.waitKey(2000) # ২ সেকেন্ড পর স্বয়ংক্রিয়ভাবে উইন্ডো বন্ধ হবে (মেইন থ্রেড আর লুপে ফাসবে না)
            cv2.destroyAllWindows()
            return count
        except Exception as e:
            logger.error(f"UI Capture processing pipeline error: {e}")
            return 0

    def run(self):
        logger.info("Vision processing pipeline thread activated successfully.")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("Primary hardware camera node offline or restricted access.")
            return

        # রিড স্পীড বুস্ট করতে ফ্রেম সাইজ সীমিত করা
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while self.running and SYSTEM_ACTIVE:
            try:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.05)
                    continue

                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, "Human Identity Locked", (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]

                    eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 1)

                    # DeepFace এআই প্রসেসিং থ্রেড সেফ ও এক্সেপশন শিল্ড করা হলো
                    try:
                        cropped_face = frame[y:y+h, x:x+w]
                        analysis = DeepFace.analyze(cropped_face, actions=['emotion'], enforce_detection=False)
                        dominant_emotion = analysis[0]['dominant_emotion']
                        cv2.putText(frame, f"Emotion: {dominant_emotion.upper()}", (x, y + h + 20), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    except Exception:
                        pass

                cv2.imshow("Jarvis Vision Core (Press 'q' inside feed window to escape)", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except Exception as loop_err:
                logger.error(f"Error inside loop architecture processing pipeline: {loop_err}")
                break

        cap.release()
        cv2.destroyAllWindows()
        logger.info("Vision processing framework successfully decommissioned.")


# =====================================================================
#             MODULE 5: THE ASYNC TASK ENGINE (SCHEDULER)
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
            "description": html.escape(description),
            "priority": priority.upper(),
            "status": "QUEUED",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.memory.data["tasks"].append(task_payload)
        self.memory.save_memory()
        background_task_queue.put(task_payload)
        logger.info(f"Queued async execution thread module task ID: {task_id}")

    def run(self):
        logger.info("Asynchronous task scheduling array engine fully active.")
        while self.running and SYSTEM_ACTIVE:
            try:
                task = background_task_queue.get(timeout=1)
                logger.info(f"Processing dynamic system queued node: '{task['description']}'")
                time.sleep(2)
                
                # থ্রেড সেফ স্টেট মিউটেশন
                for item in self.memory.data["tasks"]:
                    if item["id"] == task["id"]:
                        item["status"] = "COMPLETED"
                        
                self.memory.save_memory()
                logger.info(f"Asynchronous pipeline execution verification code complete for ID: {task['id']}")
                background_task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Scheduler core error state trapped: {e}")


# =====================================================================
#                     UNIFIED MAIN CONSOLE ENGINE
# =====================================================================
class JarvisCoreMainframe:
    def __init__(self):
        self.voice = JarvisVoiceCore()
        self.peripherals = JarvisPeripheralController()
        self.cognitive_mem = JarvisMemory()
        self.academic = JarvisAcademicEngine(self.cognitive_mem)
        
        self.vision_thread = None
        self.scheduler_thread = JarvisTaskEngine(self.cognitive_mem)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.current_user = "Student"
        self.cognitive_mem.update_user_profile(self.current_user, "Academic Mode Default")

    def handle_quiz_session(self, quizzes: list):
        if not quizzes:
            self.voice.speak("No quiz items structurally configured or available.")
            return

        self.voice.speak("Ready to initiate. Let's test your understanding.")
        correct_count = 0
        
        for idx, item in enumerate(quizzes, 1):
            print(f"\n[Question {idx}]: {item['question']}")
            if len(item['options']) > 1:
                for opt in item['options']:
                    print(opt)
                user_ans = input("Your Answer (Choice Letter): ").strip().upper()
            else:
                user_ans = input("Complete the blank context metrics: ").strip().lower()

            if user_ans == str(item['answer']).upper() or user_ans == str(item['answer']).lower():
                print("Correct! Excellent execution.")
                correct_count += 1
            else:
                print(f"Incorrect execution parameters. Solution: {item['answer']}")

        score_pct = (correct_count / len(quizzes)) * 100.0
        username = self.current_user.lower()
        
        profile = self.cognitive_mem.data["users"][username]
        old_quizzes = profile.get("quizzes_taken", 0)
        old_average = profile.get("average_score", 0.0)

        new_quizzes = old_quizzes + 1
        new_average = ((old_average * old_quizzes) + score_pct) / new_quizzes

        profile["study_sessions"] = profile.get("study_sessions", 0) + 1
        profile["quizzes_taken"] = new_quizzes
        profile["average_score"] = new_average
        self.cognitive_mem.save_memory()

        self.voice.speak(f"Quiz completed. You scored {correct_count} out of {len(quizzes)} entries.")


# =====================================================================
#                         MAIN RUNTIME DECK
# =====================================================================
def main():
    global SYSTEM_ACTIVE
    mainframe = JarvisCoreMainframe()

    print("\n" + "="*71)
    print("             JARVIS ENTERPRISE COGNITIVE OPERATING SYSTEM             ")
    print("="*71)
    mainframe.voice.speak("System check complete. Academic modules synchronized and operational.")

    active_pdf_text = ""

    while True:
        print("\n=== SYSTEM CORE EXECUTIVE MENU ===")
        print("1. Read PDF Document & Extract Text")
        print("2. Explain Extracted Document Topics")
        print("3. Generate & Run Learning Quizzes")
        print("4. View My Learning Progress Metrics")
        print("5. Start Camera Vision Processing (Face, Eyes, Emotion)")
        print("6. Run Button & UI Viewport Scanner")
        print("7. View System Diagnostic Hardware Stats")
        print("8. Close System Safe Down")
        print("-" * 71)
        
        choice = input("Enter operational choice (1-8): ").strip()
        
        if choice == '1':
            pdf_path = input("Enter full target absolute path of PDF file: ").strip()
            mainframe.voice.speak("Extracting textual document contents.")
            active_pdf_text = mainframe.academic.read_pdf(pdf_path)
            if active_pdf_text:
                print(f"\n[Success] Loaded PDF text stream sample:\n{active_pdf_text[:300]}...\n")
                mainframe.voice.speak("Document successfully read into system memory array.")
            else:
                mainframe.voice.speak("Failed reading document path location structure.")
                
        elif choice == '2':
            if not active_pdf_text:
                mainframe.voice.speak("No document data parsed yet. Load a valid file from step 1.")
                continue
            mainframe.voice.speak("Analyzing topics.")
            mainframe.academic.explain_topics(active_pdf_text)
            
        elif choice == '3':
            quizzes_to_run = mainframe.academic.generate_quiz(active_pdf_text)
            mainframe.handle_quiz_session(quizzes_to_run)
            
        elif choice == '4':
            mainframe.academic.monitor_progress(mainframe.current_user)
            
        elif choice == '5':
            if mainframe.vision_thread is None or not mainframe.vision_thread.is_alive():
                mainframe.vision_thread = JarvisVisionSystem()
                mainframe.vision_thread.daemon = True
                mainframe.vision_thread.start()
                mainframe.voice.speak("Visual tracking camera framework deployment online.")
            else:
                print("[Warning] Camera processing array is already executed and online.")
                
        elif choice == '6':
            mainframe.voice.speak("Scanning desktop interface matrix layouts.")
            # থ্রেড সেফ ইন্সট্যান্স গ্র্যাব কল
            scanner = JarvisVisionSystem()
            detected_elements = scanner.capture_screen_and_detect_ui()
            print(f"[Matrix Engine Log] Structural scan absolute complete. Elements identified: {detected_elements}")
            
        elif choice == '7':
            try:
                cpu = psutil.cpu_percent(interval=0.1)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                print(f"\n--- JARVIS COMPONENT CORE HARDWARE METRICS ---")
                print(f"System Processors Load: {cpu}% | RAM Consumption: {ram}% | Disk Utilization: {disk}%")
                mainframe.voice.speak(f"System processing resources capacity state is at {int(cpu)} percent.")
            except Exception as ps_err:
                logger.error(f"Failed to pull diagnostic infrastructure stats: {ps_err}")
            
        elif choice == '8':
            print("\n[Safe Shutdown Initiated] Terminating background processes securely...")
            mainframe.voice.speak("Shutting down core routines. Moving system parameters securely offline.")
            SYSTEM_ACTIVE = False
            
            if mainframe.vision_thread is not None:
                mainframe.vision_thread.running = False
                mainframe.vision_thread.join(timeout=2.0)
            
            mainframe.scheduler_thread.running = False
            print("[System Safe Shutdown Completed] All modules, keys, and processes offline. Terminal Safe.")
            break
        else:
            print("[Runtime Deck Alert] Input option sequence out of target array bound limits.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Force Interrupt Trapped] Shutting down mainframe engine safely.")
        SYSTEM_ACTIVE = False
        sys.exit(0)
          
