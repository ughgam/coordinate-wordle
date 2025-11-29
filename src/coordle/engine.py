# src/coordle/engine.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import random

from .config import GameConfig
from .functions import build_function, FunctionParseError
from .geometry import min_distance_curve_to_point


@dataclass
class GuessResult:
    expr: str
    dist: float
    best_dist: float
    hit: bool
    error: Optional[str] = None


@dataclass
class GameState:
    config: GameConfig
    target: Tuple[float, float]
    attempts: List[GuessResult] = field(default_factory=list)
    finished: bool = False
    won: bool = False


class CoordinateWordleEngine:
    def __init__(self, config: Optional[GameConfig] = None, rng: Optional[random.Random] = None):
        self.config = config or GameConfig()
        self.rng = rng or random.Random()
        self.state = self._init_state()

    def _init_state(self) -> GameState:
        x0 = self.rng.uniform(self.config.point_min, self.config.point_max)
        y0 = self.rng.uniform(self.config.point_min, self.config.point_max)
        return GameState(config=self.config, target=(x0, y0))

    def is_finished(self) -> bool:
        return self.state.finished

    def has_won(self) -> bool:
        return self.state.won

    def remaining_attempts(self) -> int:
        return self.config.max_attempts - len(self.state.attempts)

    def submit_guess(self, expr: str) -> GuessResult:
        if self.state.finished:
            raise RuntimeError("Game already finished")

        expr = expr.strip()
        if not expr:
            gr = GuessResult(expr=expr, dist=float("inf"), best_dist=self._best_dist_or_inf(),
                            hit=False, error="Empty expression")
            self._record_attempt(gr)
            return gr

        try:
            f = build_function(expr)
        except FunctionParseError as e:
            gr = GuessResult(
                expr=expr,
                dist=float("inf"),
                best_dist=self._best_dist_or_inf(),
                hit=False,
                error=str(e),
            )
            self._record_attempt(gr)
            return gr

        dist = min_distance_curve_to_point(
            f,
            self.state.target,
            self.config.x_min,
            self.config.x_max,
            self.config.n_samples,
        )

        best_prev = self._best_dist_or_inf()
        best_dist = min(best_prev, dist)
        hit = dist < self.config.eps

        gr = GuessResult(
            expr=expr,
            dist=dist,
            best_dist=best_dist,
            hit=hit,
        )
        self._record_attempt(gr)
        return gr

    def _best_dist_or_inf(self) -> float:
        if not self.state.attempts:
            return float("inf")
        return min(a.dist for a in self.state.attempts)

    def _record_attempt(self, gr: GuessResult) -> None:
        self.state.attempts.append(gr)

        if gr.hit:
            self.state.finished = True
            self.state.won = True
            return

        if len(self.state.attempts) >= self.config.max_attempts:
            self.state.finished = True
            self.state.won = False

    def reveal_target(self) -> Tuple[float, float]:
        return self.state.target
