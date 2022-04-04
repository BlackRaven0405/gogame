from gogame import *


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
