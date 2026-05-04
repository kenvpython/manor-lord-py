from manorlord.systems.base import System
from manorlord.systems.diplomacy import DiplomacySystem
from manorlord.systems.economy import EconomySystem
from manorlord.systems.event_system import EventSystem
from manorlord.systems.lifecycle import LifecycleSystem
from manorlord.systems.warfare import WarfareSystem


def default_systems() -> list[System]:
    return [
        EconomySystem(),
        LifecycleSystem(),
        DiplomacySystem(),
        WarfareSystem(),
        EventSystem(),
    ]


__all__ = [
    "System",
    "DiplomacySystem",
    "EconomySystem",
    "EventSystem",
    "LifecycleSystem",
    "WarfareSystem",
    "default_systems",
]
