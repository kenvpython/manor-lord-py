from dataclasses import dataclass, field

from manorlord.entities.title import Title


@dataclass
class Character:
    id: int
    first_name: str
    last_name: str
    age: int
    is_male: bool
    title: Title = Title.BARON
    realm_id: int | None = None
    traits: list[str] = field(default_factory=list)

    martial: int = 5
    diplomacy: int = 5
    stewardship: int = 5
    intrigue: int = 5

    loyalty: int = 50
    is_alive: bool = True

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
