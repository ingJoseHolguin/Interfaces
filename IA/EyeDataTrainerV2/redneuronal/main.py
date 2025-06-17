import os
import cv2
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import keras
from keras import layers, models, Input, Model

# 📥 Cargar CSV
df = pd.read_csv("iris_data/multimodal_labels.csv")

# Leer imágenes y vector de landmarks
X_left, X_right, X_landmarks, y = [], [], [], []
for _, row in df.iterrows():
    leye_path = os.path.join("iris_data/left_eye", row["left_eye"])
    reye_path = os.path.join("iris_data/right_eye", row["right_eye"])

    left_img = cv2.imread(leye_path, cv2.IMREAD_GRAYSCALE)
    right_img = cv2.imread(reye_path, cv2.IMREAD_GRAYSCALE)

    if left_img is not None and right_img is not None:
        X_left.append(left_img / 255.0)
        X_right.append(right_img / 255.0)
        landmark_vec = row.iloc[4:].values.astype(np.float32)
        X_landmarks.append(landmark_vec)
        y.append([row["x_norm"], row["y_norm"]])

# Convertir a arreglos
X_left = np.array(X_left).reshape(-1, 64, 64, 1)
X_right = np.array(X_right).reshape(-1, 64, 64, 1)
X_landmarks = np.array(X_landmarks)
y = np.array(y)

# Dividir datos
(Xl_train, Xl_test,
 Xr_train, Xr_test,
 Xm_train, Xm_test,
 y_train, y_test) = train_test_split(
    X_left, X_right, X_landmarks, y, test_size=0.2, random_state=42
)

# 🧠 Subred CNN para ojo
def build_eye_branch(name):
    inp = Input(shape=(64, 64, 1), name=f"{name}_input")
    x = layers.Conv2D(32, (3, 3), activation='relu')(inp)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)

    x = layers.Conv2D(64, (3, 3), activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)

    x = layers.Flatten()(x)
    return inp, x

# Subred densa para landmarks
def build_landmark_branch():
    inp = Input(shape=(20,), name="landmark_input")
    x = layers.Dense(64, activation='relu')(inp)
    x = layers.BatchNormalization()(x)
    return inp, x

# Crear ramas
left_input, left_branch = build_eye_branch("left_eye")
right_input, right_branch = build_eye_branch("right_eye")
landmark_input, landmark_branch = build_landmark_branch()

# 🔗 Fusión
combined = layers.Concatenate()([left_branch, right_branch, landmark_branch])
x = layers.Dense(128, activation='relu')(combined)
x = layers.Dropout(0.3)(x)
x = layers.Dense(64, activation='relu')(x)
output = layers.Dense(2)(x)  # salida normalizada

# Definir modelo final
model = Model(inputs=[left_input, right_input, landmark_input], outputs=output)
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Entrenar
history = model.fit(
    [Xl_train, Xr_train, Xm_train], y_train,
    validation_split=0.1,
    epochs=30,
    batch_size=16
)

# Evaluar
loss, mae = model.evaluate([Xl_test, Xr_test, Xm_test], y_test)
print(f"MAE en coordenadas normalizadas: {mae:.4f}")

# Guardar modelo
model.save("iris_gaze_multimodal.keras")
