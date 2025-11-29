# src/coordle/cli.py

from .engine import CoordinateWordleEngine
from .config import GameConfig


def main() -> None:
    config = GameConfig()
    engine = CoordinateWordleEngine(config=config)

    print("COORDINATE WORDLE")
    print("-----------------")
    print("A secret point (x0, y0) is hidden.")
    print(f"You have {config.max_attempts} attempts to write a function y = f(x)")
    print("such that its graph passes near that point.")
    print(f"If the minimum distance between your curve and the point is < {config.eps}, you win.")
    print()
    print("Enter functions in Python-like syntax, e.g.:")
    print("  2*x + 3")
    print("  x**2 - 4*x + 1")
    print("  sin(x) + x/2")
    print()

    while not engine.is_finished():
        remaining = engine.remaining_attempts()
        print(f"Remaining attempts: {remaining}")
        expr = input(f"Attempt {len(engine.state.attempts) + 1} - enter f(x): ")

        result = engine.submit_guess(expr)

        if result.error:
            print(f"Error: {result.error}")
            print()
            continue

        print(f"Minimum distance for this function: {result.dist:.6f}")
        print(f"Best distance so far: {result.best_dist:.6f}")
        if result.x_at_min is not None and result.x_at_min == result.x_at_min:  # not NaN
            print(f"Closest approach around x ≈ {result.x_at_min:.3f}")


        if result.hit:
            print()
            x0, y0 = engine.reveal_target()
            print("You hit the target (within tolerance).")
            print(f"Hidden point was approximately: ({x0:.3f}, {y0:.3f})")
            break

        print()

    if not engine.has_won():
        x0, y0 = engine.reveal_target()
        print("Out of attempts.")
        print(f"The hidden point was: ({x0:.3f}, {y0:.3f})")


if __name__ == "__main__":
    main()
