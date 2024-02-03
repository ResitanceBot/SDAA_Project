from picamera.array import PiRGBArray
from picamera import PiCamera
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import cv2
import time

camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 10
camera.rotation = 180
rawCapture = PiRGBArray(camera, size=(320, 240))

face_cascade = cv2.CascadeClassifier('/home/pi/opencv/data/haarcascades/haarcascade_frontalface_alt2.xml')

#cargar imagen de fondo
bg_image = cv2.imread('/home/pi/images.jpeg')
bg_image = cv2.resize(bg_image, (320, 240))

# creating segmentation instance for taking the foreground (the person).
segmentor = SelfiSegmentation()

time.sleep(1)

#initialize auxiliar variables for fps counting
prev_frame_timestamp = 0
new_frame_timestamp = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    
    # segmenting the image
    ar_image = segmentor.removeBG(image, bg_image, threshold=0.9)
    cv2.imshow("Camera Stream", ar_image)

    # fps trace
    new_frame_timestamp = time.time()
    fps = int(1/(new_frame_timestamp-prev_frame_timestamp))
    print(fps)
    prev_frame_timestamp = new_frame_timestamp

    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)

    if key == ord("q"):
        break
camera.close()
cv2.destroyAllWindows()
