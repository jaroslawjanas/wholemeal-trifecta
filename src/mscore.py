import numpy as np
from multiprocessing import Pool
import time
from utils import open_img
from typing import List, Tuple, Literal
from numpy import uint8
from numpy.typing import NDArray


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
    mov_heatmap = calc_movement_heatmap(img1, img2)
    return np.mean(mov_heatmap)


def calc_movement_scores(frame_paths: List[str]) -> List[Tuple[str, float]]:
    """Calculate movement scores for a list of frame paths and return them as a list of (path, score) tuples."""
    mov_scores = [(frame_paths[0], 0.0)]
    previous_frame_img = open_img(frame_paths[0])

    for frame_path in frame_paths[1:]:
        frame_img = open_img(frame_path)
        mov_score = calc_movement_score(previous_frame_img, frame_img)
        mov_scores.append((frame_path, mov_score))
        previous_frame_img = frame_img

    return mov_scores


def split_paths_to_chunks(frame_paths: List[str], no_chunks: int) -> List[List[str]]:
    """Split a list of frame paths into N chunks. The first chunk may be larger if the division isn't even."""
    no_frames = len(frame_paths)
    remainder_offset = no_frames % no_chunks
    interval = int((no_frames - remainder_offset) / no_chunks)
    first_interval = interval + remainder_offset

    paths = []
    last_idx = 0
    for chunk_itr in range(no_chunks):
        if last_idx == 0:
            idx_start = 0
            idx_end = first_interval
        else:
            idx_start = last_idx - 1
            idx_end = last_idx + interval

        chunk = frame_paths[idx_start:idx_end]
        paths.append(chunk)
        last_idx = idx_end

    return paths


def calc_parallel_movement_scores(frame_paths: [List[str]], workers=12, chunks=12) -> List[Tuple[str, float]]:
    """Calculate movement scores for a list of frame paths in parallel using multiple workers."""
    pool = Pool(processes=workers)
    start_time = time.time()
    print(f"Calculating movement scores of frames ({workers} workers)...")

    frame_paths_chunks = split_paths_to_chunks(frame_paths, chunks)
    mov_score_chunks = pool.map(calc_movement_scores, frame_paths_chunks)

    merged = []
    for mov_score_chunk in mov_score_chunks:
        if not merged:
            merged.extend(mov_score_chunk)
        else:
            merged.extend(mov_score_chunk[1:])

    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    print(f"Done! Took {elapsed_time} seconds.")

    if len(merged) != len(frame_paths):
        raise ValueError("The number of movement score values does not match the number of frames.")

    return merged
