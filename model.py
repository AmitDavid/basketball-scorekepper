import numpy as np
from PIL import Image, ImageOps
from tensorflow.python.keras.engine.sequential import Sequential

PEN_MODEL = '21_06_14-pen_model.h5'
GREEN_BALL = '21_06_15-green_ball.h5'


def load_model(model_path: str) -> {Sequential, None}:
    import tensorflow.keras.models
    # Disable scientific notation for clarity
    np.set_printoptions(suppress=True)

    try:
        # Load the model
        return tensorflow.keras.models.load_model(f'models/{GREEN_BALL}')
    except (ImportError, IOError) as e:
        return None


def preprocess_frame(frame: np.ndarray) -> np.ndarray:
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


def predict(frame_array: np.ndarray, trained_model: Sequential) -> int:
    # Preprocess the image and convert array size
    data = preprocess_frame(Image.fromarray(frame_array))

    # Run model
    answer = trained_model.predict(data)

    # Return the index of the most likely prediction
    return max((v, i) for i, v in enumerate(answer[0]))[1]
