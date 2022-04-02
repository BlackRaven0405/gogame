# This program is an example of automatic game with two instances of a naive random player

import random
from gogame import *


class RandomPlayer(Player):
    def play(self):
        return random.choice(self.playable_moves())


b = Board(show=True)
p1 = RandomPlayer(name="John")
p2 = RandomPlayer(name="Smith")
b.join(p1)
b.join(p2)
winner = b.run_game(max_duration=60)
print(winner)
