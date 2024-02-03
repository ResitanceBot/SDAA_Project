from picamera.array import PiRGBArray
from picamera import PiCamera
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import cv2
import mediapipe
import time

cap = cv2.VideoCapture(0)

#Use MediaPipe to draw the hand framework over the top of hands it identifies in Real-Time
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands

face_cascade = cv2.CascadeClassifier('/home/pi/opencv/data/haarcascades/haarcascade_frontalface_alt2.xml')

time.sleep(1)

#initialize auxiliar variables for fps counting
prev_frame_timestamp = 0
new_frame_timestamp = 0

with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as hands:
    while True:
        ret, image = cap.read()
        
        #Produces the hand framework overlay ontop of the hand, you can choose the colour here too)
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        #In case the system sees multiple hands this if statment deals with that and produces another hand overlay
        if results.multi_hand_landmarks != None:
            for handLandmarks in results.multi_hand_landmarks:
                drawingModule.draw_landmarks(image, handLandmarks, handsModule.HAND_CONNECTIONS)

        #cargar imagen de fondo
        ar_image = cv2.imread('/home/pi/images.jpeg')
        ar_image = cv2.resize(ar_image, (320, 240))

        # creating segmentation instance for taking the foreground (the person).
        segmentor = SelfiSegmentation()

        # segmenting the image
        segmentated_img = segmentor.removeBG(image, ar_image, threshold=0.4)
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
        #cv2.imshow("Camera Stream", ar_image)
        new_frame_timestamp = time.time()
        fps = int(1/(new_frame_timestamp-prev_frame_timestamp))
        print(fps)
        prev_frame_timestamp = new_frame_timestamp
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
camera.close()
cv2.destroyAllWindows()
