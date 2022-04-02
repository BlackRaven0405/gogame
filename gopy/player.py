from abc import ABC, abstractmethod
import functools
from typing import (
    Optional,
    TYPE_CHECKING
)

import numpy as np

from .enum import Color

if TYPE_CHECKING:
    from .territory import Territory
    from .board import Board


def in_game(func):
    @functools.wraps(func)
    def f(self, *args, **kwargs):
        if self._in_game:
            if self._color and self._board:
                return func(self, *args, **kwargs)
            else:
                raise Exception("Player is in game but is not fully initialized")
        else:
            raise Exception("Player is not currently in game")
    return f


class Player(ABC):
    """Represents a go player.
    This class has to be overridden to implement the :func:`play()` method

    :Parameters:
        name: Optional[:class:`str`]
            The name of the player (only used to identify it)
    """
    def __init__(self, name: Optional[str] = None):
        self._in_game: bool = False
        self._board: Optional[Board] = None
        self._color: Optional[Color] = None
        self.name = name

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.__repr__()

    def __repr__(self):
        return f"<{self.__class__.__name__} color={self._color} board={self._board}>"

    def _initiate(self, board: 'Board', color: Color):
        self._in_game = True
        self._board = board
        self._color = color

    def _clear_state(self):
        self._in_game = False
        self._board = None
        self._color = None

    @property
    def is_in_game(self) -> bool:
        """Check if the player is currently linked to a board"""
        return self._in_game

    @property
    def board(self) -> Optional['Board']:
        """Returns the associated board if any"""
        return self._board

    @in_game
    def get_board_matrix(self) -> np.ndarray:
        """Returns the current state of the board (0 for empty, 1 for the player, -1 for the opponent)"""
        return self._board.matrix(self._color)

    @in_game
    def playable_moves(self) -> list[tuple[int, int]]:
        """Returns the list of all vertices available for playing"""
        return self._board.playable_moves(self._color)

    @in_game
    def my_vertices(self) -> list[tuple[int, int]]:
        """Returns a list of all vertices owned by the player"""
        return self._board.vertices(self._color)

    @in_game
    def opponent_vertices(self) -> list[tuple[int, int]]:
        """Returns a list of all vertices owned by the opponent"""
        return self._board.vertices(Color.Black if self._color is Color.White else Color.White)

    @in_game
    def free_vertices(self) -> list[tuple[int, int]]:
        """Returns a list of all empty vertices on the board"""
        return self._board.vertices(Color.Empty)

    @in_game
    def my_territories(self) -> list['Territory']:
        """Returns a list of territories owned by the player"""
        return self._board.territories(self._color)

    @in_game
    def opponent_territories(self) -> list['Territory']:
        """Returns a list of territories owned by the opponent"""
        return self._board.territories(Color.Black if self._color is Color.White else Color.White)

    @in_game
    def territories(self) -> list['Territory']:
        """Returns all territories on the board"""
        return self._board.territories()

    @abstractmethod
    def play(self) -> Optional[tuple[int, int]]:
        """This method has to be overridden by subclasses
        It's called when the player has to play and must return a 2-tuple (x, y) representing a move, or None for skipping the turn"""
        pass
