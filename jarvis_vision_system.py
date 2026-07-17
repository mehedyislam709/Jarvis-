import cv2
import numpy as np
import pyautogui
import logging
from deepface import DeepFace

# Configure logging for audit trails
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s | [JARVIS-VISION] | %(levelname)s | %(message)s'
)

class JarvisVisionEngine:
    """
    A high-performance vision engine for real-time UI analysis,
    facial recognition, and emotional diagnostic tracking.
    """
    def __init__(self):
        # Initialize Haar Cascade Classifier for localized face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.frame_counter = 0

    def detect_ui_elements(self):
        """
        Captures screen, processes edge detection using adaptive thresholding, 
        and highlights rectangular UI components.
        """
        try:
            logging.info("Initiating UI element analysis...")
            screenshot = pyautogui.screenshot()
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian Blur and Adaptive Thresholding to isolate UI structures
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )

            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                # Filter noise by setting dimension constraints for buttons/panels
                if 50 < w < 500 and 20 < h < 200:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Display results with high-quality scaling
            cv2.imshow("Jarvis UI Analysis", cv2.resize(img, (1280, 720)))
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except Exception as e:
            logging.error(f"Critical error during UI detection: {str(e)}")

    def run_realtime_analysis(self):
        """
        Processes webcam feed for facial tracking and emotion analysis.
        Implements frame-skipping to minimize computational load.
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.critical("Hardware Failure: Cannot access webcam source.")
            return

        logging.info("Visual Matrix initialized. Monitoring active...")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret: 
                    logging.warning("Signal lost from webcam.")
                    break
                
                self.frame_counter += 1
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray_frame, 1.1, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    
                    # Performance optimization: Perform DeepFace analysis every 10 frames
                    if self.frame_counter % 10 == 0:
                        try:
                            face_roi = frame[y:y + h, x:x + w]
                            analysis = DeepFace.analyze(
                                face_roi, actions=['emotion'], enforce_detection=False
                            )
                            emotion = analysis[0]['dominant_emotion']
                            cv2.putText(
                                frame, f"Mood: {emotion.upper()}", (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
                            )
                        except Exception:
                            # Silently ignore frame analysis failures to maintain stream continuity
                            pass

                cv2.imshow('Jarvis Vision Matrix', frame)
                
                # Manual termination key: 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            cap.release()
            cv2.destroyAllWindows()
            logging.info("Vision system released safely.")

if __name__ == "__main__":
    engine = JarvisVisionEngine()
    print("--- JARVIS ADVANCED VISION SYSTEM ---")
    print("1. UI Analysis\n2. Real-time Face & Emotion Tracking")
    choice = input("Select mode (1/2): ")
    
    if choice == '1':
        engine.detect_ui_elements()
    elif choice == '2':
        engine.run_realtime_analysis()
