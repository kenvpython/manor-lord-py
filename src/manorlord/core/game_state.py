from dataclasses import dataclass, field

from manorlord.core.event_bus import EventBus
from manorlord.entities import Character, Province, Realm, Settlement


@dataclass
class GameState:
    turn: int = 1
    player_character_id: int | None = None
    characters: dict[int, Character] = field(default_factory=dict)
    realms: dict[int, Realm] = field(default_factory=dict)
    provinces: dict[int, Province] = field(default_factory=dict)
    settlements: dict[int, Settlement] = field(default_factory=dict)
    log: list[str] = field(default_factory=list)
    event_bus: EventBus = field(default_factory=EventBus, repr=False, compare=False)

    def add_log(self, message: str) -> None:
        self.log.append(f"[T{self.turn}] {message}")

    @property
    def player(self) -> Character | None:
        if self.player_character_id is None:
            return None
        return self.characters.get(self.player_character_id)

    @property
    def player_realm(self) -> Realm | None:
        player = self.player
        if player is None or player.realm_id is None:
            return None
        return self.realms.get(player.realm_id)

    def __getstate__(self) -> dict:
        state = self.__dict__.copy()
        state.pop("event_bus", None)
        return state

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
        self.event_bus = EventBus()
