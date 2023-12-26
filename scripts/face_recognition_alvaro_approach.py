from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time
import numpy as np


camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 10
camera.rotation = 180
rawCapture = PiRGBArray(camera, size=(320, 240))

display_window = cv2.namedWindow("Faces")

face_cascade = cv2.CascadeClassifier('/home/pi/opencv/data/haarcascades/haarcascade_frontalface_alt2.xml')

time.sleep(1)

#initialize auxiliar variables for fps counting
prev_frame_timestamp = 0
new_frame_timestamp = 0

fixed_color = (255, 255, 255)  # Cambia esto por el color que desees en formato BGR

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    blank_image = np.full_like(image, fixed_color, dtype=np.uint8)  # Crea una imagen del mismo tamaño que la original y llena con el color fijo

    #Detección
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in faces:
        # Crea la bounding box
        cv2.rectangle(image, (x - int(w), y - int(h / 2)), (x + int(2 * w), y + int(3 * h)), (255, 0, 0), 2)

        # Crea la máscara para el área externa a la bounding box
        mask = np.zeros_like(image, dtype=np.uint8)
        cv2.rectangle(mask, (x - int(w), y - int(h / 2)), (x + int(2 * w), y + int(3 * h)), (255,255,255), -1)
        mask_inv = cv2.bitwise_not(mask)

        # Rellena el área fuera de la bounding box con el color fijo
        outside_bb = cv2.bitwise_and(blank_image, mask_inv)
        image = cv2.add(image, mask_inv)

    #Muestra ventana
    cv2.imshow("Camera Stream", image)
    new_frame_timestamp = time.time()
    fps = int(1 / (new_frame_timestamp - prev_frame_timestamp))
    print(fps)
    prev_frame_timestamp = new_frame_timestamp
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)

    if key == ord("q"):
        break

camera.close()
cv2.destroyAllWindows()
