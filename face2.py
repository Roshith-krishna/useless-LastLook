import os 
import mediapipe as mp
import cv2 as cv
import numpy as np
from deepface import DeepFace
import time
import random
import threading
import pygame

AUDIO_FILE = "bye2.mp3"

mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)


last_shutdown_time = 0
shutdown_cooldown = 10  
def shutdown():
    print("Simulated Shutdown. [DEBUG MODE]")

    # if os.name == 'nt':
    #     os.system("shutdown /s /t 1")
    # else:
    #     os.system("shutdown now")

def play_audio_and_shutdown():
    print("🔊 bye the bye na pokunnu")
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(AUDIO_FILE)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print("Audio playback error:", e)
    shutdown()

def trigger_shutdown(reason):
    global last_shutdown_time
    if time.time() - last_shutdown_time < shutdown_cooldown:
        return
    last_shutdown_time = time.time()
    print(f"❌ Shutdown Triggered: {reason}")
    threading.Thread(target=play_audio_and_shutdown).start()

def detect_face_expression(frame):
    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        emotion = result[0]['dominant_emotion']
        return emotion
    except Exception as e:
        print("DeepFace error:", e)
        return None

def detect_face_direction(face_landmarks, image_width):
    try:
        keypoints = face_landmarks.location_data.relative_keypoints
        left_eye = keypoints[0]
        right_eye = keypoints[1]
        center_x = (left_eye.x + right_eye.x) / 2
        if 0.4 < center_x < 0.6:
            return "looking"
        else:
            return "not_looking"
    except:
        return "unknown"


def random_shutdown_easter_egg():
    wait_time = random.randint(1, 300000)
    print(f"🥚 Easter egg: will shutdown in {wait_time} seconds (secretly)")
    time.sleep(wait_time)
    play_audio_and_shutdown()

threading.Thread(target=random_shutdown_easter_egg, daemon=True).start()

cap = cv.VideoCapture(0)

no_face_counter = 0
frame_count = 0
expression_check_interval = 30

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv.flip(frame, 1)
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = face_detection.process(frame_rgb)

    if results.detections:
        no_face_counter = 0
        for detection in results.detections:
            direction = detect_face_direction(detection, frame.shape[1])
            if direction != "looking":
                trigger_shutdown("Not looking at the screen")
                break

            if frame_count % expression_check_interval == 0:
                emotion = detect_face_expression(frame)
                if emotion:
                    print(f"🧠 Detected emotion: {emotion}")
                    if emotion in ["angry", "sad", "happy"]:
                        trigger_shutdown(f"{emotion.capitalize()} face detected")
                        break
    else:
        no_face_counter += 1
        if no_face_counter > 15:
            trigger_shutdown("No face detected for a while")

    frame_count += 1
    cv.imshow("Useless Detector 5000", frame)
    if cv.waitKey(1) & 0xFF == ord(' '):
        break

cap.release()
cv.destroyAllWindows()
