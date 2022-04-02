from enum import Enum


class Color(Enum):
    Black = 1
    White = -1
    Empty = 0

    def __bool__(self):
        return bool(self.value)
