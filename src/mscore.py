import numpy as np
from multiprocessing import Pool
import time
from utils import np_open_img
from typing import List, Tuple, Literal
from numpy import uint8
from numpy.typing import NDArray
from cache import Cache
from parallel import split_paths_to_chunks, merge_chunks, exec_parallel


def calc_movement_heatmap(
        img1: NDArray[int],
        img2: NDArray[int],
        mode: Literal["linear", "exponential"] = "exponential") -> NDArray[uint8]:
    """Calculate a movement heatmap by subtracting two images and averaging the color channels."""

    if mode == "exponential":
        movement_heatmap_rgb = np.square(img1 - img2)
    else:
        movement_heatmap_rgb = np.abs(img1 - img2)

    # Average channels (convert to grayscale)
    return np.mean(movement_heatmap_rgb, axis=-1, dtype="uint8")


def calc_movement_score(img1: NDArray[int], img2: NDArray[int]) -> float:
    """Calculate the movement score between two images based on their movement heatmaps."""
    movement_heatmap = calc_movement_heatmap(img1, img2)
    return np.mean(movement_heatmap)


def calc_movement_scores(frame_paths: List[str]) -> List[Tuple[str, float]]:
    """Calculate movement scores for a list of frame paths and return them as a list of (path, score) tuples."""
    movement_scores = [(frame_paths[0], 0.0)]
    previous_frame_img = np_open_img(frame_paths[0])

    for frame_path in frame_paths[1:]:
        frame_img = np_open_img(frame_path)
        movement_score = calc_movement_score(previous_frame_img, frame_img)
        movement_scores.append((frame_path, movement_score))
        previous_frame_img = frame_img

    return movement_scores


def calc_parallel_movement_scores(frame_paths: [List[str]], workers=12) -> List[Tuple[str, float]]:
    """Calculate movement scores for a list of frame paths in parallel using multiple workers."""

    start_time = time.time()
    print(f"Calculating movement scores of frames ({workers} workers)...")

    frame_paths_chunks = split_paths_to_chunks(frame_paths, workers)
    movement_scores_chunks = exec_parallel(calc_movement_scores, frame_paths_chunks, workers=12)
    movement_scores = merge_chunks(movement_scores_chunks)

    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    print(f"Done! Took {elapsed_time} seconds.")

    return movement_scores


def retrieve_movement_scores(frame_paths: [List[str]], file_cache: Cache) -> List[Tuple[str, float]]:
    movement_scores = file_cache.load_object("movement_scores")

    if movement_scores is not None:
        uin = input(f"The cache for movement scores is not empty." +
                    "\nWould you like to reuse it [y/n]?" +
                    "\n>>> ")

        if uin == "y":
            return frame_paths
        else:
            file_cache.delete_object("movement_scores")

    movement_scores = calc_parallel_movement_scores(frame_paths)
    file_cache.store_object(movement_scores, "movement_scores")

    return movement_scores

