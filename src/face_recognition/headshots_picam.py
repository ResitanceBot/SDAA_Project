import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray

name = 'Sergio' #replace with your name

cam = PiCamera()
cam.resolution = (640, 480)
cam.framerate = 10
cam.rotation = 180
rawCapture = PiRGBArray(cam, size=(640, 480))
    
img_counter = 0

while True:
    for frame in cam.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        cv2.imshow("Press Space to take a photo", image)
        rawCapture.truncate(0)
    
        k = cv2.waitKey(1)
        rawCapture.truncate(0)
        if k%256 == 27: # ESC pressed
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = "/home/pi/SDAA_Project/src/face_recognition/dataset/"+ name +"/image_{}.jpg".format(img_counter)
            cv2.imwrite(img_name, image)
            print("{} written!".format(img_name))
            img_counter += 1
            
    if k%256 == 27:
        print("Escape hit, closing...")
        break

cv2.destroyAllWindows()
