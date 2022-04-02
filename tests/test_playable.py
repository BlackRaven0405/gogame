from gopy import *


def test_two_eyes():
    pattern = np.array([[0, 0, 1, -1, 0, -1, 1, 0, 0],
                        [0, 0, 1, -1, -1, -1, 1, 0, 0],
                        [0, 0, 1, -1, 0, -1, 1, 0, 0],
                        [0, 0, 1, -1, -1, -1, 1, 0, 0],
                        [0, 0, 1, 1, 1, 1, 1, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0]])
    grid = np.vectorize(Color)(pattern)
    b = Board.from_grid(grid)
    assert not b.is_playable(0, 4, Color.Black)
    assert b.is_playable(0, 4, Color.White)


def test_one_eye():
    pattern = np.array([[0, 0, 1, -1, 0, -1, 1, 0, 0],
                        [0, 0, 1, -1, -1, -1, 1, 0, 0],
                        [0, 0, 1, 1, 1, 1, 1, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0]])
    grid = np.vectorize(Color)(pattern)
    b = Board.from_grid(grid)
    assert b.is_playable(0, 4, Color.Black)
    assert not b.is_playable(0, 4, Color.White)
