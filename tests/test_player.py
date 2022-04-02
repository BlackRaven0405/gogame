from gogame import *


def test_random_player():

    class RandomPlayer(Player):
        def play(self):
            l = self.playable_moves()
            return l[0] if l else None

    p1 = RandomPlayer()
    p2 = RandomPlayer()

    b = Board()

    b.join(p1)
    b.join(p2)

    res = b.run_game(max_turn=500)
    assert res in {p1, p2}
