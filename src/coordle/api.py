# src/coordle/api.py

from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import uuid

from .config import GameConfig
from .engine import CoordinateWordleEngine

app = FastAPI()

origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory store: game_id -> engine instance
GAMES: Dict[str, CoordinateWordleEngine] = {}


# ---------- Pydantic models (request/response schemas) ----------
from fastapi.responses import Response
from .plotting import create_attempt_image

class NewGameResponse(BaseModel):
    game_id: str
    x_min: float
    x_max: float
    max_attempts: int
    eps: float


class GuessRequest(BaseModel):
    game_id: str
    expr: str


class GuessResponse(BaseModel):
    dist: float
    best_dist: float
    hit: bool
    finished: bool
    attempts_used: int
    image_url: str | None = None
    attempts_left: int
    error: str | None = None
    # later we'll add: image_url: str | None


# ---------- Endpoints ----------

@app.post("/new-game", response_model=NewGameResponse)
def new_game() -> NewGameResponse:
    """
    Create a new game instance and return its ID + basic config.
    """
    config = GameConfig()
    engine = CoordinateWordleEngine(config=config)

    game_id = str(uuid.uuid4())
    GAMES[game_id] = engine

    return NewGameResponse(
        game_id=game_id,
        x_min=config.x_min,
        x_max=config.x_max,
        max_attempts=config.max_attempts,
        eps=config.eps,
    )


@app.post("/guess", response_model=GuessResponse)
def guess(payload: GuessRequest) -> GuessResponse:
    """
    Submit a function expression for a given game_id.
    Returns distance and game state.
    """
    game = GAMES.get(payload.game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    result = game.submit_guess(payload.expr)

    attempt_index = len(game.state.attempts) - 1
    image_url = f"/image/{payload.game_id}/{attempt_index}" if result.error is None else None

    return GuessResponse(
        dist=result.dist,
        best_dist=result.best_dist,
        hit=result.hit,
        finished=game.is_finished(),
        attempts_used=len(game.state.attempts),
        attempts_left=game.remaining_attempts(),
        error=result.error,
        image_url=image_url,
    )

@app.get("/image/{game_id}/{attempt_index}")
def attempt_image(game_id: str, attempt_index: int):
    game = GAMES.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    attempts = game.state.attempts
    if attempt_index < 0 or attempt_index >= len(attempts):
        raise HTTPException(status_code=404, detail="Attempt not found")

    attempt = attempts[attempt_index]

    if attempt.error:
        raise HTTPException(status_code=400, detail="No image for an invalid expression")

    img_bytes = create_attempt_image(
        expr=attempt.expr,
        target=game.state.target,
        x_at_min=attempt.x_at_min,
        y_at_min=attempt.y_at_min,
        config=game.config,
         show_target=True,  # always show the hidden point
    )

    return Response(content=img_bytes, media_type="image/png")
