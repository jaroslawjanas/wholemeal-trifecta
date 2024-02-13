# import tkinter as tk
from tkinter import filedialog
import ffmpeg
import time
import os
from mscore import retrieve_movement_scores
from typing import List
from cache import Cache


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


def extract_frames(file_path: str, file_cache: Cache) -> List[str]:
    """Check if the cache directory is empty, and proceed with extraction.
    If the cache directory is not empty, the user is given the option to reuse it.
    The cache location is returned after extraction."""

    frame_paths = file_cache.get_cached_frames()

    if len(frame_paths) > 0:  # if frames cached

        file_name = os.path.basename(file_path)
        uin = input(f"The cache for \"{file_name}\" is not empty." +
                    "\nWould you like to reuse it [y/n]?" +
                    "\n>>> ")

        if uin == "y":
            return frame_paths

    # If caches frames are not being used, re-create the entire
    # file cache and store extracted frames directly in it
    file_cache.create_new()
    ffmpeg_extract_frames(file_path, f"{file_cache.get_cache_directory()}/frames")
    frame_paths = file_cache.get_cached_frames()

    if len(frame_paths) == 0:
        print("Frame extraction failed!")
        return []

    return frame_paths


def main():
    cwd: str = os.getcwd()
    cache = ".cache"
    cache_location = f"{cwd}/{cache}"

    # Ask for an input file
    file_path: str = filedialog.askopenfilename()

    # Create file's cache
    file_cache = Cache(file_path, cache_location)

    frame_paths = extract_frames(file_path, file_cache)
    movement_scores = retrieve_movement_scores(frame_paths, file_cache)


if __name__ == '__main__':
    main()
