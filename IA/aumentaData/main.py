import os
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import random

# Directorios
input_dir = './normal/'  # Directorio con tus imágenes originales
output_dir = './aumentado/'  # Directorio donde guardarás las siluetas aumentadas

# Crea el directorio de salida si no existe
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Lista todas las imágenes en el directorio de entrada
image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

# Número de imágenes aumentadas a generar por cada imagen original
num_augmentations_per_image = 10

# Contador para nombrar las nuevas imágenes
counter = 0

def convert_to_silhouette(image):
    """Convierte una imagen a silueta BLANCA sobre fondo NEGRO."""
    # Convertir a escala de grises si es necesario
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Aplicar umbral para crear una imagen binaria
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # IMPORTANTE: Invertir la imagen para tener silueta blanca sobre fondo negro
    thresh = cv2.bitwise_not(thresh)
    
    # Operaciones morfológicas para mejorar la silueta
    kernel = np.ones((5,5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Encontrar contornos para asegurarnos que tenemos la mano solamente
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 0:
        # Crear una máscara negra
        mask = np.zeros_like(thresh)
        
        # Encontrar solo el contorno más grande (la mano)
        max_contour = max(contours, key=cv2.contourArea)
        
        # Dibujar el contorno relleno en BLANCO
        cv2.drawContours(mask, [max_contour], 0, 255, -1)
        
        # Usar esta máscara como la silueta final
        thresh = mask
    
    # Asegurar que la silueta está en 224x224
    silhouette = cv2.resize(thresh, (224, 224))
    
    return silhouette

for img_file in image_files:
    # Carga la imagen con OpenCV
    img_path = os.path.join(input_dir, img_file)
    original_img = cv2.imread(img_path)
    
    if original_img is None:
        print(f"No se pudo cargar la imagen: {img_path}")
        continue
    
    # Convertir a silueta
    silhouette = convert_to_silhouette(original_img)
    
    # Guardar la silueta original
    output_path = os.path.join(output_dir, f'rock_original_{counter:04d}.png')
    cv2.imwrite(output_path, silhouette)
    counter += 1
    
    # Generar versiones aumentadas
    for i in range(num_augmentations_per_image):
        # Crear una copia de la silueta para esta transformación
        augmented = silhouette.copy()
        
        # 1. Rotación aleatoria
        if random.random() > 0.5:
            angle = random.uniform(-15, 15)
            h, w = augmented.shape[:2]
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
            augmented = cv2.warpAffine(augmented, M, (w, h), borderValue=0)
        
        # 2. Zoom (recorte y redimensionamiento)
        if random.random() > 0.5:
            h, w = augmented.shape[:2]
            # Recorta entre 0-15% de cada lado
            crop_percent = random.uniform(0, 0.15)
            x = int(w * crop_percent)
            y = int(h * crop_percent)
            w_new = int(w * (1 - 2 * crop_percent))
            h_new = int(h * (1 - 2 * crop_percent))
            
            # Asegurarse de que el recorte no sea demasiado grande
            if w_new > 0 and h_new > 0:
                augmented = augmented[y:y+h_new, x:x+w_new]
                augmented = cv2.resize(augmented, (224, 224))
        
        # 3. Traslación (desplazamiento)
        if random.random() > 0.5:
            h, w = augmented.shape[:2]
            shift_x = random.randint(-30, 30)  # Píxeles a desplazar en X
            shift_y = random.randint(-30, 30)  # Píxeles a desplazar en Y
            M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
            augmented = cv2.warpAffine(augmented, M, (w, h), borderValue=0)
        
        # 4. Escalado no uniforme (estirar o comprimir)
        if random.random() > 0.6:
            h, w = augmented.shape[:2]
            scale_x = random.uniform(0.9, 1.1)
            scale_y = random.uniform(0.9, 1.1)
            scaled_w = int(w * scale_x)
            scaled_h = int(h * scale_y)
            
            if scaled_w > 0 and scaled_h > 0:
                augmented = cv2.resize(augmented, (scaled_w, scaled_h))
                
                # Crear una imagen negra y centrar la imagen escalada
                result = np.zeros((224, 224), dtype=np.uint8)
                
                # Calcular coordenadas para centrar
                x_offset = max(0, (224 - scaled_w) // 2)
                y_offset = max(0, (224 - scaled_h) // 2)
                
                # Pegar la parte que cabe en el lienzo
                if x_offset + scaled_w <= 224 and y_offset + scaled_h <= 224:
                    result[y_offset:y_offset+scaled_h, x_offset:x_offset+scaled_w] = augmented
                else:
                    # Si es más grande que 224x224, recortar
                    crop_w = min(scaled_w, 224)
                    crop_h = min(scaled_h, 224)
                    result[0:crop_h, 0:crop_w] = augmented[0:crop_h, 0:crop_w]
                
                augmented = result
        
        # 5. Erosión o dilatación (cambiar ligeramente el grosor de la silueta)
        if random.random() > 0.6:
            kernel_size = random.randint(1, 3)
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            if random.random() > 0.5:  # Erosión: adelgazar la silueta
                augmented = cv2.erode(augmented, kernel, iterations=1)
            else:  # Dilatación: engrosar la silueta
                augmented = cv2.dilate(augmented, kernel, iterations=1)
        
        # 6. Pequeña distorsión de perspectiva
        if random.random() > 0.7:
            h, w = augmented.shape[:2]
            # Crear puntos de origen
            pts1 = np.float32([[0,0], [w,0], [0,h], [w,h]])
            
            # Crear puntos destino con pequeña distorsión
            shift = 20  # Máximo desplazamiento en píxeles
            pts2 = np.float32([
                [0+random.randint(0,shift), 0+random.randint(0,shift)],
                [w-random.randint(0,shift), 0+random.randint(0,shift)],
                [0+random.randint(0,shift), h-random.randint(0,shift)],
                [w-random.randint(0,shift), h-random.randint(0,shift)]
            ])
            
            # Aplicar transformación de perspectiva
            M = cv2.getPerspectiveTransform(pts1, pts2)
            augmented = cv2.warpPerspective(augmented, M, (w, h), borderValue=0)
        
        # Asegurarse de que la imagen final sea de 224x224
        augmented = cv2.resize(augmented, (224, 224))
        
        # Guardar la imagen aumentada
        output_path = os.path.join(output_dir, f'rock_{counter:04d}.png')
        cv2.imwrite(output_path, augmented)
        counter += 1

print(f"Generadas {counter} imágenes en total (incluyendo originales).")