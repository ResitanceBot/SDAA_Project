from picamera.array import PiRGBArray
from picamera import PiCamera
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import cv2
import mediapipe
import time



cap = cv2.VideoCapture(0)
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

#Use MediaPipe to draw the hand framework over the top of hands it identifies in Real-Time
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands

time.sleep(1)

#initialize auxiliar variables for fps counting
prev_frame_timestamp = 0
new_frame_timestamp = 0

#cargar imagen de fondo
bg_image = cv2.imread('/home/pi/images.jpeg')
bg_image = cv2.resize(bg_image, (IMAGE_WIDTH, IMAGE_HEIGHT))
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
                # Obtener landmarks de la mano
                thumb_tip = handLandmarks.landmark[handsModule.HandLandmark.THUMB_TIP]
                index_tip = handLandmarks.landmark[handsModule.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = handLandmarks.landmark[handsModule.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = handLandmarks.landmark[handsModule.HandLandmark.RING_FINGER_TIP]
                pinky_tip = handLandmarks.landmark[handsModule.HandLandmark.PINKY_TIP]
                thumb_mcp = handLandmarks.landmark[handsModule.HandLandmark.THUMB_MCP]
                index_mcp = handLandmarks.landmark[handsModule.HandLandmark.INDEX_FINGER_MCP]
                middle_mcp = handLandmarks.landmark[handsModule.HandLandmark.MIDDLE_FINGER_MCP]
                ring_mcp = handLandmarks.landmark[handsModule.HandLandmark.RING_FINGER_MCP]
                pinky_mcp = handLandmarks.landmark[handsModule.HandLandmark.PINKY_MCP]
                drawingModule.draw_landmarks(image, handLandmarks, handsModule.HAND_CONNECTIONS)

                THUMB_Y_THRESHOLD = 30
                INDEX_FINGER_Y_THRESHOLD = 30
                MIDDLE_FINGER_Y_THRESHOLD = 45
                RING_FINGER_Y_THRESHOLD = 45
                PINKY_FINGER_Y_THRESHOLD = 30
                
                # no es robusto a zoom, pero no se me ocurre referencia con la que normalizarlo
                # a pesar de ello, para un rango de funcionamiento normal, no debe haber problema
                # con estos umbrales ya que hay margen de diferencia entre los 2 tipos de clasificación
                print('dst', 480*abs(index_tip.y-index_mcp.y))
                print('dst', 480*abs(middle_tip.y-middle_mcp.y))
                print('dst', 480*abs(ring_tip.y-ring_mcp.y))
                print('dst', 480*abs(pinky_tip.y-pinky_mcp.y))
                if(
                    #480*abs(thumb_tip.y-thumb_mcp.y)<THUMB_Y_THRESHOLD and
                   480*abs(index_tip.y-index_mcp.y)<INDEX_FINGER_Y_THRESHOLD
                   and 480*abs(middle_tip.y-middle_mcp.y)<MIDDLE_FINGER_Y_THRESHOLD
                   and 480*abs(ring_tip.y-ring_mcp.y)<RING_FINGER_Y_THRESHOLD
                   and 480*abs(pinky_tip.y-pinky_mcp.y)<PINKY_FINGER_Y_THRESHOLD):
                    print('Mano cerrada detectada')
                else:
                    print('Mano abierta detectada')

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
