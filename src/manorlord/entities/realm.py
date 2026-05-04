from dataclasses import dataclass, field


@dataclass
class Realm:
    id: int
    name: str
    owner_id: int
    color: tuple[int, int, int] = (200, 180, 120)
    description: str = ""
    province_ids: list[int] = field(default_factory=list)
    capital_province_id: int | None = None
    treasury: int = 100
    income: int = 0
    troops: int = 0
    at_war_with: list[int] = field(default_factory=list)
