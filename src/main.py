# import tkinter as tk
from tkinter import filedialog
import ffmpeg
import time
import os
import shutil
import glob
from mscore import parallel_movement_scores
from typing import List


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
