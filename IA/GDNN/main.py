import os
import numpy as np
from PIL import Image
from keras import models, layers
from tensorflow.keras.layers import Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

gestures = {'L_': 'L',
           'fi': 'Fist',
           'ok': 'Okay',
           'pe': 'Peace',
           'pa': 'Palm',
           'ro': 'Rock'
           }

gestures_map = {'Fist': 0,
                'L': 1,
                'Okay': 2,
                'Palm': 3,
                'Peace': 4,
                'Rock': 5
                }


def process_image(path):
    # Abre y redimensiona la imagen
    img = Image.open(path)
    img = img.convert('RGB')  # Convertimos explícitamente a RGB
    img = img.resize((224, 224))
    # Convertimos a array y aseguramos dtype correcto
    img_array = np.array(img, dtype='float32')
    # Normalizamos aquí directamente
    img_array /= 255.0
    return img_array

def process_data(X_data, y_data):
    # Convertimos a arrays numpy
    X_data = np.array(X_data, dtype='float32')
    # Ya NO hacemos ninguna transformación de canales aquí
    # Solo verificamos la forma para depuración
    print(f"Forma de X_data: {X_data.shape}")
    
    # Procesamos las etiquetas
    y_data = np.array(y_data)
    y_data = to_categorical(y_data)
    print(f"Forma de y_data: {y_data.shape}")
    
    return X_data, y_data

def walk_file_tree(relative_path):
    X_data = []
    y_data = []
    
    for directory, subdirectories, files in os.walk(relative_path):
        for file in files:
            if not file.startswith('.'):
                try:
                    path = os.path.join(directory, file)
                    # Si tus archivos L tienen formato L_XXX.jpg
                    if file.startswith('L_'):
                        gesture_name = 'L'
                        # Procesamos la imagen y la añadimos
                        processed_img = process_image(path)
                        X_data.append(processed_img)
                        y_data.append(gestures_map[gesture_name])
                    else:
                        # Usamos minúsculas para mayor compatibilidad
                        prefix = file[0:2].lower()
                        if prefix in gestures:
                            gesture_name = gestures[prefix]
                            # Procesamos la imagen y la añadimos
                            processed_img = process_image(path)
                            X_data.append(processed_img)
                            y_data.append(gestures_map[gesture_name])
                        else:
                            print(f"Prefijo desconocido: {prefix} en archivo: {file}, omitiendo...")
                except Exception as e:
                    print(f"Error procesando {file}: {e}")
            else:
                continue
    
    if len(X_data) == 0:
        raise ValueError("No se encontraron imágenes válidas. Verifica la ruta y los archivos.")
    
    # Procesamos los datos
    X_data, y_data = process_data(X_data, y_data)
    return X_data, y_data


class Data(object):
    def __init__(self):
        self.X_data = []
        self.y_data = []

    def get_data(self):
        return self.X_data, self.y_data


relative_path = './silhouettes/'
rgb = False

X_data, y_data = walk_file_tree(relative_path)
X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=12, stratify=y_data)

model = models.Sequential()
model.add(layers.Conv2D(32, (5, 5), strides=(2, 2), activation='relu', input_shape=(224, 224, 3)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Flatten())
model.add(layers.Dense(128, activation='relu'))
model.add(layers.Dense(128, activation='relu'))
model.add(layers.Dense(128, activation='relu'))
model.add(Dropout(0.25, seed=21))
model.add(layers.Dense(6, activation='softmax')) 

model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=4, batch_size=64, validation_data=(X_test, y_test), verbose=1)

# evaluate the keras model
_, accuracy = model.evaluate(X_data, y_data)
print('Accuracy: %.2f' % (accuracy*100))
# make class predictions with the model
#predictions = (model.predict(X_data) > 0.5).astype(int)
# summarize the first 5 cases
#for i in range(5):
#    print('{} (expected {})'.format(predictions[i], y_data[i]))


file_path = './saved_model.hdf5'
# Guardar el Modelo
model.save(file_path)


# Recrea el mismo modelo  desde el archivo
from tensorflow.keras.models import load_model
loaded_model = load_model(file_path)

gesture_names = {0: 'Fist',
                 1: 'L',
                 2: 'Okay',
                 3: 'Palm',
                 4: 'Peace',
                 5: 'Rock'}

for i in range(5):
    pred_array = loaded_model.predict(X_data[i].reshape(1, 224, 224, 3))
    #print(f'pred_array: {pred_array}')
    result = gesture_names[np.argmax(pred_array)]
    #print(f'Result: {result}')
    #print(max(pred_array[0]))
    score = float("%0.2f" % (max(pred_array[0]) * 100))
    print('{} (score {})'.format(result, score))

