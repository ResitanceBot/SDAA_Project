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

time.sleep(1)

#initialize auxiliar variables for fps counting
prev_frame_timestamp = 0
new_frame_timestamp = 0

#cargar imagen de fondo
bg_image = cv2.imread('/home/pi/images.jpeg')
bg_image = cv2.resize(bg_image, (320, 240))
bg_image = cv2.resize(bg_image, (640, 480))
# creating segmentation instance for taking the foreground (the person).
segmentor = SelfiSegmentation()

with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as hands:
    while True:

        ret, image = cap.read()
        image = cv2.rotate(image, cv2.ROTATE_180)
        
        #Produces the hand framework overlay ontop of the hand, you can choose the colour here too)
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        #In case the system sees multiple hands this if statment deals with that and produces another hand overlay
        if results.multi_hand_landmarks != None:
            for handLandmarks in results.multi_hand_landmarks:
                drawingModule.draw_landmarks(image, handLandmarks, handsModule.HAND_CONNECTIONS)

        # segmenting the image
        ar_image = segmentor.removeBG(image, bg_image, threshold=0.4)
        cv2.imshow("Camera Stream", ar_image)

        # trace fps
        new_frame_timestamp = time.time()
        fps = int(1/(new_frame_timestamp-prev_frame_timestamp))
        print(fps)
        prev_frame_timestamp = new_frame_timestamp

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        
cv2.destroyAllWindows()
