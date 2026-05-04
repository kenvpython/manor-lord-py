from __future__ import annotations

from typing import TYPE_CHECKING

from manorlord.systems.base import System

if TYPE_CHECKING:
    from manorlord.core.game_state import GameState


class EconomySystem(System):
    name = "economy"

    def advance_turn(self, state: "GameState") -> None:
        for realm in state.realms.values():
            realm.income = sum(
                state.provinces[pid].base_tax
                for pid in realm.province_ids
                if pid in state.provinces
            )
            realm.treasury += realm.income
        state.add_log("Economy ticked.")
