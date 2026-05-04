import pickle
from pathlib import Path

from manorlord.core.game_state import GameState


def save(state: GameState, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        pickle.dump(state, fh)


def load(path: str | Path) -> GameState:
    with Path(path).open("rb") as fh:
        return pickle.load(fh)
