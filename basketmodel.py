import threading
import time
from threading import Thread, Lock

import numpy as np
import tensorflow.keras.models
from PIL import Image, ImageOps
from tensorflow.python.keras.engine.sequential import Sequential

from webcam import Webcam

# ---- Machine States Enums ---- #
STATE_BALL_ABOVE_BASKET = 0
STATE_BALL_IN_BASKET = 1
STATE_BALL_MISSED_BASKET = 2
STATE_BALL_UNDER_BASKET = 3
STATE_NO_BALL = 4

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

PEN_MODEL = '21_06_14-pen_model.h5'
GREEN_BALL = '21_06_15-green_ball.h5'


def load_model(model_path: str = GREEN_BALL) -> {Sequential, None}:
    try:
        return tensorflow.keras.models.load_model(f'models/{model_path}')
    except (ImportError, IOError) as e:
        return None


class BasketModel:
    def __init__(self, trained_model: Sequential, webcam: Webcam):
        self._works = False
        self._mirror_image = False
        self._cycles_in_basket = 0

        self._webcam = webcam
        self._trained_model = trained_model

        self._score_buffer = 0
        self._score_buffer_lock = Lock()

        try:
            # Load the model
            self._thread = Thread(target=self._update, daemon=True)
            self._thread.start()
            self._works = True
        except (ImportError, IOError, RuntimeError) as e:
            pass

    def _update(self):
        # Wait for webcam to lead
        time.sleep(1)

        while True:
            curr_prediction = self._predict()

            if curr_prediction == STATE_BALL_IN_BASKET:
                self._cycles_in_basket += 1
            else:
                if self._cycles_in_basket >= 2:
                    self._score_buffer_lock.acquire()
                    self._score_buffer += 2
                    self._score_buffer_lock.release()
                self._cycles_in_basket = 0

    def _predict(self) -> int:
        # Preprocess the image and convert array size
        x = self._webcam.get_frame_array()
        y = Image.fromarray(x)
        data = self._preprocess_frame(y)

        # Run model
        answer = self._trained_model.predict(data)
        # Return the index of the most likely prediction
        return max((v, i) for i, v in enumerate(answer[0]))[1]

    @staticmethod
    def _preprocess_frame(frame: Image) -> np.ndarray:
        # Create the array of the right shape to feed into the keras model
        # The 'length' or number of images you can put into the array is
        # determined by the first position in the shape tuple, in this case 1.
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        # resize the image to a 224x224 with the same strategy as in TM2:
        # resizing the image to be at least 224x224 and then cropping from the center
        size = (224, 224)
        frame = ImageOps.fit(frame, size, Image.ANTIALIAS)

        # turn the image into a numpy array
        image_array = np.asarray(frame)

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        return data

    def get_score_buffer(self) -> int:
        while self._score_buffer_lock.locked():
            pass
        temp_score_buffer = self._score_buffer
        self._score_buffer = 0
        return temp_score_buffer
