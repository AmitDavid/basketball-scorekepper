import cv2

VideoCapture = cv2.VideoCapture

def load_camera(camera_index: int) -> VideoCapture:
    # initialize the camera
    return VideoCapture(camera_index)  # 0 -> index of camera


def capture_image(cam: VideoCapture):
    captured, image = cam.read()

    # frame captured without any errors
    if captured:
        # Debug
        # imshow("cam-test", image)
        # waitKey(0)
        # destroyWindow("cam-test")

        return image
