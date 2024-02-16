from PIL import Image
import numpy as np
from numpy.typing import NDArray
from numpy import uint8
import pickle
import glob
from typing import List
import os


def open_img(image_path: str) -> Image:
    return Image.open(image_path)


def np_open_img(image_path: str) -> NDArray[uint8]:
    """Open an image file from the specified path and convert it to a NumPy array."""
    image = open_img(image_path)
    return np.asarray(image, dtype="uint8")


def fetch_file_paths(directory: str, file_extension="png") -> List[str]:
    """Find all files in a directory and return their paths."""
    return glob.glob(f"{directory}/*.{file_extension}")


def obj_save(obj: object, file_path: str,):
    """Save an object to a file"""
    with open(file_path, "wb") as fp:
        pickle.dump(obj, fp)


def obj_load(file_path: str) -> object:
    """Load an object from a file"""
    with open(file_path, "rb") as fp:
        return pickle.load(fp)


def path_to_basename(file_path: str) -> str:
    """Returns the filename from the file_path"""
    return (os.path
            .basename(file_path)
            .lower()
            .replace(" ", "_")
            )
