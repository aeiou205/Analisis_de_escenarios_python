import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Iniciar la captura de video
cap = cv2.VideoCapture(2)

# Configurar la detección de manos
with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        # Leer el cuadro de video
        success, image = cap.read()
        if not success:
            print("Error al leer el cuadro de video")
            break

        # Convertir la imagen de BGR a RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detectar las manos en la imagen
        results = hands.process(image)

        # Dibujar la línea entre THUMB_TIP e INDEX_FINGER_TIP
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 255),
                                           thickness=2,
                                           circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255),
                                           thickness=2))

                # Obtener las coordenadas de THUMB_TIP e INDEX_FINGER_TIP
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Convertir las coordenadas a píxeles de imagen
                image_height, image_width, _ = image.shape
                thumb_px = int(thumb_tip.x * image_width), int(thumb_tip.y * image_height)
                index_px = int(index_finger_tip.x * image_width), int(index_finger_tip.y * image_height)

                # Dibujar la línea
                cv2.line(image, thumb_px, index_px, (255, 0, 0), 2)

        # Mostrar la imagen resultante
        cv2.imshow('MediaPipe Hands', image)

        # Esperar por una tecla para salir
        if cv2.waitKey(5) & 0xFF == 27:
            break

# Liberar los recursos
cap.release()
cv2.destroyAllWindows()




