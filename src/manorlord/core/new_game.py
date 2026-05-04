from __future__ import annotations

import json
import random
from pathlib import Path

from manorlord.config import REALM_COLORS
from manorlord.core.game_state import GameState
from manorlord.entities import Character, Province, Realm, Title


_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(name: str) -> object:
    with (_DATA_DIR / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_names() -> dict[str, list[str]]:
    return _load_json("names.json")  # type: ignore[return-value]


def _load_realms_data() -> list[dict]:
    return _load_json("realms.json")  # type: ignore[return-value]


def _load_provinces_data() -> list[dict]:
    return _load_json("provinces.json")  # type: ignore[return-value]


def create_world(seed: int | None = None) -> GameState:
    rng = random.Random(seed)
    names = _load_names()
    realms_data = _load_realms_data()
    provinces_data = _load_provinces_data()

    state = GameState()

    for prov in provinces_data:
        province = Province(
            id=prov["id"],
            name=prov["name"],
            terrain=prov["terrain"],
            population=prov["population"],
            base_tax=prov["base_tax"],
            polygon=[tuple(point) for point in prov["polygon"]],
            center=tuple(prov["center"]),
        )
        state.provinces[province.id] = province

    next_char_id = 1
    for realm_def in realms_data:
        lord_def = realm_def["lord"]
        is_male = lord_def["first_name_pool"] == "male"
        first_pool = names["male"] if is_male else names["female"]

        lord = Character(
            id=next_char_id,
            first_name=rng.choice(first_pool),
            last_name=lord_def["last_name"],
            age=rng.randint(lord_def["age_min"], lord_def["age_max"]),
            is_male=is_male,
            title=Title[lord_def["title"]],
            realm_id=realm_def["id"],
            traits=[rng.choice(["brave", "shrewd", "just", "wrathful", "honest"])],
            martial=rng.randint(3, 12),
            diplomacy=rng.randint(3, 12),
            stewardship=rng.randint(3, 12),
            intrigue=rng.randint(3, 12),
        )
        state.characters[lord.id] = lord
        next_char_id += 1

        realm = Realm(
            id=realm_def["id"],
            name=realm_def["name"],
            owner_id=lord.id,
            color=REALM_COLORS[realm_def["color_key"]],
            description=realm_def["description"],
            province_ids=list(realm_def["provinces"]),
            capital_province_id=realm_def["provinces"][0] if realm_def["provinces"] else None,
            treasury=realm_def["treasury"],
        )
        state.realms[realm.id] = realm

    state.add_log("Eight realms watch the marches; one will rise.")
    return state


def set_player(state: GameState, realm_id: int) -> None:
    realm = state.realms.get(realm_id)
    if realm is None:
        raise ValueError(f"Unknown realm id {realm_id}")
    state.player_character_id = realm.owner_id
    player = state.characters[realm.owner_id]
    state.add_log(f"You are {player.title.display_name} {player.full_name} of {realm.name}.")


def new_game(seed: int | None = None, realm_id: int = 1) -> GameState:
    state = create_world(seed=seed)
    set_player(state, realm_id)
    return state
