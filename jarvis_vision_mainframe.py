import os
import sys
import time
import cv2
import numpy as np
import logging

# Ensure Ultralytics and Dlib are installed securely
try:
    from ultralytics import YOLO
    import dlib
except ImportError as err:
    logging.critical(f"[System Init] Missing CV/ML Packages: {err}. Please check your pip installations.")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Jarvis Vision) %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

class JarvisVisionSystem:
    def __init__(self, landmark_predictor_path: str = "shape_predictor_68_face_landmarks.dat"):
        # Load ultra-fast YOLOv8 Model for real-time bounding box tracking
        logging.info("[Vision Core] Activating YOLO Detection Engine...")
        self.yolo_model = YOLO("yolov8n.pt")  # Auto-downloads if not cached locally

        # Initialize Dlib Face Detector & Facial Landmark Predictor for Eye Tracking
        logging.info("[Vision Core] Booting Facial Landmark Predictor...")
        self.face_detector = dlib.get_frontal_face_detector()
        
        if not os.path.exists(landmark_predictor_path):
            logging.warning(f"[Warning] landmark file '{landmark_predictor_path}' not found! "
                            "Please download it to enable Eye-Strain monitoring.")
            self.predictor = None
        else:
            self.predictor = dlib.shape_predictor(landmark_predictor_path)

        # Eye Aspect Ratio (EAR) Threshold Metrics for Fatigue
        self.EAR_THRESHOLD = 0.21
        self.CONSECUTIVE_FRAMES_LIMIT = 25  # Represents ~1.5 seconds of closed eyes
        self.eye_closed_counter = 0

        # Safe distance calibration (Pixels representation of optimal distance)
        self.PROXIMITY_DANGER_THRESHOLD_PX = 280  # Higher width means user is too close to webcam

    def compute_ear_ratio(self, eye_points) -> float:
        """
        Calculates Eye Aspect Ratio (EAR) to mathematically determine 
        if the eyelids are collapsing or straining.
        """
        # Distance between vertical eye coordinates
        v_dist_1 = np.linalg.norm(eye_points[1] - eye_points[5])
        v_dist_2 = np.linalg.norm(eye_points[2] - eye_points[4])
        # Distance between horizontal eye coordinates
        h_dist = np.linalg.norm(eye_points[0] - eye_points[3])
        
        # EAR Formula application
        ear = (v_dist_1 + v_dist_2) / (2.0 * h_dist)
        return ear

    def process_frame(self, frame):
        """Processes each video frame through the parallel processing networks."""
        h, w, _ = frame.shape
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # --- Pipeline 1: YOLO Object Detection & Proximity Assessment ---
        yolo_results = self.yolo_model(frame, verbose=False)[0]
        user_detected = False

        for box in yolo_results.boxes:
            box_cls = int(box.cls[0])
            box_label = self.yolo_model.names[box_cls]
            confidence = float(box.conf[0])

            # Focus solely on 'person' tracking for proximity validation
            if box_label == "person" and confidence > 0.5:
                user_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                face_width = x2 - x1
                
                # Check bounding box width relative to physical proximity
                if face_width > self.PROXIMITY_DANGER_THRESHOLD_PX:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                    cv2.putText(frame, "JARVIS WARNING: STEP BACK FROM SCREEN!", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    logging.warning("[Proximity Alert] User is sitting too close to the screen.")
                else:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"User Confirmed: Safe Distance", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # --- Pipeline 2: Facial Landmark & Eye Strain Diagnostics ---
        if self.predictor is not None:
            detected_faces = self.face_detector(gray_frame)
            for face in detected_faces:
                landmarks = self.predictor(gray_frame, face)
                
                # Extract Eye coordinate matrices from facial landmarks index
                # Left Eye: 36 to 41, Right Eye: 42 to 47
                left_eye = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)])
                right_eye = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)])

                left_ear = self.compute_ear_ratio(left_eye)
                right_ear = self.compute_ear_ratio(right_eye)
                average_ear = (left_ear + right_ear) / 2.0

                # Render Eye Contours on Output Frame
                cv2.drawContours(frame, [left_eye], -1, (255, 255, 0), 1)
                cv2.drawContours(frame, [right_eye], -1, (255, 255, 0), 1)

                # Evaluate for Fatigue or Extreme Strain (Drowsiness)
                if average_ear < self.EAR_THRESHOLD:
                    self.eye_closed_counter += 1
                    if self.eye_closed_counter >= self.CONSECUTIVE_FRAMES_LIMIT:
                        cv2.putText(frame, "FATIGUE ALERT: REST YOUR EYES!", (30, 80),
                                    cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 3)
                        logging.warning("[Fatigue Monitor] Continuous micro-sleep/fatigue patterns flagged!")
                else:
                    self.eye_closed_counter = 0

                # Display active parameters on Stream Overlay
                cv2.putText(frame, f"Diagnostic EAR: {average_ear:.2f}", (30, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
        return frame

    def execute_live_stream(self):
        """Starts real-time analysis through local system camera resource."""
        logging.info("[Vision Engine] Booting System Camera Capture Index [0]...")
        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            logging.critical("[Hardware Error] Camera execution failed. Verify USB connection.")
            return

        cv2.namedWindow("Jarvis Visual Matrix Controller", cv2.WINDOW_NORMAL)

        try:
            while True:
                success, frame = camera.read()
                if not success:
                    logging.warning("[Signal Drop] Frame dropped by system bus.")
                    break

                processed_output = self.process_frame(frame)
                cv2.imshow("Jarvis Visual Matrix Controller", processed_output)

                # Exit key binds: Esc or 'q'
                interrupt_key = cv2.waitKey(1) & 0xFF
                if interrupt_key == 27 or interrupt_key == ord('q'):
                    logging.info("[Core Process] Manual termination received.")
                    break
        finally:
            camera.release()
            cv2.destroyAllWindows()
            logging.info("[Vision Engine] Safe camera and window resource release completed.")

if __name__ == "__main__":
    # Ensure landmark model path points to the correct absolute directory
    vision_core = JarvisVisionSystem(landmark_predictor_path="shape_predictor_68_face_landmarks.dat")
    vision_core.execute_live_stream()
