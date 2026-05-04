from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manorlord.core.game_state import GameState


class System:
    name: str = "system"

    def advance_turn(self, state: "GameState") -> None:
        raise NotImplementedError
