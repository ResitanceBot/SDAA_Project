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

time.sleep(1)

#initialize auxiliar variables for fps counting
prev_frame_timestamp = 0
new_frame_timestamp = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    
    #cargar imagen de fondo
    ar_image = cv2.imread('/home/pi/images.jpeg')
    ar_image = cv2.resize(ar_image, (320, 240))
    
    # creating segmentation instance for taking the foreground (the person).
    segmentor = SelfiSegmentation()
    
    # segmenting the image
    segmentated_img = segmentor.removeBG(frame, ar_image, threshold=0.9)
    cv2.imshow("Camera Stream", segmentated_img)
    image_ = cv2.add(segmentated_img,ar_image)
    

    #Detección
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x,y,w,h) in faces:
        upper_corner_x = x-int(w)
        upper_corner_y = y-int(h/2)
        down_corner_x = x+int(2*w)
        down_corner_y = y+int(3*h)
        cv2.rectangle(image, (upper_corner_x, upper_corner_y), (down_corner_x, down_corner_y), (255,0,0), 2)
        ar_image[upper_corner_y:(down_corner_y+1), upper_corner_x:(down_corner_x+1)] = image[upper_corner_y:(down_corner_y+1), upper_corner_x:(down_corner_x+1)]
    #Muestra ventana
    cv2.imshow("Camera Stream", ar_image)
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
