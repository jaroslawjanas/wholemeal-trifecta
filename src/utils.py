from PIL import Image
import numpy as np
from numpy.typing import NDArray
from numpy import int16
import pickle


def open_img(image_path: str) -> NDArray[int16]:
    """Open an image file from the specified path and convert it to a NumPy array."""
    image = Image.open(image_path)
    return np.asarray(image, dtype="int16")


def obj_save(file_path: str, obj: object):
    """Save an object to a file"""
    with open(file_path, "wb") as fp:
        pickle.dump(obj, fp)


def obj_load(file_path: str) -> object:
    """Load an object from a file"""
    with open(file_path, "rb") as fp:
        return pickle.load(fp)
