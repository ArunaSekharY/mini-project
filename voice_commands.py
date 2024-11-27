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


if __name__ == "__main__":
    voice_control()
