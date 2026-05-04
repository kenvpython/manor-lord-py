from enum import IntEnum


class Title(IntEnum):
    BARON = 1
    COUNT = 2
    DUKE = 3
    KING = 4

    @property
    def display_name(self) -> str:
        return self.name.capitalize()
