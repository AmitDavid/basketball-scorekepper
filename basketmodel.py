import time
from threading import Lock, Thread

import numpy as np
import tensorflow.keras.models
from PIL import Image, ImageOps
from tensorflow.python.keras.engine.sequential import Sequential

from webcam import Webcam

# ---- Machine States Enums ---- #
STATE_BALL_IN_BASKET = 0
STATE_BALL_UNDER_BASKET = 1
STATE_NO_BALL = 2


# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

SIZE = (224, 224)

MODEL_NAME = '28_06_23-basket_12.h5'


def load_model() -> {Sequential, None}:
    try:
        return tensorflow.keras.models.load_model(f'models/{MODEL_NAME}')
    except (ImportError, IOError) as e:
        pass

    return None


class BasketModel:
    def __init__(self, trained_model: Sequential, webcam: Webcam, start_thread: bool = True):
        self._works = False

        self._webcam = webcam
        self._trained_model = trained_model

        self._score_buffer = 0
        self._score_buffer_lock = Lock()
        if start_thread:
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

        waiting_limit = 15  # waiting_limit >= 0
        waiting_counter = 0

        cycles_in_basket_limit = 1  # cycles_in_basket_limit > 0
        cycles_in_basket = 0

        while True:
            prediction = self._predict()

            # Logic: If we get {STATE_BALL_IN_BASKET} for {cycles_in_basket_limit} frames in a row,
            # add score to {self._score_buffer} and wait for {waiting_limit} frames with {STATE_NO_BALL},
            # only afterward keep looking for new score
            if waiting_counter == 0:
                if prediction == STATE_BALL_IN_BASKET:
                    cycles_in_basket -= 1
                else:
                    cycles_in_basket = cycles_in_basket_limit

                if cycles_in_basket == 0:
                    self._score_buffer_lock.acquire()
                    self._score_buffer += 2
                    self._score_buffer_lock.release()
                    waiting_counter = waiting_limit
            else:
                if prediction == STATE_NO_BALL:
                    waiting_counter -= 1
                if waiting_counter == 0:
                    print('------------------------------------')

    def _predict(self) -> int:
        # Preprocess the image and convert array size
        image = Image.fromarray(self._webcam.get_frame_array())
        data = self._preprocess_frame(image)

        # Run model
        answer = self._trained_model.predict(data)[0]
        class_answer = max((v, i) for i, v in enumerate(answer))[1]
        if answer[STATE_NO_BALL] < 0.9:
            print(f'{answer} {class_answer}')

        # Force STATE_NO_BALL in some cases.
        if 0.85 >= answer[STATE_BALL_IN_BASKET] >= 0.5:
            return STATE_NO_BALL

        return class_answer

    @staticmethod
    def _preprocess_frame(frame: Image) -> np.ndarray:
        # Create the array of the right shape to feed into the keras model
        # The 'length' or number of images you can put into the array is
        # determined by the first position in the shape tuple, in this case 1.
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        # resize the image to a 224x224 with the same strategy as in TM2:
        # resizing the image to be at least 224x224 and then cropping from the center
        frame = ImageOps.fit(frame, SIZE, Image.ANTIALIAS)

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
