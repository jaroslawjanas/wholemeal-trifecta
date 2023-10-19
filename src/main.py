# import tkinter as tk
from tkinter import filedialog
import ffmpeg
import time
import os
import shutil
import glob
import numpy as np
from numpy import uint8, int16
from numpy.typing import NDArray
from typing import List, Tuple
from PIL import Image
from multiprocessing import Pool


def ffmpeg_extract_frames(file_path: str, output_dir: str):
    """Extract frames from a video file using FFmpeg and save them to the specified directory"""
    print("Extracting frames to cache...")
    start_time = time.time()

    (
        ffmpeg.input(file_path)
        .output(f"{output_dir}/frame_%07d.png")
        .overwrite_output()
        .run()
    )

    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    print(f"Done! Took {elapsed_time} seconds.")


def extract_frames(file_path: str, cache_location: str) -> str:
    """Check if the cache directory is empty, and proceed with extraction.
    If the cache directory is not empty, the user is given the option to reuse it.
    The cache location is returned after extraction."""
    file_name = os.path.basename(file_path).split('.')[0]

    # Define a cache directory
    cache_dir = f"{cache_location}/{file_name}"

    # Check if the cache directory already exists
    out_dir_exists = os.path.isdir(cache_dir)

    # Create a cache directory if it's missing
    if not out_dir_exists:
        os.makedirs(cache_dir, exist_ok=True)

    # If the cache directory exists, check if it's empty
    else:
        is_out_dir_empty = not os.listdir(cache_dir)

        # If the cache directory is not empty, ask if the user wants to reuse it
        if not is_out_dir_empty:
            uin = input(f"The cache for \"{file_name}\" is not empty." +
                        "\nWould you like to reuse it [y/n]?" +
                        "\n>>> ")
            # If not, empty the directory and extract new frames
            if uin == "n":
                shutil.rmtree(cache_dir)
                os.mkdir(cache_dir)
            else:
                return cache_dir

    ffmpeg_extract_frames(file_path, cache_dir)
    return cache_dir


def fetch_frame_paths(frames_dir: str, file_extension="png") -> List[str]:
    """Find all frame files in a directory and return their paths."""
    return glob.glob(f"{frames_dir}/*.{file_extension}")


def open_img(image_path: str) -> NDArray[int16]:
    """Open an image file from the specified path and convert it to a NumPy array."""
    image = Image.open(image_path)
    return np.asarray(image, dtype="int16")


def movement_heatmap(img1: NDArray[int], img2: NDArray[int]) -> NDArray[uint8]:
    """Calculate a movement heatmap by subtracting two images and averaging the color channels."""
    movement_heatmap_rgb = np.abs(img1 - img2)
    # Average channels (convert to grayscale)
    return np.mean(movement_heatmap_rgb, axis=-1, dtype="uint8")


def movement_score(img1: NDArray[int], img2: NDArray[int]) -> float:
    """Calculate the movement score between two images based on their movement heatmaps."""
    mov_heatmap = movement_heatmap(img1, img2)
    return np.mean(mov_heatmap)


def movement_scores(frame_paths: List[str]) -> List[Tuple[str, float]]:
    """Calculate movement scores for a list of frame paths and return them as a list of (path, score) tuples."""
    mov_scores = [(frame_paths[0], 0.0)]
    previous_frame_img = open_img(frame_paths[0])

    for frame_path in frame_paths[1:]:
        frame_img = open_img(frame_path)
        mov_score = movement_score(previous_frame_img, frame_img)
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


def parallel_movement_scores(frame_paths: [List[str]], workers=12, chunks=12) -> List[Tuple[str, float]]:
    """Calculate movement scores for a list of frame paths in parallel using multiple workers."""
    pool = Pool(processes=workers)
    start_time = time.time()
    print(f"Calculating movement scores of frames ({workers} workers)...")

    frame_paths_chunks = split_paths_to_chunks(frame_paths, chunks)
    mov_score_chunks = pool.map(movement_scores, frame_paths_chunks)

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


def main():
    cwd = os.getcwd()
    cache = ".cache"
    cache_location = f"{cwd}/{cache}"

    # Ask for an input file
    file_path = filedialog.askopenfilename()
    frames_dir = extract_frames(file_path, cache_location)
    frame_paths = fetch_frame_paths(frames_dir)
    parallel_movement_scores(frame_paths, workers=12, chunks=12)


if __name__ == '__main__':
    main()
