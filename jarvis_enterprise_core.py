import cv2
import numpy as np
import pyautogui
from deepface import DeepFace
import time
import json
import os
import sys
import threading
import queue
import logging
from datetime import datetime
import psutil

# =====================================================================
#                          SYSTEM LOGGING SETUP
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("jarvis_system.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# জেনুইন মাল্টি-থ্রেডিং সিঙ্ক্রোনাইজেশন ভ্যারিয়েবল
system_active = True

# =====================================================================
#                 COGNITIVE ENGINE: MEMORY & CRYPTO
# =====================================================================
class JarvisMemory:
    def __init__(self, filename="jarvis_secure_memory.json"):
        self.filename = filename
        self.key = 42  
        self.lock = threading.Lock() # মাল্টি-থ্রেড রাইটিং প্রটেকশন
        self.data = self.load_memory()

    def _xor_cipher(self, data_str: str) -> str:
        return "".join(chr(ord(char) ^ self.key) for char in data_str)

    def load_memory(self):
        default_structure = {"users": {}, "tasks": [], "plans": [], "notes": []}
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as file:
                    encrypted_content = file.read()
                    if not encrypted_content.strip():
                        return default_structure
                    decrypted_json = self._xor_cipher(encrypted_content)
                    return json.loads(decrypted_json)
            except Exception as e:
                logging.error(f"Error loading secure memory, resetting structure: {e}")
                return default_structure
        return default_structure

    def save_memory(self):
        with self.lock: # রেস কন্ডিশন এড়ানোর জন্য লক ব্যবহার
            try:
                raw_json = json.dumps(self.data, indent=4)
                encrypted_json = self._xor_cipher(raw_json)
                with open(self.filename, "w", encoding="utf-8") as file:
                    file.write(encrypted_json)
            except Exception as e:
                logging.error(f"Failed to write memory securely: {e}")

    def update_user_profile(self, username, trait, value):
        username = username.lower().strip()
        if not username:
            return
        if username not in self.data["users"]:
            self.data["users"][username] = {}
        self.data["users"][username][trait] = value
        self.save_memory()
        logging.info(f"Memory updated: {trait} -> {value} for user '{username}'")


# =====================================================================
#                 COGNITIVE ENGINE: RECURSIVE PLANNING
# =====================================================================
class JarvisPlanningEngine:
    def decompose_goal(self, goal: str) -> list:
        logging.info(f"Decomposing macro goal: '{goal}'")
        g_low = goal.lower()
        if "deploy software" in g_low:
            return [
                "Verify dependencies and configurations",
                "Run unit test suite recursively",
                "Compile production-ready packages",
                "Execute server deployment script"
            ]
        elif "analyze system health" in g_low:
            return [
                "Read CPU/RAM diagnostic bounds",
                "Scan active system log files for critical warnings",
                "Check network socket loopbacks"
            ]
        return [
            f"Initialize target definition phase for '{goal}'",
            "Execute sequence execution steps",
            "Assess target completion indicators"
        ]


# =====================================================================
#                COGNITIVE ENGINE: LOGICAL REASONING
# =====================================================================
class JarvisReasoningEngine:
    def resolve_constraints(self, constraint_a: str, constraint_b: str) -> str:
        logging.info(f"Parsing logical conflicts: [{constraint_a}] vs [{constraint_b}]")
        ca, cb = constraint_a.lower(), constraint_b.lower()
        if "max performance" in ca and "low power" in cb:
            return "Resolution: Throttle CPU to 75% load capacity; balance core distribution dynamically."
        elif "high privacy" in ca and "cloud integration" in cb:
            return "Resolution: Restrict cloud output. Route queries through local secure hash pipelines."
        return "Resolution: Prioritize local execution parameters over remote hooks."


# =====================================================================
#                 COGNITIVE ENGINE: TASK SCHEDULER
# =====================================================================
class JarvisTaskEngine:
    def __init__(self, memory_obj):
        self.memory = memory_obj

    def register_task(self, description, priority="MEDIUM"):
        task_id = len(self.memory.data["tasks"]) + 1
        new_task = {
            "id": task_id,
            "description": description,
            "priority": priority.upper(),
            "status": "PENDING",
            "created_at": datetime.now().isoformat()
        }
        self.memory.data["tasks"].append(new_task)
        self.memory.save_memory()
        logging.info(f"New task registered: ID {task_id} | {description}")

    def list_all_tasks(self):
        tasks = self.memory.data.get("tasks", [])
        if not tasks:
            print("\n[Task Engine] No tasks currently scheduled.")
            return
        print("\n=== SYSTEM TASK SCHEDULE ===")
        for t in tasks:
            print(f"[{t['id']}] {t['description']} | Priority: {t['priority']} | Status: {t['status']}")


# =====================================================================
#                 SYSTEM HARDWARE MONITOR (DIAGNOSTICS)
# =====================================================================
class JarvisDiagnostics:
    @staticmethod
    def get_hardware_status():
        return {
            "cpu_percent": psutil.cpu_percent(interval=None), # Non-blocking UI
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }


# =====================================================================
#                       ADVANCED VISION MODULE
# =====================================================================
class JarvisVisionSystem:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.running = False
        self.cap = None
        self.emotion_label = "Analyzing..."
        self.last_emotion_check = 0
        self.emotion_interval = 2.0  # প্রতি ২ সেকেন্ড পর পর ইমোশন অ্যানালাইসিস হবে (CPU সেভার)

    def start_capture(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logging.error("Failed to map target camera index.")
            return False
        self.running = True
        logging.info("Vision Pipeline Successfully Triggered.")
        return True

    def process_frame(self):
        """মেইন লুপ থেকে কল করার উপযোগী ফ্রেম প্রসেসর"""
        if not self.running or self.cap is None:
            return False

        ret, frame = self.cap.read()
        if not ret:
            return True

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        current_time = time.time()
        
        # ১. ফেস ডিটেকশন
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, "Target Located", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]

            # ২. আই ট্র্যাকিং
            eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 1)

            # ৩. থ্রটলড ইমোশন রিকগনিশন (CPU প্রটেকশন মডিউল)
            if current_time - self.last_emotion_check > self.emotion_interval:
                try:
                    cropped_face = frame[y:y+h, x:x+w]
                    # মডেল সাইজ ছোট রাখার জন্য এবং ক্রাশ এড়াতে enforce_detection=False
                    analysis = DeepFace.analyze(cropped_face, actions=['emotion'], enforce_detection=False, silent=True)
                    self.emotion_label = analysis[0]['dominant_emotion'].upper()
                    self.last_emotion_check = current_time
                except Exception:
                    pass
            
            cv2.putText(frame, f"State: {self.emotion_label}", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # ৪. স্কিন সেগমেন্টেশন এবং হ্যান্ড জেসচার
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
                cv2.putText(frame, "Gesture Area Tracked", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # মেইন থ্রেড GUI রেন্ডারিং
        cv2.imshow("Jarvis Vision Module", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
        return True

    def stop_capture(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()
        logging.info("Vision Engine Securely Disengaged.")


# =====================================================================
#                         NLP COMMAND PARSER
# =====================================================================
class JarvisNLPParser:
    def __init__(self, memory_sys, task_sys, reasoning_sys, planning_sys):
        self.memory = memory_sys
        self.tasks = task_sys
        self.reasoning = reasoning_sys
        self.planning = planning_sys

    def process_command(self, raw_input: str):
        text = raw_input.strip().lower()
        if not text:
            return

        if "remember" in text:
            parts = text.replace("remember ", "").split(" prefers ")
            if len(parts) == 2:
                self.memory.update_user_profile(parts[0], "preference", parts[1])
                print(f"[Jarvis] Fact stored for {parts[0]}.")
            else:
                print("[Jarvis] Syntax Error. Use: 'remember [name] prefers [preference]'")

        elif "schedule" in text or "task" in text:
            task_desc = text.replace("task ", "").replace("schedule ", "")
            self.tasks.register_task(task_desc, "HIGH")
            print(f"[Jarvis] Task safely registered under scheduler queue.")

        elif "plan" in text:
            goal = text.replace("plan ", "")
            subtasks = self.planning.decompose_goal(goal)
            print(f"\n[Plan Constructed for: {goal}]")
            for idx, st in enumerate(subtasks, 1):
                print(f"  Step {idx}: {st}")

        elif "resolve" in text:
            inputs = text.replace("resolve ", "").split(" vs ")
            if len(inputs) == 2:
                res = self.reasoning.resolve_constraints(inputs[0], inputs[1])
                print(f"\n[Reasoning Output]\n{res}")
            else:
                res = self.reasoning.resolve_constraints(text.replace("resolve ", ""), "low power")
                print(f"\n[Reasoning Output]\n{res}")

        elif "status" in text or "diagnose" in text:
            metrics = JarvisDiagnostics.get_hardware_status()
            print(f"\n--- SYSTEM HEALTH METRICS ---")
            print(f"CPU Utilization: {metrics['cpu_percent']}%")
            print(f"Memory Alloc:    {metrics['ram_percent']}%")
            print(f"Primary Disk:    {metrics['disk_percent']}%")
        else:
            print(f"[Jarvis Logic] Unrecognized intent pipeline: '{raw_input}'")


# =====================================================================
#                         MAIN RUNTIME LOOP
# =====================================================================
def main():
    global system_active
    
    memory_system = JarvisMemory()
    task_system = JarvisTaskEngine(memory_system)
    reasoning_system = JarvisReasoningEngine()
    planning_system = JarvisPlanningEngine()
    nlp_system = JarvisNLPParser(memory_system, task_system, reasoning_system, planning_system)
    
    vision_system = JarvisVisionSystem()

    print("\n=======================================================")
    print("        JARVIS ENTERPRISE COGNITIVE CO-PROCESSOR       ")
    print("=======================================================")
    print("Welcome back, Agent. Core systems online.")

    while system_active:
        print("\n--- Command Console Options ---")
        print("1. Launch Vision Processing Pipeline (Face/Eye/Gestures/Emotions)")
        print("2. Enter Natural Language Interface (NLP Command Loop)")
        print("3. View Hardware Performance Metrics")
        print("4. View All Scheduled Tasks")
        print("5. Safely Offline/Exit")
        print("-------------------------------------------------------")
        
        choice = input("Initiate action (1-5): ").strip()
        
        if choice == '1':
            if not vision_system.running:
                if vision_system.start_capture():
                    print("[Jarvis] Stream active. Press 'q' inside the video window to return to console.")
                    # OpenCV GUI Loop টিকে মেইন থ্রেডে পুশ করা হলো ক্রাশ এড়াতে
                    while vision_system.running:
                        keep_running = vision_system.process_frame()
                        if not keep_running:
                            vision_system.stop_capture()
                            break
            else:
                print("[Jarvis Alert] Camera pipeline already active.")
                
        elif choice == '2':
            print("\nEntering NLP Loop (Type 'exit' to return to Main Console)")
            while True:
                cmd = input("Command >> ").strip()
                if cmd.lower() in ["exit", "back", "return"]:
                    break
                nlp_system.process_command(cmd)
                
        elif choice == '3':
            metrics = JarvisDiagnostics.get_hardware_status()
            print(f"\n--- JARVIS CPU/RAM RUNTIME DIAGNOSTIC ---")
            print(f"CPU Load: {metrics['cpu_percent']}% | RAM Alloc: {metrics['ram_percent']}% | HD: {metrics['disk_percent']}%")
            
        elif choice == '4':
            task_system.list_all_tasks()
            
        elif choice == '5':
            print("\n[Jarvis Engine] Safely closing down subroutines...")
            system_active = False
            vision_system.stop_capture()
            print("System is securely offline. Goodbye!")
            break
        else:
            print("[Warning] Invalid selection parameter. Attempt again.")

if __name__ == "__main__":
    main()
