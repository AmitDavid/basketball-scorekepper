import cv2
import numpy as np

VideoCapture = cv2.VideoCapture

def load_camera(camera_index: int) -> VideoCapture:
    # initialize the camera
    return VideoCapture(camera_index)


def capture_frame(cam: VideoCapture) -> np.ndarray:
    captured, frame = cam.read()

    # frame captured without any errors
    if captured:
        # Debug
        # imshow("cam-test", image)
        # waitKey(0)
        # destroyWindow("cam-test")

        return frame
