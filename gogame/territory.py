from __future__ import annotations
import numpy as np
from typing import (
    Optional,
    TYPE_CHECKING
)

from .enum import Color

if TYPE_CHECKING:
    from .board import Board


class Territory:
    """Represents a territory i.e. a list of nearby vertices of the same color"""
    def __init__(self, *,
                 x: Optional[int] = None,
                 y: Optional[int] = None,
                 vertices: Optional[list[tuple[int, int]]] = None,
                 board: Board
                 ):
        """
        :param x: The x coordinate of the vertice to use to initiate the territory. This cannot be mixed with the `vertices` parameter

        :param y: The y coordinate of the vertice to use to initiate the territory. This cannot be mixed with the `vertices` parameter

        :param vertices: A list of vertices to initiate the territory. This cannot be mixed with the `x` and `y` parameters

        :notes: When using the `x, y` initializer, the territory is built by exploring the board while with `vertices` it only uses the given vertices without any exploration

        :raises TypeError: Parameters are not of the right type

        :raises ValueError: Failed to create the territory with the given parameters
        """
        self._board: Board = board
        self._vertices: list[tuple[int, int]]
        self._freedom: list[tuple[int, int]]
        self._color: Color

        if vertices is not None and x is None and y is None:
            if not isinstance(vertices, list):
                raise TypeError(f'Expected type list for vertices but got {vertices.__class__.__name__}')
            if not vertices:
                raise ValueError('Vertices list cannot be empty')
            self._color = board[vertices[0]]
            if any(board[v] is not self._color for v in vertices):
                raise ValueError('Vertices are of different colors')
            self._vertices = vertices
            self._freedom = self._hypothetical_freedom() if self._color is not Color.Empty else []
            if not self.is_coherent:
                raise ValueError('Vertices are not all nearby')
        elif x is not None and y is not None and vertices is None:
            self._vertices = self._explore(x, y)
            self._color = board[x, y]
            self._freedom = self._hypothetical_freedom() if self._color is not Color.Empty else []
        else:
            raise TypeError("Please provide either vertices or both x and y")

    def __repr__(self):
        return f"<{self.__class__.__name__} board={self._board} size={self.size} color={self._color}>"

    @property
    def size(self) -> int:
        """Returns the number of vertices in the territory"""
        return len(self._vertices)

    @property
    def vertices(self) -> list[tuple[int, int]]:
        return self._vertices

    def clone(self, board: Optional[Board] = None) -> Territory:
        """Returns a deep copy of the territory

        :param board: The board to link the new territory, if None it's the same as the current territory

        :returns: The copy of the territory
        """
        new_territory = Territory(vertices=list(self._vertices), board=board if board else self._board)
        return new_territory

    def is_coherent(self) -> bool:
        return set(self._explore(*self._vertices[0])) == set(self._vertices)

    def _explore(self, x: int, y: int) -> list[tuple[int, int]]:
        to_explore = set(self._board.around(x, y))
        explored = [(x, y)]
        while to_explore:
            for i, j in list(to_explore):
                if self._board[i, j] is self._board[x, y]:
                    explored.append((i, j))
                    to_explore.update({k for k in self._board.around(i, j) if k not in explored})
                to_explore.remove((i, j))
        return explored

    @classmethod
    def merge(cls,
              *territories: Territory,
              with_vertice: Optional[tuple[int, int]] = None
              ) -> Territory:
        """Merge several connected territories into one

        :param territories: An argument list of territories to merge

        :param with_vertice: A vertice to connect all territories, if none is specified, territories have to be already connected

        :raises TypeError: Parameters aren't of the right type

        :raises ValueError: Failed to merge territories

        :returns: The new territory"""
        if n := next((t for t in territories if not isinstance(t, Territory)), None):
            raise TypeError(f'Expected value of type Territory, but got {n.__class__.__name__}')
        if len(territories) < 2:
            raise TypeError('Expected at least 2 argument for merging')
        if any(t._board != territories[0]._board for t in territories):
            raise ValueError('Territories are not on the same board')
        vertices = []
        if with_vertice:
            if not isinstance(with_vertice, (tuple, list, np.ndarray)) or not len(with_vertice) == 2:
                raise TypeError('Expected 2-len tuple for with_vertices')
            vertices.append(with_vertice)
        for x in territories:
            vertices.extend(x._vertices)
        new_territory = cls(vertices=list(set(vertices)), board=territories[0]._board)
        return new_territory

    def is_nearby(self, territory: Territory) -> bool:
        """Checks if a territory is connected

        :param territory: The territory to check

        :returns: Indicate if the territory is connected or not"""
        return any(territory.is_touching(x, y) for x, y in self._vertices)

    def is_touching(self, x: int, y: int) -> bool:
        """Checks if a vertice is touching the territory

        :param x: The x coordinate of the vertice

        :param y: The y coordinate of the vertice

        :returns: Indicate if the vertice is touching the territory"""
        for i, j in self._board.around(x, y):
            if (i, j) in self._vertices:
                return True
        return False

    def includes(self, x: int, y: int, color: Optional[Color] = None) -> bool:
        """Checks if a vertice is included in the territory

        :param x: The x coordinate of the vertice

        :param y: The y coordinate of the vertice

        :param color: The color of the targeted vertice

        :returns: Indicates if the vertice is included or not"""
        return (color is None or color is self._color) and (x, y) in self._vertices

    def _update(self, x: int, y: int, color: Color) -> None:
        if self.is_touching(x, y):
            if color is self._color:
                if (x, y) not in self._vertices:
                    self._vertices.append((x, y))
                    if self._color is not Color.Empty:
                        if (x, y) in self._freedom:
                            self._freedom.remove((x, y))
                        self._freedom.extend([(i, j) for i, j in self._board.around(x, y) if self._board[i, j] is Color.Empty])
            else:
                if (x, y) in self._vertices:
                    self._vertices.remove((x, y))
                    if self._color is not Color.Empty:
                        if self._board[x, y] is Color.Empty:
                            self._freedom.append((x, y))
                        for i, j in self._board.around(x, y):
                            if (i, j) in self._freedom and not any((k, l) in self._vertices for k, l in self._board.around(i, j)):
                                self._freedom.remove((i, j))
                else:
                    if (x, y) in self._freedom:
                        self._freedom.remove((x, y))

    @property
    def board(self) -> Board:
        """The board associated with the territory"""
        return self._board

    @property
    def color(self) -> Color:
        """The color of the territory"""
        return self._color

    def freedom(self) -> list[tuple[int, int]]:
        """Calculate the freedom of the territory, i.e. the vertices where it can expend

        :returns: The list of available vertices to expend the territory"""
        return self._freedom

    def _hypothetical_freedom(self,
                              x: Optional[int] = None,
                              y: Optional[int] = None,
                              color: Optional[Color] = None
                              ) -> list[tuple[int, int]]:
        if any(k is None for k in [x, y, color]) and not all(k is None for k in [x, y, color]):
            raise TypeError('x, y and color have to be all specified')
        free_vertices = []
        if x is not None and y is not None and color is not None:
            hypothetical_board = np.copy(self._board._grid)
            hypothetical_board[x, y] = color
            if color == self._color and self.is_touching(x, y):
                hypothetical_vertices = self._vertices + [(x, y)]
            else:
                hypothetical_vertices = self._vertices
        else:
            hypothetical_board = self._board._grid
            hypothetical_vertices = self._vertices
        for x, y in hypothetical_vertices:
            for i, j in self._board.around(x, y):
                if hypothetical_board[i, j] is Color.Empty and (i, j) not in free_vertices:
                    free_vertices.append((i, j))
        return free_vertices
