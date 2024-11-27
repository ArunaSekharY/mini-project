import threading
import time
import cv2
import mediapipe as mp
import pyautogui as pag
import speech_recognition as sr
import threading
import time
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

    if "double click" in command:
        pag.doubleClick()
        print("Double clicked.")
        return

    if "right click" in command:
        pag.click(button="right")

        print("Right Click.")
        return

    if "click" in command:
        pag.click()
        print("Clicked.")
        return

    if "enter" in command:
        pag.press("enter")
        print("Pressed enter.")
        return

    if "exit" or "stop" in command:
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
            for id, point in enumerate(landmarks[474:478]):
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                if id == 1:
                    screen_x = screen_w / frame.shape[1] * x
                    screen_y = screen_h / frame.shape[0] * y
                    # print("Screen coordinates: ", screen_x, screen_y)
                    pag.moveTo(screen_x, screen_y)

            # Blinking-based control logic
            left_eye = [landmarks[145], landmarks[159]]
            right_eye = [landmarks[374], landmarks[386]]
            for landmark in right_eye + left_eye:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

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
