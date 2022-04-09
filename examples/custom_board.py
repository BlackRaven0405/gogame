# This program is an example of how you can subclass the Board class to create a custom score system.
# Here each player gets additional points depending on their order in the game.

from gogame import *


class CustomBoard(Board):
    def score(self, color: Color) -> int:
        value = self.prisoners(color) + len(self.vertices(color))
        if self._players:
            players = sorted(self._players, key=lambda c: c.value)
            value += players.index(color) * 7
        else:
            value += (color.value - 1) * 7
        return value


b = CustomBoard()
b.play(15, 3, color=Color.Black)
b.play(15, 15, color=Color.White)
b.play(3, 3, color=Color.Black)
b.play(2, 15, color=Color.White)
print(b.score(Color.Black))
print(b.score(Color.White))
