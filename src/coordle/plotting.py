# src/coordle/plotting.py

import io
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np

from .functions import build_function
from .config import GameConfig


def create_attempt_image(
    expr: str,
    target: Tuple[float, float],
    x_at_min: float | None,
    y_at_min: float | None,
    config: GameConfig,
    show_target: bool = False,
) -> bytes:
    """
    Returns a PNG image as bytes:
      - curve from user expression
      - dot on curve where it's closest
      - optional target point (shown after game finished)
    Fully clean: no axes, no numbers, no labels.
    """

    # 1. Rebuild function
    f = build_function(expr)

    # 2. Generate x values
    xs = np.linspace(config.x_min, config.x_max, 600)
    ys = []

    for x in xs:
        try:
            y = f(float(x))
            if np.isfinite(y):
                ys.append(y)
            else:
                ys.append(np.nan)
        except Exception:
            ys.append(np.nan)

    xs = np.array(xs)
    ys = np.array(ys)

    # 3. Create a clean figure
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)

    # Plot curve
    ax.plot(xs, ys, linewidth=1.5)

        # Plot closest point (if valid)
    if x_at_min is not None and y_at_min is not None:
        ax.scatter([x_at_min], [y_at_min], color="blue", s=40, zorder=3)

    # Plot target (optional, controlled by show_target)
    if show_target:
        x0, y0 = target
        ax.scatter([x0], [y0], color="red", s=45, zorder=4)

    # Remove all axes
    ax.set_axis_off()

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)

    return buf.getvalue()
