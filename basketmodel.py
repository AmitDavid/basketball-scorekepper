import time
from threading import Thread, Lock

import numpy as np
import tensorflow.keras.models
from PIL import Image, ImageOps
from tensorflow.python.keras.engine.sequential import Sequential

from webcam import Webcam

# ---- Machine States Enums ---- #
STATE_BALL_IN_FRAME = 0
STATE_BALL_IN_BASKET = 1
STATE_NO_BALL = 2

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

PEN_MODEL = '21_06_14-pen_model.h5'
GREEN_BALL = '21_06_15-green_ball.h5'
BASKET_1 = '21_06_23-basket_1.h5'
BASKET_2 = '21_06_23-basket_2.h5'


def load_model(model_path: str = BASKET_2) -> {Sequential, None}:
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
        # Wait for webcam to load
        time.sleep(1)

        score_flag = False
        waiting_counter = 0
        waiting_limit = 10

        while True:
            prediction = self._predict()
            print(f' {prediction}')

            # Logic: After model decided ball is scored, don't score again until
            # waited for {waiting_limit} predictions with {STATE_NO_BALL}
            if score_flag and prediction == STATE_NO_BALL:
                waiting_counter += 1
                if waiting_counter == waiting_limit:
                    score_flag = False
                    waiting_counter = 0

            if score_flag is False and prediction == STATE_BALL_IN_BASKET:
                score_flag = True
                self._score_buffer_lock.acquire()
                self._score_buffer += 2
                self._score_buffer_lock.release()
            else:
                self._cycles_in_basket = 0

    def _predict(self) -> int:
        # Preprocess the image and convert array size
        image = Image.fromarray(self._webcam.get_frame_array())
        data = self._preprocess_frame(image)

        # Run model
        answer = self._trained_model.predict(data)
        print(f'{i}: {answer[0]}', end='')

        # Return the index of the most likely prediction
        if STATE_NO_BALL < 0.9 and STATE_BALL_IN_BASKET > STATE_BALL_IN_FRAME:
            return STATE_BALL_IN_BASKET

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
