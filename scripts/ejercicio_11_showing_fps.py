from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time

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

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array

    #Detección
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x,y,w,h) in faces:
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)

    #Muestra ventana
    cv2.imshow("Faces", image)
    new_frame_timestamp = time.time()
    fps = int(1/(new_frame_timestamp-prev_frame_timestamp))
    print(fps)
    prev_frame_timestamp = new_frame_timestamp
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)

    if key == ord("q"):
        cv2.imwrite('resultado.jpg',image)
        break
camera.close()
cv2.destroyAllWindows()
