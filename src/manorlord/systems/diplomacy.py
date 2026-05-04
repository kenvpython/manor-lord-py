from __future__ import annotations

from typing import TYPE_CHECKING

from manorlord.systems.base import System

if TYPE_CHECKING:
    from manorlord.core.game_state import GameState


class DiplomacySystem(System):
    name = "diplomacy"

    def advance_turn(self, state: "GameState") -> None:
        state.add_log("Diplomacy ticked.")
