import random
from gogame import *


def test_random_game():
    b = Board.circular((19, 15))
    p = Color.Black
    for x in range(25):
        playable = b.playable_moves(p)
        x, y = random.choice(playable)
        b.play(x, y, color=p)
        p = Color.White if p is Color.Black else Color.Black
