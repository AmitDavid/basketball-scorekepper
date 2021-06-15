import cv2
import numpy as np

VideoCapture = cv2.VideoCapture


def load_webcam(index=0) -> {VideoCapture, None}:
    cam = VideoCapture(index)
    try:
        if cam.read()[0]:
            return cam

    except (ValueError, IOError) as e:
        return None

    return None


def capture_frame(cam: VideoCapture) -> (np.ndarray, bytes):
    # Read image from capture device (camera)
    frame_array = cam.read()[1]
    # Convert the image to PNG Bytes, and show in app
    image_bytes = cv2.imencode('.png', frame_array)[1].tobytes()

    return frame_array, image_bytes
