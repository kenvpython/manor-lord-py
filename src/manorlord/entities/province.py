from dataclasses import dataclass, field


@dataclass
class Province:
    id: int
    name: str
    terrain: str = "plains"
    population: int = 1000
    base_tax: int = 5
    buildings: list[str] = field(default_factory=list)
    polygon: list[tuple[int, int]] = field(default_factory=list)
    center: tuple[int, int] = (0, 0)
