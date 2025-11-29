# Coordinate Wordle

Coordinate Wordle is a function-based guessing game.

A secret point `(x0, y0)` is hidden in the plane.  
On each turn, you type a function `f(x)` (in Python syntax).  
The game evaluates your function over a domain and tells you the **minimum Euclidean distance** between your curve and the hidden point.

If your curve passes within a small threshold, you win.

This is essentially "Wordle meets analytic geometry":  
you don't guess letters, you sculpt functions.

---

## Features (v1)

- Random hidden point in a configurable box.
- Players submit functions of `x` like:
  - `2*x + 3`
  - `x**2 - 4*x + 1`
  - `sin(x) + x/2`
- Expressions are parsed via Python's `ast` module and evaluated in a restricted environment:
  - allowed operators: `+ - * / **`
  - allowed functions: `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `abs`, `floor`, `ceil`
- Distance is approximated by sampling `f(x)` over a domain and computing the minimum Euclidean distance to the hidden point.
- Configurable:
  - domain `[X_MIN, X_MAX]`
  - number of samples
  - number of attempts
  - win threshold `EPS`

---

## Installation

```bash
git clone https://github.com/your-username/coordinate-wordle.git
cd coordinate-wordle
pip install -e .
