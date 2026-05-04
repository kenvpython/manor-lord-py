import pickle

from manorlord.core.game_state import GameState
from manorlord.core.new_game import new_game


def test_default_state_is_empty():
    state = GameState()
    assert state.turn == 1
    assert state.player_character_id is None
    assert state.characters == {}
    assert state.realms == {}


def test_new_game_creates_player_and_realm():
    state = new_game(seed=42)
    assert state.player is not None
    assert state.player_realm is not None
    assert state.player.realm_id == state.player_realm.id
    assert len(state.provinces) >= 1


def test_state_pickle_roundtrip_drops_event_bus():
    state = new_game(seed=1)
    state.event_bus.subscribe("turn.advanced", lambda payload: None)

    blob = pickle.dumps(state)
    restored = pickle.loads(blob)

    assert restored.turn == state.turn
    assert restored.player.full_name == state.player.full_name
    assert restored.event_bus is not state.event_bus
