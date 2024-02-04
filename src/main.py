#-------------------------------------------
# Authors: Sergio León & Álvaro García
# Description: ***Main*** script of software project
#-------------------------------------------

# External modules importation
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
    light_state = False
    light_button_pressed = False
    lockTime = 0
    currentMode = "OPERATOR_SCREEN"
    operatorDetected = False
    
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
        
        if currentMode == "OPERATOR_SCREEN":
        
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
                            if not light_button_pressed:
                                light_button_pressed = True
                                if (light_state is False):
                                    command = 'LIGHT_ON'
                                    light_state = True
                                else:
                                    command = 'LIGHT_OFF'
                                    light_state = False
                        else:
                            light_button_pressed = False
                        if command is not None and command is not 'LIGHT':
                            send_command_UDP(command)
                elif gesture_type is "CLOSE_HAND_GESTURE":
                    light_button_pressed = False
                    lockTime = time.time()
                    currentMode = "LOCK_SCREEN"
                    bg_image = load_image(BACKGROUND_IMAGE_RELATIVE_PATH_LIST[1])
                else:
                    cv2.circle(filtered_image, (int(pointer.x*IMAGE_WIDTH), int(pointer.y*IMAGE_HEIGHT)), 20, (0,0,255), thickness=10)
                    light_button_pressed = False
                    
        elif currentMode == "LOCK_SCREEN":
            #añadir face_recognition
            background_filter_thread = ThreadWithReturnValue(target=background_filter, args=[current_frame, bg_image])
            #face_recognition_thread = ThreadWithReturnValue(target=face_recognition, args=[current_frame])
            #face_recognition_thread.start()
            background_filter_thread.start()
            filtered_image = background_filter_thread.join()
            #[boxes, names] = face_recognition_thread.join()
            boxes, names = face_processing(current_frame)
            
            timeInterval = time.time() - lockTime
            
            # Edit Image
            for ((top, right, bottom, left), name) in zip(boxes, names):
		        # draw the predicted face name on the image - color is in BGR
                cv2.rectangle(filtered_image, (left, top), (right, bottom),(0, 255, 225), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(filtered_image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.8, (0, 255, 255), 2)
                if name == "Sergio" and timeInterval > COOLDOWN_LOCK_SCREEN:
                    operatorDetected = True  
            
            if (timeInterval > COOLDOWN_LOCK_SCREEN):
                if operatorDetected:
                    currentMode = "OPERATOR_SCREEN"
                    bg_image = load_image(BACKGROUND_IMAGE_RELATIVE_PATH_LIST[0])
                    operatorDetected = False
            else:
                cooldown_msg = "Unlock available in: " + str(int(COOLDOWN_LOCK_SCREEN - timeInterval)) + "s"
                filtered_image = cv2.putText(filtered_image, cooldown_msg, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
            
            filtered_image = cv2.putText(filtered_image, "LOCKED SCREEN", (240,400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                  
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



