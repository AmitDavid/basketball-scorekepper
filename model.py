from threading import Thread, Lock

import numpy as np
import tensorflow.keras.models
from PIL import Image, ImageOps
from tensorflow.python.keras.engine.sequential import Sequential

from webcam import Webcam

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

PEN_MODEL = '21_06_14-pen_model.h5'
GREEN_BALL = '21_06_15-green_ball.h5'


class Model:
    def __init__(self, model_name: str, webcam: Webcam):
        self._works = False
        self._webcam = webcam

        self._score_buffer = 0
        self._score_buffer_lock = Lock()

        try:
            # Load the model
            self._model = tensorflow.keras.models.load_model(f'models/{GREEN_BALL}')
            self._thread = Thread(target=self._predict, daemon=True)
            self._thread.start()
            self._works = True
        except (ImportError, IOError, RuntimeError) as e:
            pass

    @staticmethod
    def _preprocess_frame(frame: np.ndarray) -> np.ndarray:
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

    def _predict(self, frame_array: np.ndarray, trained_model: Sequential) -> int:
        while True:
            # Preprocess the image and convert array size
            data = self._preprocess_frame(Image.fromarray(self._webcam.get_frame_array()))

            # Run model
            answer = trained_model.predict(data)

            # Return the index of the most likely prediction
            return max((v, i) for i, v in enumerate(answer[0]))[1]

    def get_score_buffer(self):
        while self._score_buffer_lock.locked():
            pass
        return self._score_buffer
