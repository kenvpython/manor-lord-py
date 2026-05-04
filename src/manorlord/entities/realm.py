from dataclasses import dataclass, field


@dataclass
class Realm:
    id: int
    name: str
    owner_id: int
    province_ids: list[int] = field(default_factory=list)
    treasury: int = 100
    income: int = 0
    troops: int = 0
    at_war_with: list[int] = field(default_factory=list)
