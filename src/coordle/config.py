# src/coordle/config.py

from dataclasses import dataclass


@dataclass
class GameConfig:
    x_min: float = -20.0
    x_max: float = 20.0
    n_samples: int = 2000
    max_attempts: int = 8
    eps: float = 0.2  # win threshold
    point_min: float = -10.0
    point_max: float = 10.0
