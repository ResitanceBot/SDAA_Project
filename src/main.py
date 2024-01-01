#-------------------------------------------
# Authors: Sergio León & Álvaro García
# Description: ***Main*** script of software project
#-------------------------------------------

# External modules importation
import cv2
from threading import Thread

# Functions importation from external modules
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from mediapipe import solutions as mp_solutions
from time import time
from threading import Thread

# Own modules importation
from constants import *
from helpers import *

#-------------------------------------------
## Variables setup ##
segmentor = SelfiSegmentation()
bg_hmi_interface_image = load_image(BACKGROUND_IMAGE_RELATIVE_PATH_LIST)
handsModule = mp_solutions.hands
drawingModule = mp_solutions.drawing_utils

## --- Main code --- ##
if __name__ == "__main__":
    read_new_frame_thread = Thread(target=read_new_frame_picamera)
    show_image_thread = Thread(target=show_current_frame)
    read_new_frame_thread.start()
    time.sleep(5)
    show_image_thread.start()



