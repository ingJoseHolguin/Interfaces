import cv2
import mediapipe as mp
import pygame
import pyautogui
import numpy as np
import time

# Initialize MediaPipe and Pygame
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Definir el radio como una constante global
radius = 15

screen_width = pyautogui.size()[0]  
screen_height = pyautogui.size()[1] 
print(f"Screen dimensions: {screen_width}x{screen_height}")

# Definir puntos de calibración
calibration_points = [
    (radius, radius),                                 
    (screen_width - radius, radius),                  
    (screen_width - radius, screen_height - radius),  
    (radius, screen_height - radius),                 
    (screen_width // 2, screen_height // 2)   
]

# Hay dos opciones para corregir el error:
# OPCIÓN 1: Modificar la función para que use el radio global
def draw_calibration_point(position, screen):
    """Dibujar un punto de calibración en la pantalla"""
    screen.fill(BLACK)
    pygame.draw.circle(screen, WHITE, position, radius + 5)
    pygame.display.flip()


def run_calibration():
    """Ejecutar el proceso de calibración mostrando puntos en la pantalla"""
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Calibración Eye Tracking")
    
    # Para cada punto de calibración
    for point_idx, point in enumerate(calibration_points):
        print(f"Mostrando punto {point_idx+1}: {point}")

        draw_calibration_point(point, screen)
       
        start_time = time.time()
        while time.time() - start_time < 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    return False
        
        screen.fill(BLACK)
        font = pygame.font.Font(None, 36)
        text = font.render(f"Punto {point_idx+1} completado", True, WHITE)
        screen.blit(text, (screen_width//2 - text.get_width()//2, screen_height//2))
        pygame.display.flip()
        time.sleep(0.5)
    
    # Mostrar mensaje de finalización
    screen.fill(BLACK)
    font = pygame.font.Font(None, 48)
    text = font.render("¡Calibración completada!", True, WHITE)
    screen.blit(text, (screen_width//2 - text.get_width()//2, screen_height//2 - 50))
    
    font = pygame.font.Font(None, 36)
    text = font.render("Presiona cualquier tecla para continuar", True, WHITE)
    screen.blit(text, (screen_width//2 - text.get_width()//2, screen_height//2 + 50))
    pygame.display.flip()
    
    # Esperar a que se presione una tecla
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                waiting = False
    
    # Cerrar la ventana de calibración
    pygame.display.quit()
    print("Calibración completada.")
    return True

# Función para ejecutar el eye tracking normal después de la calibración
def run_eye_tracking():
    # Set magnification factor and band height
    magnification = 3
    band_height = pyautogui.size()[1] * 0.1
    band_width = pyautogui.size()[0] * 0.1  # Added band_width for x-direction tracking

    # Create Pygame window for magnified band
    window = pygame.display.set_mode(
        (int(band_width * magnification), int(band_height * magnification)))  # Convertir a enteros
    pygame.display.set_caption("Eye Tracking Magnifier")

    def magnify_screen(x_position, y_position):
        # Capture screenshot and magnify band at gaze position
        screenshot = pyautogui.screenshot()
        screenshot_pygame = pygame.image.fromstring(screenshot.tobytes(), screenshot.size, screenshot.mode)
        magnified = pygame.transform.scale(screenshot_pygame,
                                        (screenshot.size[0] * magnification, screenshot.size[1] * magnification))
        # Convertir coordenadas a enteros para evitar errores
        x_pos = int(x_position * magnification)
        y_pos = int(y_position * magnification)
        band_w = int(band_width * magnification)
        band_h = int(band_height * magnification)
        band = magnified.subsurface((x_pos, y_pos, band_w, band_h))
        return band

    # Start webcam capture
    cap = cv2.VideoCapture(0)

    # Usar el nombre correcto del parámetro: refine_landmarks en lugar de refine_landmark
    with mp_face_mesh.FaceMesh(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        refine_landmarks=True) as face_mesh:  # Corregido a refine_landmarks
        
        initial_nose_position = None  # To hold the initial nose position
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar el fotograma.")
                break

            # Define ROI
            height, width, _ = frame.shape
            roi_x = width // 4
            roi_y = height // 2
            roi_width = width // 2
            roi_height = height // 2
            roi = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]

            # Convert the ROI to RGB before processing
            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            # Flip the image horizontally for a later selfie-view display
            roi_rgb = cv2.flip(roi_rgb, 1)

            # Process the ROI and get the results
            results = face_mesh.process(roi_rgb)

            # Draw the face landmarks on the ROI
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(roi_rgb, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION)

                    # Get nose position (nose tip)
                    nose_tip = face_landmarks.landmark[4]
                    if initial_nose_position is None:
                        initial_nose_position = (nose_tip.x, nose_tip.y)
                        print("Posición inicial de la nariz establecida:", initial_nose_position)

                    # Calculate distance moved from initial position
                    distance_moved = ((nose_tip.x - initial_nose_position[0]) ** 2 + (
                                nose_tip.y - initial_nose_position[1]) ** 2) ** 0.5
                    
                    # If distance moved is above a certain threshold, update gaze position
                    if distance_moved > 0.02:  # Made it 5 times more sensitive to movement
                        # Calcular posición de la mirada ajustada por ROI
                        gaze_position_x = (nose_tip.x * roi_width + roi_x) * pyautogui.size()[0] / width
                        gaze_position_y = (nose_tip.y * roi_height + roi_y) * pyautogui.size()[1] / height
                        
                        # Magnify screen at gaze position
                        try:
                            band = magnify_screen(gaze_position_x, gaze_position_y)
                            window.blit(band, (0, 0))
                            pygame.display.flip()
                        except ValueError as e:
                            print(f"Error en magnify_screen: {e}")
                            print(f"Coordenadas: x={gaze_position_x}, y={gaze_position_y}")
                            # Continuar con el siguiente frame si hay un error

            # Convert ROI back to BGR for display
            roi_bgr = cv2.cvtColor(roi_rgb, cv2.COLOR_RGB2BGR)
            
            # Display the ROI with landmarks
            cv2.imshow('ROI with landmarks', roi_bgr)

            # Break the loop when 'q' is pressed
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    print("Eye tracking finalizado.")

# Función principal que ejecuta calibración y luego eye tracking
def main():
    print("Iniciando el programa...")
    
    # Primero ejecutar la calibración
    calibration_success = run_calibration()
    
    if calibration_success:
        # Si la calibración es exitosa, ejecutar el eye tracking
        print("Iniciando eye tracking...")
        run_eye_tracking()
    else:
        print("Calibración cancelada. Saliendo del programa.")

if __name__ == "__main__":
    main()