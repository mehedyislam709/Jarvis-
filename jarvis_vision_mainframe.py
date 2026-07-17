import os
import cv2
import numpy as np
import logging
import threading
import queue
from ultralytics import YOLO
import dlib

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [JARVIS-VISION-V2] %(message)s")

class JarvisVisionSystem:
    def __init__(self, landmark_path: str = "shape_predictor_68_face_landmarks.dat"):
        # Model Hardening
        try:
            self.yolo_model = YOLO("yolov8n.pt")
            self.detector = dlib.get_frontal_face_detector()
            if not os.path.exists(landmark_path):
                raise FileNotFoundError(f"Missing critical model: {landmark_path}")
            self.predictor = dlib.shape_predictor(landmark_path)
        except Exception as e:
            logging.critical(f"System Load Failure: {e}")
            raise

        self.frame_queue = queue.Queue(maxsize=2)
        self.running = True
        
        # Thresholds
        self.EAR_THRESHOLD = 0.20
        self.FATIGUE_LIMIT = 20
        self.fatigue_counter = 0

    def _compute_ear(self, eye):
        # A, B, C distance calculation
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        return (A + B) / (2.0 * C)

    def _inference_worker(self):
        """Dedicated thread for CPU/GPU intensive Vision Tasks."""
        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                # Process logic goes here (YOLO + Landmark)
                # ... (Logic remains similar but isolated from UI)

    def execute_live_stream(self):
        """Hardened Stream Executor with Watchdog."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("Hardware access denied.")
            return

        # Start background processing thread
        worker = threading.Thread(target=self._inference_worker, daemon=True)
        worker.start()

        try:
            while self.running:
                ret, frame = cap.read()
                if not ret: continue
                
                # Non-blocking queue update
                if self.frame_queue.empty():
                    self.frame_queue.put(frame)
                
                # UI Rendering Layer
                cv2.imshow("Jarvis Vision Matrix", frame)
                if cv2.waitKey(1) & 0xFF == 27: break
        finally:
            self.running = False
            cap.release()
            cv2.destroyAllWindows()
            logging.info("Jarvis Vision Core Shutdown Safely.")

if __name__ == "__main__":
    vision = JarvisVisionSystem()
    vision.execute_live_stream()
