from PIL import Image, ImageFilter
import numpy as np
from multiprocessing import Pool
import time
from utils import open_img
from typing import List, Tuple, Literal
from numpy import uint8
from numpy.typing import NDArray
from cache import Cache
from parallel import split_paths_to_chunks, merge_chunks, exec_parallel


def calc_edges(
        img: Image,
        mode: Literal["laplacian"] = "laplacian") -> NDArray[uint8]:
    """Calculate a movement heatmap by subtracting two images and averaging the color channels."""

    img = img.convert("L")

    # Calculating Edges using the laplacian Kernel
    kernel = None
    if mode == "laplacian":
        kernel = (
            -1, -1, -1,
            -1, 8, -1,
            -1, -1, -1
        )

    img_edges = img.filter(
        ImageFilter.Kernel(
            (3, 3),
            kernel,
            1, 0
        )
    )

    return np.asarray(img_edges, dtype="uint8")


def calc_edge_score(img1: NDArray[int], img2: NDArray[int]) -> float:
    """Calculate the movement score between two images based on their movement heatmaps."""
    img1_edges = calc_edges(img1)
    img2_edges = calc_edges(img2)
    edge_diff = np.square(img1_edges - img2_edges)

    return np.mean(edge_diff)


def calc_edge_scores(frame_paths: List[str]) -> List[Tuple[str, float]]:
    """Calculate movement scores for a list of frame paths and return them as a list of (path, score) tuples."""
    edge_scores = [(frame_paths[0], 0.0)]
    previous_frame_img = open_img(frame_paths[0])

    for frame_path in frame_paths[1:]:
        frame_img = open_img(frame_path)
        edge_score = calc_edge_score(previous_frame_img, frame_img)
        edge_scores.append((frame_path, edge_score))
        previous_frame_img = frame_img

    return edge_scores


def calc_parallel_edge_scores(frame_paths: [List[str]], workers=12) -> List[Tuple[str, float]]:
    """Calculate movement scores for a list of frame paths in parallel using multiple workers."""

    start_time = time.time()
    print(f"Calculating edge scores of frames ({workers} workers)...")

    frame_paths_chunks = split_paths_to_chunks(frame_paths, workers)
    edge_scores_chunks = exec_parallel(calc_edge_scores, frame_paths_chunks, workers)
    edge_scores = merge_chunks(edge_scores_chunks)

    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)
    print(f"Done! Took {elapsed_time} seconds.")

    return edge_scores


def retrieve_edge_scores(frame_paths: [List[str]], file_cache: Cache) -> List[Tuple[str, float]]:
    edge_scores = file_cache.load_object("edge_scores")

    if edge_scores is not None:
        uin = input(f"The cache for edge scores is not empty." +
                    "\nWould you like to reuse it [y/n]?" +
                    "\n>>> ")

        if uin == "y":
            return edge_scores  # type: ignore[return-value]
        else:
            file_cache.delete_object("edge_scores")

    edge_scores = calc_parallel_edge_scores(frame_paths)
    file_cache.store_object(edge_scores, "edge_scores")

    return edge_scores

