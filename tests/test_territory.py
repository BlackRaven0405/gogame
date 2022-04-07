from gogame import *
import pytest
import numpy as np


@pytest.mark.parametrize(('vertices'), [
    ([(1, 1), (2, 1), (1, 3)]),
    ([(1, 3), (2, 3)])
])
def test_invalid_territory_creation(vertices):
    with pytest.raises(ValueError):
        grid = np.array([[0, 0, 0, 0, 0],
                         [0, 1, 0, 1, 0],
                         [0, 1, 0, 2, 0],
                         [0, 0, 0, 0, 0]])
        b = Board.from_grid(grid)
        t = Territory(vertices=vertices, board=b)


def test_valid_territory_creation():
    grid = np.array([[0, 0, 0, 0, 0],
                     [0, 1, 0, 1, 0],
                     [0, 1, 0, 2, 0],
                     [0, 0, 0, 0, 0]])
    b = Board.from_grid(np.vectorize(Color)(grid))
    vertices = [(1, 1), (2, 1)]
    t = Territory(vertices=vertices, board=b)


def test_exploration_creation():
    grid = np.array([[0, 0, 0, 0, 0],
                     [0, 1, 1, 1, 0],
                     [0, 1, 0, 1, 0],
                     [0, 1, 1, 1, 0]])
    b = Board.from_grid(np.vectorize(Color)(grid))
    t = Territory(x=1, y=1, board=b)
    assert set(t.vertices) == {(1, 1), (1, 2), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1), (2, 1)}


def test_invalid_merge():
    with pytest.raises(ValueError):
        b = Board(size=5)
        t1 = Territory(x=0, y=0, board=b)
        t2 = Territory(x=0, y=0, board=b)
        grid = np.array([[0, 0, 0, 0, 0],
                         [0, 1, 1, 1, 0],
                         [0, 2, 0, 1, 0],
                         [0, 2, 2, 2, 0]])
        b2 = Board.from_grid(np.vectorize(Color)(grid))
        t1._board = b2
        t2._board = b2
        t1._color = Color(1)
        t2._color = Color(2)
        t1._vertices = [(1, 1), (1, 2), (1, 3), (2, 3)]
        t2._vertices = [(3, 3), (3, 2), (3, 1), (2, 1)]
        t3 = Territory.merge(t1, t2)


def test_valid_merge():
    b = Board(size=5)
    t1 = Territory(x=0, y=0, board=b)
    t2 = Territory(x=0, y=0, board=b)
    grid = np.array([[0, 0, 0, 0, 0],
                     [0, 1, 1, 1, 0],
                     [0, 1, 0, 1, 0],
                     [0, 1, 1, 1, 0]])
    b2 = Board.from_grid(np.vectorize(Color)(grid))
    t1._board = b2
    t2._board = b2
    t1._vertices = [(1, 1), (1, 2), (1, 3), (2, 3)]
    t2._vertices = [(3, 3), (3, 2), (3, 1), (2, 1)]
    t1._color = Color(1)
    t2._color = Color(1)
    t3 = Territory.merge(t1, t2)
    assert set(t3.vertices) == {(1, 1), (1, 2), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1), (2, 1)}


def test_is_nearby():
    grid = np.array([[0, 0, 0, 0, 0],
                     [0, 1, 1, 3, 0],
                     [0, 1, 0, 3, 0],
                     [0, 2, 2, 1, 0]])
    b = Board.from_grid(np.vectorize(Color)(grid))
    t1 = Territory(x=1, y=1, board=b)
    t2 = Territory(x=3, y=1, board=b)
    t3 = Territory(x=1, y=3, board=b)
    t4 = Territory(x=3, y=3, board=b)
    assert t1.is_nearby(t2)
    assert t1.is_nearby(t3)
    assert not t1.is_nearby(t4)
    assert not t2.is_nearby(t3)


def test_is_touching():
    grid = np.array([[0, 0, 0, 0, 0],
                     [0, 1, 1, 1, 0],
                     [0, 1, 0, 1, 0],
                     [0, 1, 1, 1, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0]])
    b = Board.from_grid(np.vectorize(Color)(grid))
    t = Territory(x=1, y=1, board=b)
    assert t.is_touching(1, 1)
    assert t.is_touching(2, 2)
    assert not t.is_touching(0, 0)
    assert t.is_touching(0, 2)
    assert not t.is_touching(5, 2)


def test_includes():
    grid = np.array([[0, 0, 0, 0, 0],
                     [0, 1, 1, 1, 0],
                     [0, 1, 0, 1, 0],
                     [0, 1, 1, 1, 0],
                     [0, 0, 0, 0, 0]])
    b = Board.from_grid(np.vectorize(Color)(grid))
    t = Territory(x=1, y=1, board=b)
    assert t.includes(1, 1)
    assert not t.includes(0, 1)
    assert not t.includes(2, 2)
    assert t.includes(3, 2)
    assert not t.includes(4, 2)


@pytest.mark.parametrize(('grid', 'vertice', 'expected_value'), [
    (np.array([[0, 0, 0, 0, 0],
               [0, 1, 1, 1, 0],
               [0, 1, 0, 1, 0],
               [0, 1, 1, 1, 0],
               [0, 0, 0, 0, 0]]), (1, 1), 13),
    (np.array([[0, 1, 1, 1, 0],
               [0, 0, 0, 1, 0],
               [0, 1, 1, 1, 0],
               [0, 0, 0, 0, 0]]), (0, 1), 10),
    (np.array([[0, 1, 1, 0, 0],
               [0, 1, 1, 1, 0],
               [0, 0, 0, 0, 0]]), (1, 1), 7),

])
def test_hypothetical_freedom(grid, vertice, expected_value):
    b = Board.from_grid(np.vectorize(Color)(grid))
    t = Territory(x=vertice[0], y=vertice[1], board=b)
    assert len(t._hypothetical_freedom()) == expected_value
