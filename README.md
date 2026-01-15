# Coordinate Wordle
 **Play online:**  
  https://ughgam.github.io/coordinate-wordle/

-  **API backend (FastAPI docs):**  
  https://coordinate-wordle.onrender.com/docs

**Coordinate Wordle** is a web-based mathematical deduction game.  
A not so secret point is hidden somewhere in a 2D plane.  (it will be **secret** in upcoming versions but currently it gets boring so I'm working on how to make it secret and engaging)

## Concept

-| What You Guess | What It Represents |
-|----------------|--------------------|
-| f(x) = 2*x + 3 | A straight line |
-| f(x) = sin(x) + x/2 | A wavy curve |
-| f(x) = x**2 - 4*x | A parabola |

The system:
1. Samples your function across a domain range.
2. Calculates **minimum Euclidean distance** between your curve and the hidden point.
3. Returns precise feedback like:
f(x) = x**2 - 4*x
dist = 3.8721, best = 2.4415
Closest approach around x ≈ 1.33

- Expressions are parsed via Python's `ast` module and evaluated in a restricted environment:
| Allowed                         | Not Allowed              |
| ------------------------------- | ------------------------ |
| `+ - * / **`                    | File access, imports     |
| `sin, cos, tan`                 | Infinite loops           |
| `log, exp, sqrt`                | Variables other than `x` |
| Conditional: `x if x>0 else -x` | Function definitions     |

--

And displays an **image** showing:
- Your curve  
- The closest contact point  
- (Hidden point revealed only if you win / finish)

---

## TO RUN IT LOCALLY
# Clone
git clone https://github.com/ughgam/coordinate-wordle
cd coordinate-wordle

# Install
pip install -r requirements.txt

# Run backend
uvicorn coordle.api:app --reload

# Open browser
http://127.0.0.1:8000/docs

# Serve frontend (optional)
cd docs
python -m http.server 8080

```bash
git clone https://github.com/your-username/coordinate-wordle.git
cd coordinate-wordle
pip install -e .
```
---


##  Tech Stack

| Layer | Choice |
|-------|--------|
| Backend Framework | FastAPI |
| Function Parser | Python AST (safe evaluator) |
| Curve Rendering | Matplotlib |
| Frontend Hosting | GitHub Pages |
| Backend Hosting | Render (Free Web Service) |
| No Database | In-memory game sessions |
| Pure JS | Fetch API, HTML, Canvas `<img>` |

---

##  API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/new-game` | Start a new game – returns `game_id` |
| POST | `/guess` | Send a function guess – returns distance, feedback, image URL |
| GET | `/image/{game_id}/{attempt_index}` | Returns PNG image of that attempt |
| GET | `/docs` | Auto-generated Swagger API UI |

**Guess Response Example:**

```json
{
  "dist": 1.7432,
  "best_dist": 1.4231,
  "hit": false,
  "finished": false,
  "attempts_used": 3,
  "attempts_left": 5,
  "image_url": "/image/77ac.../2"
}

