from dataclasses import dataclass


@dataclass
class Settlement:
    id: int
    name: str
    kind: str  # "capital" | "town" | "village"
    realm_id: int
    province_id: int
    local_x: int
    local_y: int
    population: int
