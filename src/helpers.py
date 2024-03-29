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
import pickle
import face_recognition

# Functions importation from external modules
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
        #valid_orientation = ( (abs(distance_points_5_17/palm_perimeter-NORMDIST_5_17_TARGET)/NORMDIST_5_17_TARGET < ADMITTED_PALM_VARIATION) and \
        #    (abs(distance_points_0_17/palm_perimeter-NORMDIST_0_17_TARGET)/NORMDIST_0_17_TARGET < ADMITTED_PALM_VARIATION) and \
        #    (abs(distance_points_0_5/palm_perimeter-NORMDIST_0_5_TARGET)/NORMDIST_0_5_TARGET < ADMITTED_PALM_VARIATION) and \
        #    (distance_points_0_8/palm_perimeter < CLOSE_HAND_TRIGGER) and (distance_points_0_12/palm_perimeter < CLOSE_HAND_TRIGGER) \
        #    (distance_points_0_16/palm_perimeter < CLOSE_HAND_TRIGGER) and (distance_points_0_20/palm_perimeter < CLOSE_HAND_TRIGGER))
        valid_orientation = True
        
        if (valid_orientation):
            if(distance_points_4_5/palm_perimeter < CLICK_TRIGGERING):   
                gesture = "CLICK_GESTURE"

        if((distance_points_0_8/palm_perimeter < CLOSE_HAND_TRIGGER) and \
            (distance_points_0_12/palm_perimeter < CLOSE_HAND_TRIGGER) and \
            (distance_points_0_16/palm_perimeter < CLOSE_HAND_TRIGGER) and \
            (distance_points_0_20/palm_perimeter < CLOSE_HAND_TRIGGER)):
            gesture = "CLOSE_HAND_GESTURE"
            
        return pointer, gesture
    
def face_processing(frame):
    # Load model
    data = pickle.loads(open("/home/pi/SDAA_Project/src/face_recognition/encodings.pickle", "rb").read())
    
    
    # Detect the fce boxes
    boxes = face_recognition.face_locations(frame)
	# compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []

	# loop over the facial embeddings
    for encoding in encodings:
	    # attempt to match each face in the input image to our known
	    # encodings
        matches = face_recognition.compare_faces(data["encodings"],	encoding, 0.5)
        name = "Unknown" #if face is not recognized, then print Unknown

        # check to see if we have found a match
        if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
            name = max(counts, key=counts.get)

		# update the list of names
        names.append(name)
        
    return boxes, names
    
def command_interpreter(x,y):
    command = None

    # Speed bar area
    if ((x > SPEEDBAR_LEFT_LIMIT_X and x < SPEEDBAR_RIGHT_LIMIT_X) and (y > SPEEDBAR_UPPER_LIMIT_Y and y < SPEEDBAR_LOWER_LIMIT_Y)):
        command = 'S' + str(int(((y-SPEEDBAR_UPPER_LIMIT_Y) / (SPEEDBAR_LOWER_LIMIT_Y-SPEEDBAR_UPPER_LIMIT_Y))*100))
    # Button association
    else: 
        for button, (button_x, button_y) in BUTTON_COORDINATES.items():
            if ((x > button_x-BUTTON_TOLERANCE and x < button_x+BUTTON_TOLERANCE) and (y > button_y-BUTTON_TOLERANCE and y < button_y+BUTTON_TOLERANCE)):
                command = button
                        
    return command

def send_command_UDP(UDP_PAYLOAD):
    print("Sending UDP command:", UDP_PAYLOAD)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(UDP_PAYLOAD, "utf-8"), (UDP_RECEIVER_IP, UDP_PORT))
    sock.close()
