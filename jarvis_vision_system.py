import cv2
import numpy as np
import pyautogui
from deepface import DeepFace

# Load Haar Cascades for Face and Eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

def detect_ui_elements():
    """
    Captures the current computer screen and detects potential 
    UI elements like buttons and menus using contour analysis.
    """
    print("[Jarvis Vision] Capturing screen for UI detection...")
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    img_display = img.copy()

    # Image processing for edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detected_count = 0

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        # If the contour has 4 corners (likely a rectangular button or menu box)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)

            # Filter out extreme sizes to reduce noise
            if 30 < w < 400 and 15 < h < 150:
                detected_count += 1
                cv2.rectangle(img_display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img_display, "UI Element", (x, y - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    print(f"[Jarvis Vision] Detection completed. Found {detected_count} potential UI elements.")
    cv2.imshow("Jarvis - Detected UI Elements (Press Any Key to Close)", img_display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def run_realtime_face_eye_emotion():
    """
    Starts the webcam feed and performs real-time Face Detection,
    Eye Tracking, and Emotion Recognition on the same screen.
    """
    print("[Jarvis Vision] Starting webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[Error] Could not access webcam. Please check connection.")
        return

    print("Webcam Active. Press 'q' key to quit the feed.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to grayscale for Cascade Classifiers
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            # 1. Face Detection Box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, "Face", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # Define region of interest (ROI) inside the detected face
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # 2. Eye Tracking (Detecting eyes inside the face box)
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 4)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 2)
                cv2.putText(roi_color, "Eye", (ex, ey - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

            # 3. Emotion Recognition using DeepFace
            try:
                face_img = frame[y:y+h, x:x+w]
                # enforce_detection=False as we already cropped the face
                analysis = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)
                dominant_emotion = analysis[0]['dominant_emotion']
                
                # Render emotion text
                cv2.putText(frame, f"Emotion: {dominant_emotion.upper()}", (x, y + h + 25), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            except Exception:
                # Fallback if frame quality is too low for DeepFace to process
                pass

        cv2.imshow('Jarvis - Face, Eye & Emotion Tracking', frame)

        # Stop screen on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("==================================================")
    print("            JARVIS ADVANCED VISION SYSTEM         ")
    print("==================================================")
    print("1. Detect On-Screen UI (Buttons/Menus)")
    print("2. Run Real-time Camera (Face, Eye & Emotion)")
    print("3. Exit")
    print("--------------------------------------------------")
    
    choice = input("Enter choice (1/2/3): ")
    if choice == '1':
        detect_ui_elements()
    elif choice == '2':
        run_realtime_face_eye_emotion()
    else:
        print("[Jarvis System] Exiting Vision Module. Goodbye!")
