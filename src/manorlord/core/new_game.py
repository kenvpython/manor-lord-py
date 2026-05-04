from __future__ import annotations

import json
import random
from pathlib import Path

from manorlord.core.game_state import GameState
from manorlord.entities import Character, Province, Realm, Title


_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_names() -> dict[str, list[str]]:
    with (_DATA_DIR / "names.json").open("r", encoding="utf-8") as fh:
        return json.load(fh)


def new_game(seed: int | None = None) -> GameState:
    rng = random.Random(seed)
    names = _load_names()

    state = GameState()

    province = Province(id=1, name="Ashford", terrain="plains", population=2400, base_tax=12)
    state.provinces[province.id] = province

    is_male = rng.random() < 0.5
    first_pool = names["male"] if is_male else names["female"]
    player = Character(
        id=1,
        first_name=rng.choice(first_pool),
        last_name=rng.choice(names["surnames"]),
        age=rng.randint(20, 40),
        is_male=is_male,
        title=Title.COUNT,
        realm_id=1,
        traits=[rng.choice(["brave", "shrewd", "just"])],
    )
    state.characters[player.id] = player
    state.player_character_id = player.id

    realm = Realm(
        id=1,
        name="County of Ashford",
        owner_id=player.id,
        province_ids=[province.id],
        treasury=150,
    )
    state.realms[realm.id] = realm

    state.add_log(f"{player.full_name} inherits {realm.name}.")
    return state
