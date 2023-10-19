from PIL import Image
import numpy as np
from numpy.typing import NDArray
from numpy import int16


def open_img(image_path: str) -> NDArray[int16]:
    """Open an image file from the specified path and convert it to a NumPy array."""
    image = Image.open(image_path)
    return np.asarray(image, dtype="int16")
