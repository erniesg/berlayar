import mediapipe as mp
import numpy as np
import cv2
import pygame
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# For webcam input:
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

last_sound_time = 0  # Tracks when the sound was last played
sound_cooldown = 2  # Cooldown in seconds

pygame.mixer.init()
sound = pygame.mixer.Sound('sample_out.mp3')

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Function to draw hand landmarks on the frame
def draw_hand_landmarks(frame, landmarks):
    # Assuming landmarks is a list of landmarks with x, y, z coordinates normalized to the image size
    for landmark in landmarks:
        x = int(landmark.x * frame.shape[1])
        y = int(landmark.y * frame.shape[0])
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

# Create a gesture recognizer instance with the live stream mode:
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    print('gesture recognition result: {}'.format(result))
    handle_gesture(result)

def handle_gesture(result):
    global last_sound_time  # Use the global variable for tracking sound play time
    current_time = time.time()

    # Access attributes directly without subscripting
    gesture_recognition_results = result  # Get the hand gesture recognition results
    print("Received gesture recognition results:", gesture_recognition_results)

    # Check if any hand gestures were recognized
    if gesture_recognition_results.gestures:
        # Iterate over detected hands
        for hand_gestures in gesture_recognition_results.gestures:
            # Check each gesture in the list
            for gesture in hand_gestures:
                # Check if the gesture is a closed fist with a high confidence
                if gesture.category_name == 'Closed_Fist' and gesture.score >= 0.75 and current_time - last_sound_time > sound_cooldown:
                    print("High confidence closed fist gesture detected!")
                    # Play the audio if a closed fist gesture with high confidence is detected and cooldown has passed
                    sound.play()
                    last_sound_time = current_time  # Update the last sound time to now
                else:
                    print("Other gesture detected or confidence too low:", gesture)
    else:
        print("No gestures recognized.")


# Setup MediaPipe Gesture Recognizer
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

recognizer = GestureRecognizer.create_from_options(options)

cap = cv2.VideoCapture(0)  # Use webcam

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a later selfie-view display
    frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    #mp_frame = mp.framework.formats.image_frame.ImageFrame(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    timestamp_ms = int(time.time() * 1000)

    # Process the image and detect gestures
    recognizer.recognize_async(mp_image, timestamp_ms)
    # Display the frame
    # To improve performance, optionally mark the frame as not writeable to pass by reference.
    frame.flags.writeable = False
    results = hands.process(frame)

    # Draw the hand annotations on the image.
    frame.flags.writeable = True

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),  # Green color for landmarks
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),  # Red color for connections
            )

    # Display the processed frame
    cv2.imshow('MediaPipe Hands', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
