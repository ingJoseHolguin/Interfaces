import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import os
import random
import pyautogui
import tkinter as tk

# 📏 Resolución real
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
print(f"Resolución detectada: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# 🎯 Puntos de calibración
calibration_points = [(0.1, 0.1), (0.5, 0.1), (0.9, 0.1),
                      (0.1, 0.5), (0.5, 0.5), (0.9, 0.5),
                      (0.1, 0.9), (0.5, 0.9), (0.9, 0.9)]

# 🗂️ Carpetas de salida
base_dir = "iris_data"
left_eye_dir = os.path.join(base_dir, "left_eye")
right_eye_dir = os.path.join(base_dir, "right_eye")
os.makedirs(left_eye_dir, exist_ok=True)
os.makedirs(right_eye_dir, exist_ok=True)

# 🧠 Landmarks faciales seleccionados
selected_landmark_indices = [1, 33, 263, 70, 300, 105, 334, 152, 10, 9]  # nariz, cejas, barbilla, centro rostro...

# 🧾 DataFrame
columns = ["left_eye", "right_eye", "x_norm", "y_norm"] + \
          [f"lm{i}_x" for i in range(10)] + [f"lm{i}_y" for i in range(10)]
data_rows = []

# 🖥️ Mostrar punto con tkinter
def show_calibration_dot(x_ratio, y_ratio):
    def close():
        root.destroy()

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    canvas = tk.Canvas(root, bg="black")
    canvas.pack(fill="both", expand=True)

    x, y = int(x_ratio * SCREEN_WIDTH), int(y_ratio * SCREEN_HEIGHT)
    canvas.create_oval(x-10, y-10, x+10, y+10, fill="white", outline="")

    root.after(1500, close)
    root.mainloop()
    return x, y

# 🔍 Extraer ojo
def extract_eye(frame, landmarks, indices):
    h, w, _ = frame.shape
    pts = np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in indices])
    x, y, w_, h_ = cv2.boundingRect(pts)
    eye = frame[y:y+h_, x:x+w_]
    if eye.size == 0:
        return None
    eye = cv2.resize(eye, (64, 64))
    return cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)

# 🧠 Extraer vector de landmarks
def extract_landmark_vector(landmarks):
    vec = []
    for i in selected_landmark_indices:
        x = landmarks[i].x
        y = landmarks[i].y
        vec.append(x)
    for i in selected_landmark_indices:
        y = landmarks[i].y
        vec.append(y)
    return vec

# 📸 Captura de cámara
cap = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
counter = 0

print("🟢 Iniciando calibración multimodal...")

for rel_x, rel_y in calibration_points:
    abs_x, abs_y = show_calibration_dot(rel_x, rel_y)
    norm_x, norm_y = abs_x / SCREEN_WIDTH, abs_y / SCREEN_HEIGHT

    for _ in range(10):
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            left_eye = extract_eye(frame, landmarks, [474, 475, 476, 477])
            right_eye = extract_eye(frame, landmarks, [469, 470, 471, 472])
            landmark_vec = extract_landmark_vector(landmarks)

            if left_eye is not None and right_eye is not None:
                leye_name = f"left_{counter}.png"
                reye_name = f"right_{counter}.png"
                cv2.imwrite(os.path.join(left_eye_dir, leye_name), left_eye)
                cv2.imwrite(os.path.join(right_eye_dir, reye_name), right_eye)

                row = [leye_name, reye_name, norm_x, norm_y] + landmark_vec
                data_rows.append(row)
                counter += 1

        cv2.waitKey(100)

cap.release()
cv2.destroyAllWindows()

# 📝 Guardar archivo CSV
df = pd.DataFrame(data_rows, columns=columns)
df.to_csv(os.path.join(base_dir, "multimodal_labels.csv"), index=False)

print("✅ Datos multimodales guardados:")
print(f" - Izquierdo: {left_eye_dir}")
print(f" - Derecho : {right_eye_dir}")
print(f" - CSV     : {base_dir}/multimodal_labels.csv")
