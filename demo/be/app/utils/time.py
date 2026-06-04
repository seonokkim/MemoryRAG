import time


def ms_since(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)
