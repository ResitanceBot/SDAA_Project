#-------------------------------------------
# Authors: Sergio León & Álvaro García
# Description: Functions definition
#-------------------------------------------

# External modules importation
import cv2
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import mediapipe
import math
import socket

# Functions importation from external modules
from threading import Semaphore
from threading import Thread
from picamera.array import PiRGBArray
from picamera import PiCamera
from cvzone.SelfiSegmentationModule import SelfiSegmentation

# Own modules importation
from constants import *

# ------------------------------------------

# Global variables
hands = mediapipe.solutions.hands.Hands(static_image_mode=False, \
    min_detection_confidence=MEDIAPIPE_HANDS_SENSITIVITY, \
    min_tracking_confidence=MEDIAPIPE_HANDS_SENSITIVITY, \
    max_num_hands=1)
segmentor = SelfiSegmentation()

class ThreadWithReturnValue(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def load_image(relative_path_list):
    root_project_path = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    image_path = root_project_path
    for step in relative_path_list:
        image_path = os.path.join(image_path, step)
    print('Loading image from : ', image_path)
    background_image = cv2.imread(image_path)
    print(background_image.shape[0])
    print(background_image.shape[1])
    if background_image is not None:
        if (
            background_image.shape[0] != IMAGE_HEIGHT
            and background_image.shape[1] != IMAGE_WIDTH
        ): # resize to desired shape if needed
            background_image = cv2.resize(background_image, [IMAGE_WIDTH, IMAGE_HEIGHT], interpolation= cv2.INTER_LINEAR)
            print(background_image.shape[0])
            print(background_image.shape[1])
        print('Image loaded succesfully')
        return background_image
    else:
        print('Image could not be read')
        return None
    
def background_filter(current_frame, bg_image):
    filtered_image = segmentor.removeBG(current_frame, bg_image, threshold=BG_FILTER_SENSITIVITY)
    return filtered_image
        
def hand_landmarks_detection(current_frame):
    results = hands.process(cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB))
    return results.multi_hand_landmarks

def gesture_recognition(multiHandLandmarks):
    # Initialize gesture to 
    gesture = "NON_GESTURE"
    
    for handLandmarks in multiHandLandmarks:
        point_0 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.WRIST]
        point_4 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.THUMB_TIP]
        point_5 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.INDEX_FINGER_MCP]
        point_8 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        point_12 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
        point_16 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.RING_FINGER_TIP]
        point_17 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.PINKY_MCP]
        point_20 = handLandmarks.landmark[mediapipe.solutions.hands.HandLandmark.PINKY_TIP]
        
        # defining pointer as point 8
        pointer = point_8
        
        # calculating distance between points
        distance_points_0_5 = math.sqrt(pow(point_0.x-point_5.x,2)+pow(point_0.y-point_5.y,2))
        distance_points_0_8 = math.sqrt(pow(point_0.x-point_8.x,2)+pow(point_0.y-point_8.y,2))
        distance_points_0_12 = math.sqrt(pow(point_0.x-point_12.x,2)+pow(point_0.y-point_12.y,2))
        distance_points_0_16 = math.sqrt(pow(point_0.x-point_16.x,2)+pow(point_0.y-point_16.y,2))
        distance_points_0_17 = math.sqrt(pow(point_0.x-point_17.x,2)+pow(point_0.y-point_17.y,2))
        distance_points_0_20 = math.sqrt(pow(point_0.x-point_20.x,2)+pow(point_0.y-point_20.y,2))
        distance_points_4_5 = math.sqrt(pow(point_4.x-point_5.x,2)+pow(point_4.y-point_5.y,2))
        distance_points_5_17 = math.sqrt(pow(point_5.x-point_17.x,2)+pow(point_5.y-point_17.y,2))
        
        # calculate invariant metric
        palm_perimeter =( distance_points_5_17+distance_points_0_17+distance_points_0_5)
        
        # filter to apply restrictions on click detection
        valid_orientation = ( (abs(distance_points_5_17/palm_perimeter-NORMDIST_5_17_TARGET)/NORMDIST_5_17_TARGET < ADMITTED_PALM_VARIATION) and \
            (abs(distance_points_0_17/palm_perimeter-NORMDIST_0_17_TARGET)/NORMDIST_0_17_TARGET < ADMITTED_PALM_VARIATION) and \
            (abs(distance_points_0_5/palm_perimeter-NORMDIST_0_5_TARGET)/NORMDIST_0_5_TARGET < ADMITTED_PALM_VARIATION))
        
        if (valid_orientation):
            if(distance_points_4_5/palm_perimeter < CLICK_TRIGGERING):   
                gesture = "CLICK_GESTURE"

        if((distance_points_0_8/palm_perimeter < CLOSE_HAND_TRIGGER) and \
            (distance_points_0_12/palm_perimeter < CLOSE_HAND_TRIGGER) and \
            (distance_points_0_16/palm_perimeter < CLOSE_HAND_TRIGGER) and \
            (distance_points_0_20/palm_perimeter < CLOSE_HAND_TRIGGER)):
            gesture = "CLOSE_HAND_GESTURE"
            
        return pointer, gesture
        
        
def command_interpreter(x,y):
    command = None
    distance_min = float('inf')
    # Picture frame checking
    if ((x<FRAME_LEFT_LIMIT_X or x>FRAME_RIGHT_LIMIT_X) or y<FRAME_UPPER_LIMIT_Y):
        for button, (button_x, button_y) in BUTTON_COORDINATES.items():
            dist = distance_calc(button_x, button_y, x, y)
            if dist < distance_min:
                distance_min = dist
                command = button
    return command

def distance_calc(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)

def send_command_UDP(UDP_PAYLOAD):
    print("Sending UDP command:", UDP_PAYLOAD)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(UDP_PAYLOAD, "utf-8"), (UDP_RECEIVER_IP, UDP_PORT))    
    sock.close()
    