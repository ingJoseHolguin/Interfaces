import numpy as np
import keras
import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui

# Resolución real de pantalla
screen_width, screen_height = pyautogui.size()

# Cargar modelo
model = keras.models.load_model("iris_gaze_multimodal.keras")

# MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

left_iris_indices = [474, 475, 476, 477]
right_iris_indices = [469, 470, 471, 472]
landmark_indices = [1, 33, 263, 70, 300, 105, 334, 152, 10, 9]

def extract_eye(frame, landmarks, indices):
    h, w, _ = frame.shape
    pts = np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in indices])
    x, y, w_, h_ = cv2.boundingRect(pts)
    eye = frame[y:y+h_, x:x+w_]
    if eye.size == 0:
        return None
    eye = cv2.resize(eye, (64, 64))
    return cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)

def extract_landmark_vector(landmarks):
    vec = []
    for i in landmark_indices:
        vec.append(landmarks[i].x)
    for i in landmark_indices:
        vec.append(landmarks[i].y)
    return np.array(vec, dtype=np.float32)

def draw_grid_black(frame, rows=3, cols=3, color=(100, 100, 100), thickness=1):
    h, w = frame.shape[:2]
    dy, dx = h // rows, w // cols
    for y in range(1, rows):
        cv2.line(frame, (0, y * dy), (w, y * dy), color, thickness)
    for x in range(1, cols):
        cv2.line(frame, (x * dx, 0), (x * dx, h), color, thickness)

# Captura de cámara
cap = cv2.VideoCapture(0)

# Crear ventana sin bordes
root = tk.Tk()
root.overrideredirect(True)
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.lift()
root.attributes("-topmost", True)

canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="black", highlightthickness=0)
canvas.pack()

def update():
    ret, frame = cap.read()
    if not ret:
        root.after(10, update)
        return

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    # Crear fondo negro
    black_frame = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        left_eye = extract_eye(frame, landmarks, left_iris_indices)
        right_eye = extract_eye(frame, landmarks, right_iris_indices)
        landmark_vec = extract_landmark_vector(landmarks)

        if left_eye is not None and right_eye is not None:
            l_input = left_eye.reshape(1, 64, 64, 1) / 255.0
            r_input = right_eye.reshape(1, 64, 64, 1) / 255.0
            lm_input = landmark_vec.reshape(1, 20)

            x_norm, y_norm = model.predict([l_input, r_input, lm_input], verbose=0)[0]
            x_screen = int(x_norm * screen_width)
            y_screen = int(y_norm * screen_height)

            # Dibujar punto verde sobre fondo negro
            cv2.circle(black_frame, (x_screen, y_screen), 12, (0, 255, 0), -1)

    # Dibujar cuadrícula opcional
    draw_grid_black(black_frame, rows=3, cols=3)

    # Mostrar en tkinter
    image = Image.fromarray(cv2.cvtColor(black_frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=image)
    canvas.create_image(0, 0, anchor="nw", image=imgtk)
    canvas.imgtk = imgtk

    root.after(10, update)

def quit_on_esc(event):
    cap.release()
    root.destroy()

topmost_enabled = True  # estado inicial

def toggle_topmost(event):
    global topmost_enabled
    topmost_enabled = not topmost_enabled
    root.attributes("-topmost", topmost_enabled)
    print(f"🔁 Ventana al frente: {'Sí' if topmost_enabled else 'No'}")

root.bind("<Escape>", quit_on_esc)
root.bind("t", toggle_topmost)
update()
root.mainloop()
