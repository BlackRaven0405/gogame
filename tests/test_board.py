from gogame import *
import pytest
import numpy as np


class MockPlayer(Player):
    def play(self):
        return None


def test_square_board_creation():
    b = Board(size=5)
    assert b._grid.shape == (5, 5)
    assert b._last_grid.shape == (5, 5)
    assert np.all(b._grid == Color.Empty)
    assert len(b._territories) == 1
    assert b._territories[0].color == Color.Empty
    assert len(b._territories[0]._vertices) == 25


def test_non_square_board_creation():
    b = Board(size=(3, 7))
    assert b._grid.shape == (3, 7)
    assert b._last_grid.shape == (3, 7)
    assert np.all(b._grid == Color.Empty)
    assert len(b._territories) == 1
    assert b._territories[0].color == Color.Empty
    assert len(b._territories[0]._vertices) == 21


@pytest.mark.parametrize(("shape", "grid"), [
    ((5, 5), np.array([
        [-1, 0, 0, 0, -1],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [-1, 0, 0, 0, -1]])),
    ((9, 7), np.array([
        [-1, -1, 0, 0, 0, -1, -1],
        [-1, 0, 0, 0, 0, 0, -1],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, -1],
        [-1, -1, 0, 0, 0, -1, -1]])),
])
def test_circular_board_creation(shape, grid):
    b = Board.circular(size=shape)
    assert b._grid.shape == shape
    assert b._last_grid.shape == shape
    reference_grid = np.vectorize(Color)(grid)
    assert np.all(b._grid == reference_grid)
    assert len(b._territories) == 1
    assert b._territories[0].color == Color.Empty
    assert len(b._territories[0]._vertices) == np.count_nonzero(grid == 0)


def test_get_item():
    b = Board.from_grid(np.vectorize(Color)(np.array([
        [0, 1, 1, 0],
        [0, 0, 2, 0],
        [0, -1, -1, 0]])))
    assert b[0, 0] == Color.Empty
    assert b[0, 1] == Color.Black
    assert b[1, 2] == Color.White
    assert b[2, 2] == Color.Wall


def test_next_player():
    b = Board()
    with pytest.raises(ValueError):
        b.next_player()
    p1 = MockPlayer(color=Color.Black)
    p2 = MockPlayer(color=Color.White)
    p3 = MockPlayer(color=Color.Yellow)
    b._players = {Color.Black: p1, Color.White: p2}
    b._current_player = p1
    assert b.next_player() == p2
    assert b.next_player(p2) == p1
    with pytest.raises(ValueError):
        b.next_player(p3)


def test_join():
    b = Board()
    p1 = MockPlayer(color=Color.White)
    p2 = MockPlayer()
    p3 = MockPlayer(color=Color.White)
    b.join(p1)
    assert b._players[Color.White] == p1
    b.join(p2)
    assert b._players[Color.Black] == p2
    with pytest.raises(ValueError):
        b.join(p3)


def test_remove_player():
    b = Board()
    p1 = MockPlayer(color=Color.Black)
    p2 = MockPlayer(color=Color.White)
    p3 = MockPlayer(color=Color.Yellow)
    b._players = {Color.Black: p1, Color.White: p2}
    b.remove_player(p2)
    assert b._players == {Color.Black: p1}
    with pytest.raises(ValueError):
        b.remove_player(p3)
    b.remove_player(p1)
    assert b._players == {}


def test_clear_players():
    b = Board()
    p1 = MockPlayer(color=Color.Black)
    p2 = MockPlayer(color=Color.White)
    b._players = {Color.Black: p1, Color.White: p2}
    b.clear_players()
    b.clear_players()


@pytest.mark.parametrize(("grid", "territory_count"), [
    (np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]]), 1),
    (np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0]]), 2),
    (np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 2, 0, 1, 0],
        [0, 2, 0, 0, 0],
        [0, 0, 0, 0, 0]]), 3),
])
def test_from_grid(grid, territory_count):
    b = Board.from_grid(np.vectorize(Color)(grid))
    assert b._grid.shape == grid.shape
    assert b._last_grid.shape == grid.shape
    reference_grid = np.vectorize(Color)(grid)
    assert np.all(b._grid == reference_grid)
    assert len(b._territories) == territory_count


@pytest.mark.parametrize(("grid", "checks"), [
    (np.array([[1, 2, 0, 2, 1],
               [1, 2, 2, 2, 1],
               [1, 2, 0, 2, 1],
               [1, 2, 2, 2, 1],
               [1, 1, 1, 1, 1]]), [(0, 0, Color.Black, False), (0, 2, Color.Black, False), (2, 2, Color.Black, False), (0, 2, Color.White, True), (2, 2, Color.White, True)]),
    (np.array([[1, 2, 0, 2, 1],
               [1, 2, 2, 2, 1],
               [1, 1, 1, 1, 1]]), [(0, 0, Color.Black, False), (0, 2, Color.Black, True), (0, 2, Color.White, False)]),
    (np.array([[-1, -1, 0, 0, 1, 0],
               [-1, 0, 0, 1, 0, 1],
               [0, 0, 0, 0, 1, 0]]), [(0, 0, Color.Black, False), (1, 1, Color.Black, True), (1, 1, Color.White, True), (1, 4, Color.Black, True), (1, 4, Color.White, False)])
])
def test_is_playable(grid, checks):
    b = Board.from_grid(np.vectorize(Color)(grid))
    for x, y, color, value in checks:
        assert b.is_playable(x, y, color) == value


@pytest.mark.parametrize(("grid", "black_values", "white_values"), [
    (np.array([[1, 2, 0, 2, 1],
               [1, 2, 2, 2, 1],
               [1, 2, 0, 0, 1]]), [(2, 2), (2, 3)], [(0, 2), (2, 2), (2, 3)]),
    (np.array([[0, 0],
               [0, 0]]), [(0, 0), (0, 1), (1, 0), (1, 1)], [(0, 0), (0, 1), (1, 0), (1, 1)]),
    (np.array([[0, 1, 0],
               [1, 0, 1],
               [0, 1, 0]]), [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)], []),
    (np.array([[1, 2, 0, 2, 1],
               [1, 2, 2, 2, 1],
               [1, 2, 0, 2, 1],
               [1, 2, 2, 2, 1],
               [1, 1, 1, 1, 1]]), [], [(0, 2), (2, 2)])
])
def test_playable_moves(grid, black_values, white_values):
    b = Board.from_grid(np.vectorize(Color)(grid))
    assert set(b.playable_moves(Color.Black)) == set(black_values)
    assert set(b.playable_moves(Color.White)) == set(white_values)


def test_run_game():
    ref_color = Color.Black
    count = 0
    move_list = [(0, 0), (0, 1), (1, 0), (1, 1), None, None]

    class RunPlayer(Player):
        def play(self):
            nonlocal ref_color, count
            assert ref_color is self._color
            ref_color = Color.White if ref_color is Color.Black else Color.Black
            move = move_list[count]
            count += 1
            return move

    p1 = RunPlayer()
    p2 = RunPlayer()
    b = Board(size=5)
    b.join(p1)
    b.join(p2)
    winner = b.run_game()
    assert winner == p2
    assert count == 6


def test_play():
    b = Board(size=5)
    b.play(0, 0, color=Color.Black)
    assert b._grid[0, 0] == Color.Black
    b.play(0, 1, color=Color.White)
    assert b._grid[0, 1] == Color.White
    b.play(0, 2, color=Color.Black)
    with pytest.raises(ValueError):
        b.play(0, 1, color=Color.White)
    b.play(3, 3, color=Color.White)
    b.play(1, 1, color=Color.Black)
    assert b._grid[0, 1] == Color.Empty
    with pytest.raises(ValueError):
        b.play(0, 1, color=Color.White)
    assert b._grid[0, 1] == Color.Empty


def test_skip():
    b = Board(size=5)
    b.play(0, 0, color=Color.Black)
    reference = np.copy(b._grid)
    assert not b.skip(color=Color.White)
    assert np.all(reference == b._grid)
    assert b.skip(color=Color.Black)


def test_winner():
    b = Board()
    p1 = MockPlayer(color=Color.Black)
    p2 = MockPlayer(color=Color.White)
    b._players = {Color.Black: p1, Color.White: p2}
    assert b.winner() is p2
    b._grid[0, 0] = Color.Black
    assert b.winner() is p1
    b._prisoners[Color.White] = 1
    assert b.winner() is p2
    b._prisoners[Color.Black] = 1
    assert b.winner() is p1


def test_around():
    grid = np.array([[1, 2, 0, 2, 1],
                     [1, 2, 2, 2, 1],
                     [1, 2, 0, 2, 1],
                     [1, 2, 2, 2, 1]])
    b = Board.from_grid(np.vectorize(Color)(grid))
    assert set(b.around(0, 0)) == {(0, 1), (1, 0)}
    assert set(b.around(1, 1)) == {(0, 1), (1, 0), (2, 1), (1, 2)}
    assert set(b.around(3, 2, include_center=True)) == {(3, 1), (3, 2), (3, 3), (2, 2)}
