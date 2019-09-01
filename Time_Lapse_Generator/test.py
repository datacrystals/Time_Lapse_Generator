import numpy as np
import cv2


def create_video_stream(path): # creates a video stream

    cap = cv2.VideoCapture(path) # creates the video capture

    return cap # return the video capture

def read_frame(cap, desired_size=(0,0)): # gets the desired size for the frame

    ret, frame = cap.read() # read the next frame

    if desired_size != (0,0): # if the user specified a desired size

        frame = cv2.resize(frame, desired_size) # resizes the image

    return frame # return the frame

cap = create_video_stream('Source_Data/Video/la.webm')

while(cap.isOpened()):
    frame = read_frame(cap,(1920,870))


    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
