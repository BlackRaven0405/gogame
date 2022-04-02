from gopy import *
import random


def test_game_with_capture():
    b = Board()
    b.play(4, 5, color=Color.Black)
    b.play(5, 5, color=Color.White)
    b.play(6, 5, color=Color.Black)
    b.play(0, 0, color=Color.White)
    b.play(5, 4, color=Color.Black)
    b.play(1, 0, color=Color.White)
    b.play(5, 6, color=Color.Black)
    b.play(0, 1, color=Color.White)
    b.play(6, 6, color=Color.Black)


def test_random_game():
    b = Board()
    p = Color.Black
    for x in range(20):
        playable = b.playable_moves(p)
        x, y = random.choice(playable)
        b.play(x, y, color=p)
        p = Color.White if p is Color.Black else Color.Black
