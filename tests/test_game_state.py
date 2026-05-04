import pickle

from manorlord.core.game_state import GameState
from manorlord.core.new_game import create_world, new_game, set_player


def test_default_state_is_empty():
    state = GameState()
    assert state.turn == 1
    assert state.player_character_id is None
    assert state.characters == {}
    assert state.realms == {}


def test_create_world_has_eight_realms_with_unique_owners():
    state = create_world(seed=42)
    assert len(state.realms) == 8
    assert len(state.provinces) == 8
    owner_ids = {realm.owner_id for realm in state.realms.values()}
    assert len(owner_ids) == 8
    assert state.player_character_id is None


def test_each_province_has_polygon_and_center():
    state = create_world(seed=1)
    for province in state.provinces.values():
        assert len(province.polygon) >= 3
        assert all(isinstance(point, tuple) and len(point) == 2 for point in province.polygon)
        assert isinstance(province.center, tuple)


def test_each_realm_has_distinct_color():
    state = create_world(seed=7)
    colors = [realm.color for realm in state.realms.values()]
    assert len(set(colors)) == len(colors)


def test_set_player_attaches_lord_of_chosen_realm():
    state = create_world(seed=10)
    set_player(state, realm_id=3)

    realm = state.realms[3]
    assert state.player_character_id == realm.owner_id
    assert state.player.realm_id == 3
    assert state.player_realm is realm


def test_new_game_creates_player_and_realm():
    state = new_game(seed=42)
    assert state.player is not None
    assert state.player_realm is not None
    assert state.player.realm_id == state.player_realm.id
    assert len(state.provinces) == 8


def test_state_pickle_roundtrip_drops_event_bus():
    state = new_game(seed=1)
    state.event_bus.subscribe("turn.advanced", lambda payload: None)

    blob = pickle.dumps(state)
    restored = pickle.loads(blob)

    assert restored.turn == state.turn
    assert restored.player.full_name == state.player.full_name
    assert restored.event_bus is not state.event_bus
    assert len(restored.realms) == 8
