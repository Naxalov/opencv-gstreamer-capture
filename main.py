
import cv2

# Setting up the camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    print(frame.shape)

    

cap.release()
cv2.destroyAllWindows()