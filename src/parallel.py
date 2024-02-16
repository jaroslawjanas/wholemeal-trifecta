from typing import List, Tuple, Callable, Iterable, Optional
import time
from multiprocessing import Pool


def split_paths_to_chunks(frame_paths: List[str], no_chunks: int) -> List[List[str]]:
    """Split a list of frame paths into N chunks. The first chunk may be larger if the division isn't even.
    First frame of each chunk overlap with the last frame of previous chunk, the only exception being the first chunk,
    since it has no prior chunks."""
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


def merge_chunks(unmerged_chunks: List, expected_count: Optional[int] = None) -> List:
    merged = []

    for chunk in unmerged_chunks:
        if not merged:
            merged.extend(chunk)
        else:
            merged.extend(chunk[1:])

    if expected_count is not None:
        if len(merged) != expected_count:
            raise ValueError("The number of elements after merging does not match the expected value.")

    return merged


def exec_parallel(func: Callable, arg: Iterable, workers=12) -> List[Tuple[str, float]]:
    """Calculate movement scores for a list of frame paths in parallel using multiple workers."""
    pool = Pool(processes=workers)
    # start_time = time.time()
    # print(f"Calculating movement scores of frames ({workers} workers)...")

    output = pool.map(func, arg)

    # end_time = time.time()
    # elapsed_time = round(end_time - start_time, 2)
    # print(f"Done! Took {elapsed_time} seconds.")

    return output
