import time
from threading import Thread, Lock

import cv2
import numpy as np

VideoCapture = cv2.VideoCapture
SAMPLE_RATE = 65  # SAMPLE_RATE > 0

SIZE = (448, 448)
DIFF_THRESHOLD = 3000000


class Webcam:
    def __init__(self, name: str, index=0):
        self._name = name
        self._cam = VideoCapture(index)

        self._works = False
        self._thread = None

        self._frame_array = None
        self._frame_array_lock = Lock()

        self._image_bytes = None
        self._image_bytes_lock = Lock()

        try:
            if self._cam.read()[0]:
                self._thread = Thread(target=self._update, daemon=True)
                self._thread.start()
                self._works = True
        except (ValueError, IOError, RuntimeError) as e:
            pass

    def _update(self, save_image=False) -> None:
        # Read the next frame from the stream in a different thread
        files_numbering = 0
        last_image = np.zeros([448, 448, 3], dtype='uint8')

        while True:
            frame_captured, image = self._cam.read()
            if frame_captured:
                # Crop image to desired size, keep only the center of the frame
                x, y, c = image.shape  # x > SIZE[0], y > SIZE[1]
                start_x = (x - SIZE[0]) // 2
                start_y = (y - SIZE[1]) // 2
                image = image[start_x:start_x + SIZE[0], start_y:start_y + SIZE[1], :]

                # Read image from capture device (camera)
                self._frame_array_lock.acquire()
                self._frame_array = image
                self._frame_array_lock.release()

                # Convert the image to PNG Bytes, and show in app
                temp_image_bytes = cv2.imencode('.png', self._frame_array)[1].tobytes()
                self._image_bytes_lock.acquire()
                self._image_bytes = temp_image_bytes
                self._image_bytes_lock.release()

                # Save image if there is a difference bigger then {DIFF_THRESHOLD} between
                # it and the saved image
                if save_image and cv2.absdiff(last_image, image).sum() > DIFF_THRESHOLD:
                    cv2.imwrite(f'../images_{self._name}/img_{str(files_numbering).zfill(5)}.jpg',
                                image, (cv2.IMWRITE_JPEG_QUALITY, 90))
                    print(f'Image saved to folder {self._name}. Image number:\t{files_numbering}')
                    last_image = image
                    files_numbering += 1

            # Wait for next read
            time.sleep(1 / SAMPLE_RATE)

    def is_webcam_works(self) -> bool:
        return self._works

    def get_frame_array(self) -> np.ndarray:
        while self._frame_array_lock.locked():
            pass
        return self._frame_array

    def get_image_bytes(self) -> bytes:
        while self._image_bytes_lock.locked():
            pass
        return self._image_bytes


# For finding camera indexs
if __name__ == '__main__':
    is_working = True
    dev_port = 0
    working_ports = []
    available_ports = []
    while is_working:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            is_working = False
            print("Port %s is not working." % dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" % (dev_port, h, w))
                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." % (dev_port, h, w))
                available_ports.append(dev_port)
        dev_port += 1
