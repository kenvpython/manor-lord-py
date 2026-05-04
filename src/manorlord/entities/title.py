from enum import IntEnum


class Title(IntEnum):
    BARON = 1
    COUNT = 2
    DUKE = 3
    KING = 4

    @property
    def display_name(self) -> str:
        return {
            Title.BARON: "男爵",
            Title.COUNT: "伯爵",
            Title.DUKE: "公爵",
            Title.KING: "国王",
        }[self]
