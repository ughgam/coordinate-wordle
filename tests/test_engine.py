# tests/test_engine.py

from coordle.engine import CoordinateWordleEngine
from coordle.config import GameConfig


def test_engine_basic():
    # deterministic target for testing
    cfg = GameConfig()
    engine = CoordinateWordleEngine(config=cfg)
    engine.state.target = (0.0, 0.0)

    # function y = 0 passes exactly through (0,0)
    result = engine.submit_guess("0")
    assert result.hit
    assert engine.is_finished()
    assert engine.has_won()
