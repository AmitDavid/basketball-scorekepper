import numpy as np
from PIL import Image, ImageOps

PEN_MODEL = '21_06_14-pen_model.h5'


def load_model(model_path):  # -> tensorflow.keras.models:
    import tensorflow.keras

    # Disable scientific notation for clarity
    np.set_printoptions(suppress=True)

    # Load the model
    return tensorflow.keras.models.load_model(f'models\\{PEN_MODEL}')


def preprocess_image(image: Image) -> Image:
    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # Replace this with the path to your image
    image = Image.open('test_photo.jpg')

    # Debug
    image.show()

    # resize the image to a 224x224 with the same strategy as in TM2:
    # resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    # turn the image into a numpy array
    image_array = np.asarray(image)

    # display the resized image. Debug
    image.show()

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # Load the image into the array
    data[0] = normalized_image_array


def predict(image: Image) -> int:
    # run the inference
    prediction = model.predict(data)

    # Debug
    print(prediction)
