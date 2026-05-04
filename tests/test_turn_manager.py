from manorlord.core.game_state import GameState
from manorlord.core.new_game import new_game
from manorlord.core.turn import TurnManager
from manorlord.systems.base import System


class _Recorder(System):
    name = "recorder"

    def __init__(self) -> None:
        self.calls = 0

    def advance_turn(self, state: GameState) -> None:
        self.calls += 1


def test_advance_turn_increments_turn_counter_and_runs_each_system():
    a, b, c = _Recorder(), _Recorder(), _Recorder()
    manager = TurnManager([a, b, c])
    state = new_game(seed=7)

    starting_turn = state.turn
    manager.advance_turn(state)

    assert state.turn == starting_turn + 1
    assert a.calls == 1
    assert b.calls == 1
    assert c.calls == 1


def test_advance_turn_publishes_event():
    state = new_game(seed=11)
    seen: list[int] = []
    state.event_bus.subscribe("turn.advanced", lambda payload: seen.append(payload["turn"]))

    TurnManager([]).advance_turn(state)

    assert seen == [state.turn]
