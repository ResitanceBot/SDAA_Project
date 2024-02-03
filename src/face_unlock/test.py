import cv2
import face_recognition
from picamera.array import PiRGBArray
from picamera import PiCamera

# Imagen a comparar
image = cv2.imread("/home/pi/SDAA_Project/src/face_unlock/imgs/biden.jpg")
#face_loc = face_recognition.face_locations(image)
#print("face_loc:", face_loc)
# print(face_loc[0][3])
# print(face_loc[0][2])
# print(face_loc[0][1])
# print(face_loc[0][0])
#cv2.rectangle(image, (face_loc[0][3], face_loc[0][0]), (face_loc[0][1], face_loc[0][2]), (0, 255, 0))
#cv2.imshow("image",image)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

face_image_encodings = face_recognition.face_encodings(image, known_face_locations=[(241, 740, 562, 419)])[0]
print("face_image_encodings:", face_image_encodings)
while True:
    a = 1

######################################################################################
# Video Streaming

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
camera.rotation = 180
rawCapture = PiRGBArray(camera, size=(640, 480))

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = frame.array
     
    face_locations = face_recognition.face_locations(frame, model="cnn")
    ## PARECE DEMASIADO COSTOSO COMPUTACIONALMENTE PARA RPI
    #if face_locations != []:
    #    for face_location in face_locations:
    #        face_frame_encodings = face_recognition.face_encodings(frame, known_face_locations=[face_location])[0]
    #        result = face_recognition.compare_faces([face_image_encodings], face_frame_encodings)
    #        #print("Result:", result)
#
    #        if result[0] == True:
    #            text = "Biden"
    #            color = (125, 220, 0)
    #        else:
    #            text = "Desconocido"
    #            color = (50, 50, 255)
#
    #        cv2.rectangle(frame, (face_location[3], face_location[2]), (face_location[1], face_location[2] + 30), color, -1)
    #        cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), color, 2)
    #        cv2.putText(frame, text, (face_location[3], face_location[2] + 20), 2, 0.7, (255, 255, 255), 1)


    cv2.imshow("Frame", frame)
    k = cv2.waitKey(1)
    if k == 27 & 0xFF:
        break
      
    rawCapture.seek(0)
    rawCapture.truncate()

cv2.destroyAllWindows()