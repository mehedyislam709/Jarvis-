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
        
        if pyttsx3:
            try:
                self.speech_engine = pyttsx3.init()
                self.speech_engine.setProperty('rate', 175)
                self.speech_engine.setProperty('volume', 0.9)
                logging.info("[Audio Engine] Voice synthesis system mapped.")
            except Exception as e:
                logging.warning(f"[Audio Engine] Voice synthesis failed: {e}")
        
        if sr:
            try:
                self.recognizer = sr.Recognizer()
                self.mic = sr.Microphone()
                logging.info("[Audio Engine] Speech Recognition interfaces operational.")
            except Exception as e:
                logging.warning(f"[Audio Engine] Microphone access failed: {e}")

    def speak(self, text: str):
        logging.info(f"[Jarvis Audio] Vocalizing: '{text}'")
        if self.speech_engine:
            self.speech_engine.say(text)
            self.speech_engine.runAndWait()
        else:
            print(f"\n[Jarvis Voice]: {text}")

    def listen_command(self) -> str:
        if not self.recognizer or not self.mic:
            logging.warning("[Audio Engine] Voice input requested but interface is offline.")
            return ""

        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print("\n[Jarvis Engine] Listening for vocal command... Speak now.")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
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
        pyautogui.FAILSAFE = True  # Slam cursor into any corner of your screen to abort automation
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


# =====================================================================
#                  MODULE 3: BROWSER AUTOMATION ENGINE
# =====================================================================
class JarvisBrowserAutomator:
    def __init__(self):
        self.driver = None

    def open_link(self, url: str):
        logging.info(f"[Web Integration] Routing system web request to: {url}")
        webbrowser.open(url)


# =====================================================================
#             MODULE 4: ACADEMIC CORE (PDF, COGNITIVE & STUDY)
# =====================================================================
class JarvisAcademicEngine:
    """
    Main engine handling PDF parsing, topic extraction, 
    dynamic quiz generation, and learning progress monitoring.
    """
    def __init__(self, memory_ref):
        self.memory = memory_ref

    def read_pdf(self, file_path: str) -> str:
        """Loads and extracts text cleanly from any PDF document."""
        logging.info(f"[Academic Core] Initializing PDF scan for: '{file_path}'")
        if not os.path.exists(file_path):
            logging.error(f"[Academic Core] Target file path '{file_path}' does not exist.")
            return ""
        
        try:
            reader = PdfReader(file_path)
            extracted_text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    extracted_text += f"\n--- Page {i+1} ---\n" + page_text
            
            logging.info(f"[Academic Core] Read complete. Pages parsed: {len(reader.pages)}.")
            return extracted_text
        except Exception as e:
            logging.error(f"[Academic Core] Failed to process PDF file: {e}")
            return ""

    def explain_topics(self, document_text: str):
        """Analyzes text heuristics to isolate key concepts, terms, and explanations."""
        if not document_text.strip():
            print("[Academic Core] No text content found to explain.")
            return

        print("\n=======================================================")
        print("          JARVIS COGNITIVE ACADEMIC TOPIC PARSER       ")
        print("=======================================================")
        
        # Simple logical heuristic keyword extractor
        paragraphs = [p.strip() for p in document_text.split('\n') if len(p.strip()) > 30]
        
        print(f"\n[Analyzed Document Volume]: {len(document_text)} characters.")
        print(f"[Detected Context Blocks]: {len(paragraphs)} paragraphs.")
        print("\n--- Key Explanations extracted from Document ---")
        
        # Display top 3 context blocks as key lessons
        for idx, para in enumerate(paragraphs[:3], 1):
            sentences = para.split('.')
            summary = sentences[0] + "." if len(sentences) > 0 else para
            print(f"\n[Topic {idx} Topic Summary]: {summary}")
            if len(sentences) > 1:
                print(f"  [Elaboration]: {'.'.join(sentences[1:3]).strip()}.")
        print("=======================================================\n")

    def generate_quiz(self, document_text: str) -> list:
        """Dynamically builds a interactive custom quiz based on parsed document text."""
        paragraphs = [p.strip() for p in document_text.split('\n') if len(p.strip()) > 40]
        quizzes = []

        if not paragraphs:
            # Fallback mock quiz if document content is empty or unreadable
            quizzes = [
                {
                    "question": "What core component manages peripheral systems in Jarvis?",
                    "options": ["A) The Mouse Controller", "B) The Cognitive Core", "C) The Speech Synthesizer", "D) Video Pipeline"],
                    "answer": "B"
                },
                {
                    "question": "Which database structure retains encrypted configuration data for Jarvis?",
                    "options": ["A) Redis Database", "B) SQLite Connection", "C) Cryptographic XOR secure memory file", "D) Cloud Bucket"],
                    "answer": "C"
                }
            ]
        else:
            # Heuristically craft fill-in-the-blanks using real document parts
            for idx, para in enumerate(paragraphs[:3]):
                words = para.split()
                if len(words) > 10:
                    missing_word = words[len(words) // 2].strip(",.()\"")
                    question = para.replace(missing_word, "_______", 1)
                    quizzes.append({
                        "question": f"Fill in the missing term:\n\"{question}\"",
                        "options": [f"Target Term: {missing_word}"],
                        "answer": missing_word.lower()
                    })
        return quizzes

    def monitor_progress(self, current_username: str):
        """Monitors and updates learning metrics, tracking quiz averages and completed lessons."""
        username = current_username.lower()
        user_profiles = self.memory.data.get("users", {})
        
        if username not in user_profiles:
            print(f"[Academic Core] No learning profiles exist yet for '{username}'.")
            return

        profile = user_profiles[username]
        study_hours = profile.get("study_sessions", 0)
        quizzes_taken = profile.get("quizzes_taken", 0)
        average_score = profile.get("average_score", 0.0)

        print("\n=======================================================")
        print(f"       STUDENT REPORT CARD FOR: {username.upper()}     ")
        print("=======================================================")
        print(f"-> Total Active Lessons Completed : {study_hours} sessions")
        print(f"-> Dynamic Quizzes Completed      : {quizzes_taken}")
        print(f"-> Average Quiz Score Metric      : {average_score:.2f}%")
        
        # Performance review logic
        if average_score >= 85.0:
            status = "EXCELLENT - Advanced Concept Mastery"
        elif average_score >= 60.0:
            status = "GOOD - Stable Progress, revision suggested"
        else:
            status = "NEEDS REVIEW - Schedule focused revision"
        print(f"-> Target Performance Status      : {status}")
        print("=======================================================\n")


# =====================================================================
#             COGNITIVE ENGINE: SECURE CRYPTO MEMORY
# =====================================================================
class JarvisMemory:
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
                logging.error(f"Error restoring cognitive memory: {e}")
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
            self.data["users"][name] = {"preferences": preference, "study_sessions": 0, "quizzes_taken": 0, "average_score": 0.0}
        self.data["users"][name]["preferences"] = preference
        self.save_memory()


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
                cv2.putText(frame, "Human Detected", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

                eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 1)

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

        cap.release()
        cv2.destroyAllWindows()
        logging.info("Vision Core Thread shut down safely.")


# =====================================================================
#             MODULE 6: THE ASYNC TASK ENGINE (SCHEDULER)
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
                task = background_task_queue.get(timeout=2)
                logging.info(f"[Task Engine Process] Processing asynchronous execution node: '{task['description']}'")
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
#                     UNIFIED MAIN CONSOLE ENGINE
# =====================================================================
class JarvisCoreMainframe:
    def __init__(self):
        self.voice = JarvisVoiceCore()
        self.peripherals = JarvisPeripheralController()
        self.browser = JarvisBrowserAutomator()
        self.cognitive_mem = JarvisMemory()
        
        # New Academic Engines
        self.academic = JarvisAcademicEngine(self.cognitive_mem)
        
        # Threads
        self.vision_thread = None
        self.scheduler_thread = JarvisTaskEngine(self.cognitive_mem)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.current_user = "Student"
        # Ensure student database structure is pre-configured
        self.cognitive_mem.update_user_profile(self.current_user, "Academic Mode Default")

    def handle_quiz_session(self, quizzes: list):
        """Runs the interactive study quiz session and updates database statistics."""
        if not quizzes:
            self.voice.speak("No quiz items prepared yet.")
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
                user_ans = input("Complete the blanks: ").strip().lower()

            if user_ans == item['answer']:
                print("Correct! Excellent job.")
                correct_count += 1
            else:
                print(f"Incorrect. The correct answer was: {item['answer']}")

        # Update persistent stats in database
        score_pct = (correct_count / len(quizzes)) * 100.0
        username = self.current_user.lower()
        
        profile = self.cognitive_mem.data["users"][username]
        old_sessions = profile.get("study_sessions", 0)
        old_quizzes = profile.get("quizzes_taken", 0)
        old_average = profile.get("average_score", 0.0)

        new_quizzes = old_quizzes + 1
        new_average = ((old_average * old_quizzes) + score_pct) / new_quizzes

        profile["study_sessions"] = old_sessions + 1
        profile["quizzes_taken"] = new_quizzes
        profile["average_score"] = new_average
        self.cognitive_mem.save_memory()

        self.voice.speak(f"Quiz completed. You scored {correct_count} out of {len(quizzes)}.")


# =====================================================================
#                         MAIN RUNTIME DECK
# =====================================================================
def main():
    global system_active
    mainframe = JarvisCoreMainframe()

    print("\n=======================================================================")
    print("             JARVIS ENTERPRISE COGNITIVE OPERATING SYSTEM             ")
    print("=======================================================================")
    mainframe.voice.speak("System check complete. Academic modules synchronized.")

    # Shared variable to hold extracted text memory
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
        print("-----------------------------------------------------------------------")
        
        choice = input("Enter operational choice (1-8): ").strip()
        
        if choice == '1':
            pdf_path = input("Enter full target path of PDF file: ").strip()
            mainframe.voice.speak("Extracting textual document contents.")
            active_pdf_text = mainframe.academic.read_pdf(pdf_path)
            if active_pdf_text:
                print(f"\n[Success] Loaded PDF text stream sample:\n{active_pdf_text[:300]}...\n")
                mainframe.voice.speak("Document successfully read into system context.")
            else:
                mainframe.voice.speak("Failed reading document path. Confirm file configuration.")
                
        elif choice == '2':
            if not active_pdf_text:
                mainframe.voice.speak("No document parsed yet. Load a PDF from Option 1 first.")
                continue
            mainframe.voice.speak("Analyzing topics.")
            mainframe.academic.explain_topics(active_pdf_text)
            
        elif choice == '3':
            # Run quiz generator. Fallbacks are included if active_pdf_text is empty.
            quizzes_to_run = mainframe.academic.generate_quiz(active_pdf_text)
            mainframe.handle_quiz_session(quizzes_to_run)
            
        elif choice == '4':
            mainframe.academic.monitor_progress(mainframe.current_user)
            
        elif choice == '5':
            if mainframe.vision_thread is None or not mainframe.vision_thread.is_alive():
                mainframe.vision_thread = JarvisVisionSystem()
                mainframe.vision_thread.daemon = True
                mainframe.vision_thread.start()
                mainframe.voice.speak("Visual tracking systems online.")
            else:
                print("[Jarvis Command Log] Dynamic vision system thread is already running.")
                
        elif choice == '6':
            mainframe.voice.speak("Scanning desktop layout elements.")
            detected_elements = JarvisVisionSystem().capture_screen_and_detect_ui()
            print(f"[Jarvis Core Engine] UI element outline analysis complete. Elements found: {detected_elements}")
            
        elif choice == '7':
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            print(f"\n--- MAIN COGNITIVE CORE HARDWARE DIAGNOSTIC ---")
            print(f"System Processors Load: {cpu}% | RAM Consumption: {ram}% | Disk Utilization: {disk}%")
            mainframe.voice.speak(f"System processing levels are at {int(cpu)} percent.")
            
        elif choice == '8':
            print("\n[Safe Shutdown Interface] Closing core routines...")
            mainframe.voice.speak("Shutting down core routines. Moving system parameters securely offline.")
            system_active = False
            
            if mainframe.vision_thread is not None:
                mainframe.vision_thread.running = False
                mainframe.vision_thread.join()
            
            mainframe.scheduler_thread.running = False
            print("[System Safe Shutdown] All processes and memories offline. Farewell.")
            break
        else:
            print("[Runtime Warning] Input selection index is not defined.")

if __name__ == "__main__":
    main()
