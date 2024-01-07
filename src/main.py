#-------------------------------------------
# Authors: Sergio León & Álvaro García
# Description: ***Main*** script of software project
#-------------------------------------------

# External modules importation
import cv2
import mediapipe
import threading

# Functions importation from external modules
from time import time

# Own modules importation
from constants import *
from helpers import *

#-------------------------------------------
## --- Main code --- ##
if __name__ == "__main__":
        
    # create PiCamera related objects to use camera
    camera = PiCamera()
    camera.resolution = (IMAGE_WIDTH, IMAGE_HEIGHT)
    camera.framerate = LOOP_FREQ
    camera.rotation = 180
    rawCapture = PiRGBArray(camera, size=(IMAGE_WIDTH, IMAGE_HEIGHT))
    
    # load initial background image
    bg_image = load_image(BACKGROUND_IMAGE_RELATIVE_PATH_LIST[0])
    
    # create mediapipe drawing utility object
    drawingModule = mediapipe.solutions.drawing_utils
    
    # General variables initialization
    bg_index = 0
    light_state = False
    
    # wait some seconds for camera to be operative
    time.sleep(1)
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # loop start timestamp
        prev_time_t = time.time()
        # algorithm start timestamp
        prev_time = prev_time_t
        
        # read latest frame
        current_frame = frame.array
        current_frame = cv2.flip(current_frame,1)
        
        # parallel processing using threads (background filter + hand landmarks detection)
        background_filter_thread = ThreadWithReturnValue(target=background_filter, args=[current_frame, bg_image])
        hand_landmarks_detection_thread = ThreadWithReturnValue(target=hand_landmarks_detection, args=[current_frame])
        background_filter_thread.start()
        hand_landmarks_detection_thread.start()
        filtered_image = background_filter_thread.join()
        multiHandsLandmarks = hand_landmarks_detection_thread.join()
        
        if multiHandsLandmarks is not None:
            # draw landmarks on image
            for handLandmarks in multiHandsLandmarks:
                drawingModule.draw_landmarks(filtered_image, handLandmarks, mediapipe.solutions.hands.HAND_CONNECTIONS)
        
            # detect open/close hand & click gestures
            pointer, gesture_type = gesture_recognition(multiHandsLandmarks)
            
            if gesture_type is "CLICK_GESTURE":
                    cv2.circle(filtered_image, (int(pointer.x*IMAGE_WIDTH), int(pointer.y*IMAGE_HEIGHT)), 20, (0,255,0), thickness=10)
                    command = command_interpreter(int(pointer.x*IMAGE_WIDTH), int(pointer.y*IMAGE_HEIGHT))
                    if command is 'LIGHT':
                        if (light_state is False):
                            command = 'LIGHT_ON'
                        else:
                            command = 'LIGHT_OFF'
                    send_command_UDP(command)
            elif gesture_type is "CLOSE_HAND_GESTURE":
                if (bg_index < MAX_INTERFACES-1):
                    bg_index = bg_index + 1
                else:
                    bg_index = 0
                bg_image = load_image(BACKGROUND_IMAGE_RELATIVE_PATH_LIST[bg_index])
            else:
                cv2.circle(filtered_image, (int(pointer.x*IMAGE_WIDTH), int(pointer.y*IMAGE_HEIGHT)), 20, (0,0,255), thickness=10)
        
        cv2.imshow("Camera Stream", filtered_image)
        cv2.waitKey(1) # in this case is not inteded to poll for a key pressed, but it is mandatory to create
        # an event to trigger window redrawing
       
        # algorithm end timestamp
        current_time = time.time()
        if((current_time - prev_time) < 1/LOOP_FREQ):
            time.sleep(1/LOOP_FREQ - current_time + prev_time)
            
        # clear camera buffer
        rawCapture.seek(0)
        rawCapture.truncate()
        
        # loop end timestamp
        current_time_t = time.time()
        print('FPS achieved:', 1/(current_time_t-prev_time_t))



