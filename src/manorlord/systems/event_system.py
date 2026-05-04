from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from manorlord.systems.base import System

if TYPE_CHECKING:
    from manorlord.core.game_state import GameState


_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class EventSystem(System):
    name = "events"

    def __init__(self, events_path: Path | None = None) -> None:
        path = events_path or (_DATA_DIR / "events.json")
        self.events: list[dict[str, Any]] = self._load(path)

    @staticmethod
    def _load(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def advance_turn(self, state: "GameState") -> None:
        state.add_log(f"Events checked ({len(self.events)} loaded).")
