#-------------------------------------------
# Authors: Sergio León & Álvaro García
# Description: ***Main*** script of software project
#-------------------------------------------

# External modules importation
import cv2
import mediapipe
import threading
import math

# Functions importation from external modules
from time import time

# Own modules importation
from constants import *
from helpers import *

#-------------------------------------------
## --- Main code --- ##
if __name__ == "__main__":
        
    camera = PiCamera()
    camera.resolution = (IMAGE_WIDTH, IMAGE_HEIGHT)
    camera.framerate = LOOP_FREQ
    camera.rotation = 180
    rawCapture = PiRGBArray(camera, size=(IMAGE_WIDTH, IMAGE_HEIGHT))
    
    bg_index = 0
    cooldown_counter = COOLDOWN_CLOSE_HAND_TIME
    
    bg_image = load_image(BACKGROUND_IMAGE_RELATIVE_PATH_LIST[bg_index])
    
    drawingModule = mediapipe.solutions.drawing_utils
    
    time.sleep(1)
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        prev_time_t = time.time()
        prev_time = time.time()
        current_frame = frame.array
        background_filter_thread = ThreadWithReturnValue(target=background_filter, args=[current_frame, bg_image])
        gesture_recognition_thread = ThreadWithReturnValue(target=gesture_recognition, args=[current_frame])
        background_filter_thread.start()
        gesture_recognition_thread.start()
        filtered_image = background_filter_thread.join()
        results = gesture_recognition_thread.join()
        if results.multi_hand_landmarks != None:
            for handLandmarks in results.multi_hand_landmarks:
                point_5 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.INDEX_FINGER_MCP]
                point_17 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.PINKY_MCP]
                point_0 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.WRIST]
                point_4 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.THUMB_TIP]
                pointer = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.INDEX_FINGER_TIP] # point_8
                point_8 = pointer
                point_12 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
                point_16 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.RING_FINGER_TIP]
                point_20 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.PINKY_TIP]
                
                distance_points_0_5 = math.sqrt(pow(point_0.x-point_5.x,2)+pow(point_0.y-point_5.y,2))
                distance_points_0_17 = math.sqrt(pow(point_0.x-point_17.x,2)+pow(point_0.y-point_17.y,2))
                distance_points_5_17 = math.sqrt(pow(point_5.x-point_17.x,2)+pow(point_5.y-point_17.y,2))
                distance_points_4_5 = math.sqrt(pow(point_4.x-point_5.x,2)+pow(point_4.y-point_5.y,2))
                #palm_area = 1/2*abs(point_0.x*(point_5.y-point_17.y)+point_5.x*(point_17.y-point_0.y)+point_17.x*(point_0.y-point_5.y))
                palm_perimeter = distance_points_5_17+distance_points_0_17+distance_points_0_5
                valid_orientation = ( (abs(distance_points_5_17/palm_perimeter-NORMDIST_5_17_TARGET)/NORMDIST_5_17_TARGET < ADMITTED_PALM_VARIATION) and \
                    (abs(distance_points_0_17/palm_perimeter-NORMDIST_0_17_TARGET)/NORMDIST_0_17_TARGET < ADMITTED_PALM_VARIATION) and \
                    (abs(distance_points_0_5/palm_perimeter-NORMDIST_0_5_TARGET)/NORMDIST_0_5_TARGET < ADMITTED_PALM_VARIATION))
                if (valid_orientation):
                    drawingModule.draw_landmarks(filtered_image, handLandmarks, mediapipe.solutions.hands.HAND_CONNECTIONS)
                    if(distance_points_4_5/palm_perimeter < CLICK_TRIGGERING):   
                        cv2.circle(filtered_image, (int(pointer.x*IMAGE_WIDTH), int(pointer.y*IMAGE_HEIGHT)), 20, (0,255,0), thickness=10)
                    else:
                        cv2.circle(filtered_image, (int(pointer.x*IMAGE_WIDTH), int(pointer.y*IMAGE_HEIGHT)), 20, (0,0,255), thickness=10)
                    distance_points_0_8 = math.sqrt(pow(point_0.x-point_8.x,2)+pow(point_0.y-point_8.y,2))
                    distance_points_0_12 = math.sqrt(pow(point_0.x-point_12.x,2)+pow(point_0.y-point_12.y,2))
                    distance_points_0_16 = math.sqrt(pow(point_0.x-point_16.x,2)+pow(point_0.y-point_16.y,2))
                    distance_points_0_20 = math.sqrt(pow(point_0.x-point_20.x,2)+pow(point_0.y-point_20.y,2))
                    if((distance_points_0_8/palm_perimeter < CLOSE_HAND_TRIGGER) and \
                        (distance_points_0_12/palm_perimeter < CLOSE_HAND_TRIGGER) and \
                        (distance_points_0_16/palm_perimeter < CLOSE_HAND_TRIGGER) and \
                        (distance_points_0_20/palm_perimeter < CLOSE_HAND_TRIGGER) and cooldown_counter == 0):
                        if (bg_index < MAX_INTERFACES-1):
                            bg_index = bg_index + 1
                        else:
                            bg_index = 0
                        bg_image = load_image(BACKGROUND_IMAGE_RELATIVE_PATH_LIST[bg_index])
                        cooldown_counter = COOLDOWN_CLOSE_HAND_TIME

        cv2.imshow("Camera Stream", filtered_image)
        cv2.waitKey(1) # in this case is not inteded to poll for a key pressed, but it is mandatory to create
        #an event to trigger window redrawing
        if cooldown_counter > 0:
            cooldown_counter = cooldown_counter - 1
        current_time = time.time()
        if((current_time - prev_time) < 1/LOOP_FREQ):
            time.sleep(1/LOOP_FREQ - current_time + prev_time)
        rawCapture.seek(0)
        rawCapture.truncate()
        current_time_t = time.time()
        print('loop frequency:', 1/(current_time_t-prev_time_t))



