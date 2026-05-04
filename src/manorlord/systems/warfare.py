from __future__ import annotations

from typing import TYPE_CHECKING

from manorlord.systems.base import System

if TYPE_CHECKING:
    from manorlord.core.game_state import GameState


class WarfareSystem(System):
    name = "warfare"

    def advance_turn(self, state: "GameState") -> None:
        for realm in state.realms.values():
            population = sum(
                state.provinces[pid].population
                for pid in realm.province_ids
                if pid in state.provinces
            )
            realm.troops = population // 100
        state.add_log("Warfare ticked.")
