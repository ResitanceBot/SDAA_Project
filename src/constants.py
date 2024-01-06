IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
BACKGROUND_IMAGE_RELATIVE_PATH_LIST = [['resources', 'panel-controller.png'], ['resources', 'relax.jpg']] # relative to root project folder
MAX_INTERFACES = 2
LOOP_FREQ = 10
BG_FILTER_SENSITIVITY = 0.2 # 0 to 1
MEDIAPIPE_HANDS_SENSITIVITY = 0.2 # 0 to 1
NORMDIST_0_5_TARGET = 0.43
NORMDIST_0_17_TARGET = 0.37
NORMDIST_5_17_TARGET = 0.19
ADMITTED_PALM_VARIATION = 0.25 # Max error considered valid to identify hand (% per 1)
SAFE_DIVISION_MIN = 0.01
CLICK_TRIGGERING = 0.12
CLOSE_HAND_TRIGGER = 0.5
BUTTON_COORDINATES = {
    'FORW': (50, 160),
    'BACK': (50, 265),
    'RIGHT': (50, 372),
    'LEFT': (585, 160),
    'S0': (585, 265),
    'S100': (265, 50),
    'LIGHT': (372, 50)
}
# Button asociation, Frame Limits
FRAME_RIGHT_LIMIT_X = 520
FRAME_LEFT_LIMIT_X = 120
FRAME_UPPER_LIMIT_Y = 120
FRAME_LOWER_LIMIT_Y = 430
# UDP connection
UDP_RECEIVER_IP = '192.168.100.34' # Host IP who receives UDP msgs
UDP_PORT = 1234 # Port number 
