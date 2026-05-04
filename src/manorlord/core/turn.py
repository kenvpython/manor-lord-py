from manorlord.core.game_state import GameState
from manorlord.systems.base import System


class TurnManager:
    def __init__(self, systems: list[System]) -> None:
        self.systems = systems

    def advance_turn(self, state: GameState) -> None:
        for system in self.systems:
            system.advance_turn(state)
        state.turn += 1
        state.event_bus.publish("turn.advanced", {"turn": state.turn})
