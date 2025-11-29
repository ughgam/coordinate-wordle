<!-- .github/copilot-instructions.md - guidance for AI coding agents -->

# Coordinate Wordle — AI Agent Instructions

Brief, actionable notes to help an AI coding assistant become productive in this repository.

- **Project purpose:**: function-based guessing game where players submit `y = f(x)` expressions and the engine reports the minimum Euclidean distance between the curve and a hidden point.
- **Layout:**: source under `src/coordle/` with key modules:
  - `config.py` — game defaults (`x_min`, `x_max`, `n_samples`, `max_attempts`, `eps`).
  - `fuctions.py` — expression parser / safe evaluator (intended to be `functions.py`).
  - `geometry.py` — `min_distance_curve_to_point` sampling routine.
  - `engine.py` — game engine and `CoordinateWordleEngine` API used by the CLI and tests.
  - `cli.py` — simple interactive CLI that uses the engine.

- **Important quirk (critical):**: the module file is named `src/coordle/fuctions.py` but the code and tests import `coordle.functions`. This will cause import errors in a normal Python environment. Before running tests or importing `coordle.functions` one of these must be done:
  - Rename `fuctions.py` → `functions.py` (recommended), or
  - Add a compatibility import shim (e.g., create `functions.py` that imports `from .fuctions import *`).

- **Expression parsing & evaluation**: implemented in `SafeEvaluator` in `fuctions.py`.
  - Accepts literals, `x`, binary ops `+ - * / **`, unary `+ -`, allowed calls (`sin, cos, tan, exp, log, sqrt, abs, floor, ceil`), and a limited `if-else` expression.
  - Use `build_function(expr)` to get a callable `f(x)` or raise `FunctionParseError`.

- **Distance computation:** `min_distance_curve_to_point(f, (x0,y0), x_min, x_max, n_samples)` samples `n_samples` evenly in `[x_min,x_max]`, skips non-finite/exceptional outputs, and returns the minimum Euclidean distance.

- **Common workflows / commands:**
  - Install locally: `pip install -e .` (project uses `src/` layout; pyproject suggests Python >= 3.10).
  - Run tests: `pytest -q` or `python -m pytest` from repository root.
  - Run CLI: `python -m coordle.cli` or run `src/coordle/cli.py` via interpreter.

- **Tests to note:** `tests/test_functions.py` imports `coordle.functions` and will fail until the filename mismatch above is resolved. `tests/test_engine.py` sets a deterministic target and expects `engine.submit_guess("0")` to hit `(0,0)`.

- **Patterns & expectations for changes:**
  - Keep parsing logic in `fuctions.py` (or `functions.py`) and extend `SafeEvaluator` carefully — tests rely on exact exception types (`FunctionParseError`).
  - Numerical code uses sampling (not analytic geometry). When improving accuracy, update `n_samples` in `GameConfig` and tests accordingly.

- **Where to look for behavior changes:**
  - `config.py` for default parameter tuning.
  - `geometry.py` for distance/sampling strategy.
  - `fuctions.py` for allowed expression syntax / security.

- **If you change imports or filenames:** update `tests/` imports or add a compatibility shim so CI and local runs remain green.

If anything in these notes is unclear or you'd like the file to also contain suggested unit tests or an automated rename commit, tell me and I will iterate.
