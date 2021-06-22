import time
from threading import Thread

import cv2

VideoCapture = cv2.VideoCapture
FRAME_RATE = 30  # Must be: FRAME_RATE != 1


class Webcam:
    def __init__(self, index=0):
        self._cam = VideoCapture(index)
        self._frame_array = None
        self._image_bytes = None
        self._thread = None

        try:
            if self._cam.read()[0]:
                self._works = True
                self._thread = Thread(target=self._update, args=())
                self._thread.daemon = True
                self._thread.start()
            else:
                self._works = False
        except (ValueError, IOError) as e:
            self._works = False

    def _update(self):
        # Read the next frame from the stream in a different thread
        while True:
            # Read image from capture device (camera)
            self._frame_array = self._cam.read()[1]
            # Convert the image to PNG Bytes, and show in app
            self._image_bytes = cv2.imencode('.png', self._frame_array)[1].tobytes()
            # Wait for next read
            time.sleep(1 / (FRAME_RATE - 1))

    def get_frame(self):
        return self._frame_array, self._image_bytes

    def is_webcam_works(self):
        return self._works
