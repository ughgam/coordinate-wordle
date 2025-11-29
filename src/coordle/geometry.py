# src/coordle/geometry.py

import math
from typing import Callable, Tuple


def min_distance_curve_to_point(
    f: Callable[[float], float],
    point: Tuple[float, float],
    x_min: float,
    x_max: float,
    n_samples: int,
) -> Tuple[float, float, float]:
    """
    Approximate the minimum Euclidean distance between the curve y=f(x)
    and a single point (x0, y0) over x in [x_min, x_max].

    Returns:
        (min_dist, x_at_min, y_at_min)
    """
    x0, y0 = point
    if n_samples < 2:
        raise ValueError("n_samples must be at least 2")

    step = (x_max - x_min) / (n_samples - 1)
    min_dist = float("inf")
    x_at_min = float("nan")
    y_at_min = float("nan")

    for i in range(n_samples):
        x = x_min + i * step
        try:
            y = f(x)
        except Exception:
            # skip x values where function fails
            continue

        if isinstance(y, complex):
            continue
        if not math.isfinite(y):
            continue

        dx = x - x0
        dy = y - y0
        dist = math.hypot(dx, dy)

        if dist < min_dist:
            min_dist = dist
            x_at_min = x
            y_at_min = y

    return min_dist, x_at_min, y_at_min
