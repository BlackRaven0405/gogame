from gogame import *
import random


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
