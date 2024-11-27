import cv2
import mediapipe as mp
import pyautogui as pag


def gaze_control_with_direction():
    # Initialize camera, MediaPipe Face Mesh, and screen dimensions
    cam = cv2.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pag.size()
    print(f"Screen dimensions: {screen_w} x {screen_h}")

    # Track the previous eye position for direction detection
    prev_eye_x = None
    direction = "Center"

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Flip frame for a mirrored view
        frame = cv2.flip(frame, 1)

        # Convert to RGB for MediaPipe processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            # Get landmarks for the first detected face
            landmarks = results.multi_face_landmarks[0].landmark
            frame_h, frame_w, _ = frame.shape

            # Extract eye landmarks (left and right)
            left_eye = [landmarks[145], landmarks[159]]  # Left eye landmarks
            right_eye = [landmarks[374], landmarks[386]]  # Right eye landmarks

            # Calculate region of interest (ROI) for zooming in on the eyes
            x_min = int(min([lm.x for lm in left_eye + right_eye]) * frame_w) - 30
            y_min = int(min([lm.y for lm in left_eye + right_eye]) * frame_h) - 30
            x_max = int(max([lm.x for lm in left_eye + right_eye]) * frame_w) + 30
            y_max = int(max([lm.y for lm in left_eye + right_eye]) * frame_h) + 30

            # Ensure ROI is within frame boundaries
            x_min, y_min = max(0, x_min), max(0, y_min)
            x_max, y_max = min(frame_w, x_max), min(frame_h, y_max)

            # Crop and zoom the ROI
            zoomed_frame = frame[y_min:y_max, x_min:x_max]
            if zoomed_frame.size > 0:
                zoomed_frame = cv2.resize(zoomed_frame, (frame_w, frame_h))

            # Overlay the zoomed frame
            cv2.imshow("Zoomed Gaze View", zoomed_frame)

            # Gaze control logic
            # Get the center of the right eye landmarks as a reference point
            eye_x = int((right_eye[0].x + right_eye[1].x) / 2 * frame_w)

            # Detect direction of movement
            if prev_eye_x is not None:
                if eye_x > prev_eye_x + 5:
                    direction = "Right"
                elif eye_x < prev_eye_x - 5:
                    direction = "Left"
                else:
                    direction = "Center"
            prev_eye_x = eye_x

            # Display direction on the frame
            cv2.putText(
                frame,
                f"Direction: {direction}",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            # Map eye position to screen coordinates
            screen_x = screen_w / frame_w * eye_x

            # Move cursor continuously based on eye position
            pag.moveTo(screen_x, screen_h // 2)

            # Draw eye landmarks on the frame
            for eye_landmark in left_eye + right_eye:
                x = int(eye_landmark.x * frame_w)
                y = int(eye_landmark.y * frame_h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # Display the original frame
        cv2.imshow("Gaze Control with Direction", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    gaze_control_with_direction()
