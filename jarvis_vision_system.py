import cv2
import numpy as np
import pyautogui
import logging
from deepface import DeepFace

# লগিং কনফিগারেশন - যা সিস্টেমের ভুলগুলো ট্র্যাক করবে
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [JARVIS-VISION] - %(levelname)s - %(message)s')

class JarvisVisionEngine:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.frame_counter = 0

    def detect_ui_elements(self):
        """উন্নত এজ ডিটেকশন এবং অ্যাডাপ্টিভ থ্রেশহোল্ডিং ব্যবহার করে UI এলিমেন্ট শনাক্তকরণ"""
        try:
            screenshot = pyautogui.screenshot()
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # নয়েজ কমাতে ব্লার এবং অ্যাডাপ্টিভ থ্রেশহোল্ডিং
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if 50 < w < 500 and 20 < h < 200: # ফিল্টারিং
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            cv2.imshow("Jarvis UI Analysis", cv2.resize(img, (960, 540)))
            cv2.waitKey(0)
        except Exception as e:
            logging.error(f"UI Detection Error: {e}")

    def run_realtime_analysis(self):
        """অপ্টিমাইজড রিয়েল-টাইম ফেস এবং ইমোশন ট্র্যাকিং"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.critical("Webcam Access Denied!")
            return

        logging.info("Visual Matrix Initialized...")
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            self.frame_counter += 1
            faces = self.face_cascade.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 1.1, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # প্রতি ১০ ফ্রেমে একবার ইমোশন চেক (পারফরম্যান্স বুস্টের জন্য)
                if self.frame_counter % 10 == 0:
                    try:
                        face_roi = frame[y:y+h, x:x+w]
                        analysis = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                        emotion = analysis[0]['dominant_emotion']
                        cv2.putText(frame, f"Mood: {emotion}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    except: pass

            cv2.imshow('Jarvis Vision Matrix', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    engine = JarvisVisionEngine()
    # মেনু সিস্টেমটি আরও ক্লিন করা হয়েছে
    choice = input("Select: 1 (UI) or 2 (Face/Emotion): ")
    if choice == '1': engine.detect_ui_elements()
    elif choice == '2': engine.run_realtime_analysis()
