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
        
def gesture_recognition(current_frame):
    results = hands.process(cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB))
    return results

        
        