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

# Semaphores
current_frame_semaphore = Semaphore(1)
filtered_image_semaphore = Semaphore(1)

def load_image(relative_path_list):
    root_project_path = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    image_path = root_project_path
    for step in relative_path_list:
        image_path = os.path.join(image_path, step)
    print('Loading image from : ', image_path)
    background_image = cv2.imread(image_path)
    if background_image is not None:
        if (
            background_image.shape[0] != IMAGE_HEIGHT
            and background_image.shape[1] != IMAGE_WIDTH
        ): # resize to desired shape if needed
            background_image.resize(IMAGE_HEIGHT, IMAGE_WIDTH)
        print('Image loaded succesfully')
        return background_image
    else:
        print('Image could not be read')
        return None
    
def read_new_frame_opencv():
    global current_frame_semaphore
    global current_frame
    camera = cv2.VideoCapture(0) #workaround: delete and create object in loop
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
    # camera.set(cv2.CAP_PROP_BUFFERSIZE, 0) # do not work on raspberry pi camera hardware,
    # meaning it will buffer all frames to be read, producing latency... not a good idea
    while True:
        prev_time_t = time.time()
        prev_time = time.time()
        new_frame_confirmation, current_frame_raw = camera.read()
        if new_frame_confirmation:
            current_frame_semaphore.acquire()
            current_frame = cv2.rotate(current_frame_raw, cv2.ROTATE_180)
            current_frame_semaphore.release()
        current_time = time.time()
        if((current_time - prev_time) < 1/LOOP_FREQ):
            time.sleep(1/LOOP_FREQ - current_time + prev_time)
        current_time_t = time.time()
        print('hilo read:', 1/(current_time_t-prev_time_t))
        
def read_new_frame_picamera():
    global current_frame_semaphore
    global current_frame
    camera = PiCamera()
    camera.resolution = (IMAGE_WIDTH, IMAGE_HEIGHT)
    camera.framerate = LOOP_FREQ
    camera.rotation = 180
    rawCapture = PiRGBArray(camera, size=(IMAGE_WIDTH, IMAGE_HEIGHT))
    
    time.sleep(1)
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        prev_time_t = time.time()
        prev_time = time.time()
        current_frame_semaphore.acquire()
        current_frame = frame.array
        current_frame_semaphore.release()
        current_time = time.time()
        if((current_time - prev_time) < 1/LOOP_FREQ):
            time.sleep(1/LOOP_FREQ - current_time + prev_time)
        rawCapture.seek(0)
        rawCapture.truncate()
        current_time_t = time.time()
        print('hilo read:', 1/(current_time_t-prev_time_t))
            
def show_current_frame():
    global filtered_image_semaphore
    global current_frame
    while True:
        prev_time_t = time.time()
        prev_time = time.time()
        filtered_image_semaphore.acquire()
        cv2.imshow("Camera Stream", filtered_image)
        filtered_image_semaphore.release()
        cv2.waitKey(1) # in this case is not inteded to poll for a key pressed, but it is mandatory to create
        #an event to trigger window redrawing
        current_time = time.time()
        if((current_time - prev_time) < 1/LOOP_FREQ):
            time.sleep(1/LOOP_FREQ - current_time + prev_time)
        current_time_t = time.time()
        print('hilo show:', 1/(current_time_t-prev_time_t))

def background_filter():
    global current_frame_semaphore
    global filtered_image_semaphore
    global current_frame
    global filtered_image
    segmentor = SelfiSegmentation()
    bg_image = load_image(BACKGROUND_IMAGE_RELATIVE_PATH_LIST)
    while True:
        prev_time_t = time.time()
        prev_time = time.time()
        current_frame_semaphore.acquire()
        filtered_image_semaphore.acquire()
        filtered_image = segmentor.removeBG(current_frame, bg_image, threshold=BG_FILTER_SENSITIVITY)
        filtered_image_semaphore.release()
        current_frame_semaphore.release()
        current_time = time.time()
        if((current_time - prev_time) < 1/LOOP_FREQ):
            time.sleep(1/LOOP_FREQ - current_time + prev_time)
        current_time_t = time.time()
        print('hilo read:', 1/(current_time_t-prev_time_t))
        
def gesture_recognition():
    drawingModule = mediapipe.solutions.drawing_utils
    handsModule = mediapipe.solutions.hands
    
    with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as hands:
        
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if results.multi_hand_landmarks != None:
            for handLandmarks in results.multi_hand_landmarks:
                drawingModule.draw_landmarks(image, handLandmarks, handsModule.HAND_CONNECTIONS)
        
        