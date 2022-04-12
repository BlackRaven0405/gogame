from enum import Enum


class Color(Enum):
    """Specify the color of a vertice"""
    Empty = 0
    Black = 1
    White = 2
    Green = 3
    Blue = 4
    Yellow = 5
    Purple = 6
    Pink = 7
    Orange = 8

    Wall = -1

    def __bool__(self):
        return bool(self.value)

    def is_player(self) -> bool:
        """Check if a color is a player or a special value (empty, wall, etc...)"""
        return self.value > 0
