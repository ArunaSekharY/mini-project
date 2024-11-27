import threading
import time
import cv2
import mediapipe as mp
import pyautogui as pag
import speech_recognition as sr

# Voice Command Controls
stop_event = threading.Event()


def stop_cursor():
    stop_event.set()


def execute_command(command):
    stop_event.clear()

    if "stop" in command:
        stop_cursor()
        print("Stopping cursor movement.")
        return

    if "click" in command:
        pag.click()
        print("Clicked.")
        return

    if "double click" in command:
        pag.doubleClick()
        print("Double clicked.")
        return

    if "right click" in command:
        pag.click(button="right")
        print("Right Click.")
        return

    if "enter" in command:
        pag.press("enter")
        print("Pressed enter.")
        return

    if "exit" in command:
        print("Exiting program.")
        exit(0)


def voice_control():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        print("Voice control active. Say a command (e.g., 'click', 'stop').")

        while True:
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio).lower()
                print(f"You said: {command}")
                execute_command(command)
            except sr.UnknownValueError:
                print("I couldn't understand what you said. Please try again.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")


# Gaze Control with MediaPipe
def gaze_control():
    cam = cv2.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pag.size()
    print("Screen dimensions: ", screen_w, "x", screen_h)

    moving = False  # Flag to check if the cursor is moving
    current_direction = None  # To store the current movement direction (left/right)

    def move_cursor(direction):
        """Continuously move the cursor in the specified direction."""
        while moving:
            if direction == "left":
                pag.move(-10, 0)
            elif direction == "right":
                pag.move(10, 0)
            time.sleep(0.05)  # Adjust speed by changing the sleep time

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to capture frame.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        landmarks_points = results.multi_face_landmarks

        if landmarks_points:
            landmarks = landmarks_points[0].landmark

            # Draw landmarks for the iris and eye center
            for id, point in enumerate(landmarks[474:478]):  # Iris landmarks
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            center_x = int(landmarks[468].x * frame.shape[1])  # Eye center x
            center_y = int(landmarks[468].y * frame.shape[0])  # Eye center y
            cv2.circle(frame, (center_x, center_y), 3, (255, 0, 0), -1)

            # Detect gaze direction
            iris_x = landmarks[474].x  # X-coordinate of the iris
            if iris_x < landmarks[468].x - 0.01 and not moving:  # Gaze left
                print("Looking left.")
                moving = True
                current_direction = "left"
                threading.Thread(target=move_cursor, args=(current_direction,)).start()
            elif iris_x > landmarks[468].x + 0.01 and not moving:  # Gaze right
                print("Looking right.")
                moving = True
                current_direction = "right"
                threading.Thread(target=move_cursor, args=(current_direction,)).start()

            # Blinking-based control logic
            left_eye = [landmarks[145], landmarks[159]]
            right_eye = [landmarks[374], landmarks[386]]

            # Calculate eye aspect ratio (EAR) for blinking detection
            def calculate_ear(eye):
                return abs(eye[0].y - eye[1].y)

            left_ear = calculate_ear(left_eye)
            right_ear = calculate_ear(right_eye)

            blink_threshold = 0.02
            if left_ear < blink_threshold and right_ear < blink_threshold:
                print("Blink detected. Stopping cursor.")
                moving = False
                current_direction = None  # Reset direction
                time.sleep(0.3)  # Prevent multiple detections for a single blink

        cv2.imshow("Gaze Control", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()


# Main Function
if __name__ == "__main__":
    # Run both systems in parallel threads
    threading.Thread(target=voice_control).start()
    gaze_control()
