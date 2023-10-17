# import tkinter as tk
from tkinter import filedialog
import ffmpeg
import time
import os
import shutil
import glob


def ffmpeg_extract_frames(file_path, destination):
    start_time = time.time()

    (
        ffmpeg.input(file_path)
        .output(f"{destination}/frame_%04d.png")
        .overwrite_output()
        .run()
    )

    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)


def extract_frames(file_path, cache_location):
    file_name = os.path.basename(file_path).split('.')[0]

    # Define a cache directory
    cache_dir = f"{cache_location}/{file_name}"

    # Check if cache directory already exists
    out_dir_exists = os.path.isdir(cache_dir)

    # Create a cache directory if missing
    if not out_dir_exists:
        os.makedirs(cache_dir, exist_ok=True)

    # if it exists check if empty
    else:
        # Check if the cache directory is empty
        is_out_dir_empty = not os.listdir(cache_dir)

        # If the cache directory is not empty ask if to reuse
        if not is_out_dir_empty:
            uin = input(f"The cache for \"{file_name}\" is not empty." +
                        "\nWould you like to reuse it [y/n]?" +
                        "\n>>> ")
            # If not then empty the directory and extract new frames
            if uin == "n":
                shutil.rmtree(cache_dir)
                os.mkdir(cache_dir)
            else:
                return cache_dir

    ffmpeg_extract_frames(file_path, cache_dir)
    return cache_dir


def fetch_frames(frames_dir, file_extension="png"):
    return glob.glob(f"{frames_dir}/*.{file_extension}")



def main():
    cwd = os.getcwd()
    cache = ".cache"
    cache_location = f"{cwd}/{cache}"

    # Ask for an input file
    file_path = filedialog.askopenfilename()
    frames_dir = extract_frames(file_path, cache_location)
    frame_paths = fetch_frames(frames_dir)

if __name__ == '__main__':
    main()
