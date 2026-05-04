from __future__ import annotations

from typing import TYPE_CHECKING

from manorlord.systems.base import System

if TYPE_CHECKING:
    from manorlord.core.game_state import GameState


class LifecycleSystem(System):
    name = "lifecycle"

    def advance_turn(self, state: "GameState") -> None:
        for character in state.characters.values():
            if character.is_alive:
                character.age += 1
        state.add_log("Lifecycle ticked.")
