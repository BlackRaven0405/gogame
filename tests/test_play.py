from gogame import *
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


def test_random_player():

    class SimplePlayer(Player):
        def play(self):
            moves = self.playable_moves()
            return moves[0] if moves else None

    p1 = SimplePlayer()
    p2 = SimplePlayer()

    b = Board()

    b.join(p1)
    b.join(p2)

    res = b.run_game(max_turn=500)
    assert res in {p1, p2}


def test_multi_player():

    class RandomPlayer(Player):
        def play(self):
            moves = self.playable_moves()
            return random.choice(moves) if moves else None

    class OrderPlayer(Player):
        def play(self):
            moves = self.playable_moves()
            return moves[0] if moves else None

    p1 = RandomPlayer()
    p2 = OrderPlayer()
    p3 = RandomPlayer()

    b = Board()

    for p in [p1, p2, p3]:
        b.join(p)

    res = b.run_game(max_turn=500)
    assert res in {p1, p2, p3}


def test_shaped_board():
    b = Board.circular((19, 15))
    p = Color.Black
    for x in range(25):
        playable = b.playable_moves(p)
        x, y = random.choice(playable)
        b.play(x, y, color=p)
        p = Color.White if p is Color.Black else Color.Black
