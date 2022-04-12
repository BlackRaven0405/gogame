from __future__ import annotations
import numpy as np
import warnings
import time
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from typing import (
    Optional,
    Union,
    Generator,
    TYPE_CHECKING
)

from .territory import Territory
from .enum import Color

if TYPE_CHECKING:
    from .player import Player

cmap = ListedColormap(["red", (0.59, 0.44, 0.2), "black", "white", "green", "blue", "yellow", "purple", "pink", "orange"])
color_list = [c.value for c in Color]
max_color = max(color_list)
min_color = min(color_list)


class Board:
    """Represents the goban of a game

    Note:
        Board vertices can be accessed through indices:

        >>> b = Board()
        >>> b[0,0]
        <Color.Empty: 0>
    """
    def __init__(self, *, size: Union[int, tuple[int, int]] = 19, show: bool = False):
        """
        Args:
            size: The size of the board, either an int for a square board, or a tuple (height, width)
            show: Indicates if the board should be displayed after each move"""
        if isinstance(size, int):
            height, width = size, size
        elif isinstance(size, (tuple, list, np.ndarray)):
            if len(size) == 2:
                height, width = size
            else:
                raise TypeError(f"size must be a 2-tuple but is of len {len(size)}")
        else:
            raise TypeError(f"size must be of type int or tuple but is of type {size.__class__.__name__}")
        self.show: bool = show
        self._grid: np.ndarray = np.full((height, width), Color.Empty)
        self._last_grid: np.ndarray = np.copy(self._grid)
        self._current_player: Optional[Player] = None
        self._territories: list[Territory] = [Territory(x=0, y=0, board=self)]
        self._players: dict[Color, Player] = {}
        self._prisoners: dict[Color, int] = {}

    @classmethod
    def circular(cls, size: Union[int, tuple[int, int]] = 19, show: bool = False) -> Board:
        """A quick way to generate a circular board using walls

        Args:
            size: An int denoting the diameter of the circle, or a 2-tuple denoting the two diameter of an oval
            show: Indicates if the board should be displayed after each move

        Returns:
            The generated board
        """
        board = cls(size=size, show=show)
        middle_x = board._grid.shape[0] / 2
        middle_y = board._grid.shape[1] / 2
        for x in range(board._grid.shape[0]):
            for y in range(board._grid.shape[1]):
                if (((x - middle_x + 0.5) / middle_x)**2 + ((y - middle_y + 0.5) / middle_y)**2) > 1:
                    board._grid[x, y] = Color.Wall
                    board._territories[0]._vertices.remove((x, y))
        return board

    def __getitem__(self, name: tuple[int, int]) -> Color:
        if not (isinstance(name, tuple) and len(name) == 2):
            raise IndexError("Not a valid indice")
        return self._grid[name]

    def __repr__(self):
        return f"<{self.__class__.__name__} width={self._grid.shape[0]} height={self._grid.shape[1]}>"

    def next_player(self, player: Optional[Player] = None) -> Player:
        """Returns the player who is next in the rotation of the game

        Args:
            player: The reference player. Default to the player currently playing.

        Raises:
            ValueError: The player you gave is not on the board or there is no player on the board

        Returns:
            The next player"""
        if not self._players:
            raise ValueError("No players are joined")
        if player:
            if player not in self._players.values():
                raise ValueError(f"{player} is not joined to this board")
        else:
            player = self._current_player
        players = sorted(self._players.values(), key=lambda p: p.color.value)
        return players[(players.index(player) + 1) % len(players)]

    def join(self, player: Player) -> None:
        """Links a player to the board for a game

        Args:
            player: The player to link

        Raises:
            ValueError: There are already two players linked"""
        if len(self._players) > max_color:
            raise ValueError("Board is already full")
        if player.color in self._players:
            raise ValueError("The color of this player is already used")
        if not self._players:
            self._current_player = player
        if player.color is None:
            player._color = next((c for c in Color if c.value > 0 and c not in self._players), None)
        self._players[player.color] = player
        player._initiate(board=self)

    def remove_player(self, player: Player) -> None:
        """Unlinks a player from the board

        Args:
            player: The player to unlink

        Raises:
            ValueError: This player is not linked to the board"""
        if player.color not in self._players:
            raise ValueError("Player is not joined")
        else:
            del self._players[player.color]
        if player is self._current_player:
            self._current_player = list(self._players.values())[0]

    def clear_players(self) -> None:
        """Unlinks all players from the board"""
        for player in self._players.values():
            player._clear_state()
        self._players = {}

    @classmethod
    def from_grid(cls, grid: np.ndarray) -> Board:
        """Initialize a board from an 2D array of :class:`Color`

        Args:
            grid: A 2D array of :class:`Color` representing the state of the board

        Returns:
            The new created board"""
        new_board = cls()
        new_board._grid = grid
        new_board._last_grid = np.full(grid.shape, Color.Empty)
        new_board._init_territories()
        return new_board

    def clone(self) -> Board:
        """Returns a deep copy of the board"""
        new_board = Board()
        new_board.show = self.show
        new_board._grid = np.copy(self._grid)
        new_board._players = dict(self._players)
        new_board._territories = [t.clone(new_board) for t in self._territories]
        return new_board

    def _init_territories(self) -> None:
        self._territories = []
        for x in range(self._grid.shape[0]):
            for y in range(self._grid.shape[1]):
                if not any((x, y) in t.vertices for t in self._territories):
                    self._territories.append(Territory(x=x, y=y, board=self))

    def display(self) -> None:
        """Displays the board as a numpy matrix"""
        plt.imshow(self.matrix(), cmap=cmap, vmin=min_color, vmax=max_color)
        plt.pause(0.1)

    def is_playable(self, x: int, y: int, color: Color) -> bool:
        """Checks if a move is valid

        Args:
            x: The x coordinate to check
            y: The y coordinate to check
            color: The color of the player to check

        Returns:
            Indicates if the move is valid"""
        if not color.is_player():
            raise ValueError(f"{color.name} is not a player color")
        if self[x, y] is not Color.Empty:
            return False
        grid = np.copy(self._grid)
        grid[x, y] = color
        if np.all(grid is self._last_grid):
            if np.all(self._last_grid is self._grid):
                return True
            return False
        mine = []
        opponent = []
        for i, j in self.around(x, y):
            if t := self.get_territory(i, j):
                if t.color is color:
                    mine.append(t)
                elif t.color is not Color.Empty:
                    opponent.append(t)
        if any(not t._hypothetical_freedom(x, y, color) for t in opponent):
            return True
        if len(opponent) == len(list(self.around(x, y))):
            return False
        if mine and all(not t._hypothetical_freedom(x, y, color) for t in mine):
            return False
        return True

    def playable_moves(self, color: Color) -> list[tuple[int, int]]:
        """ Gives the list of valid move for a given color

        Args:
            color: The player

        Returns:
            A list of all vertices where the player can play
        """
        playable = []
        for t in self._territories:
            if t.color is Color.Empty:
                for x, y in t.vertices:
                    if self.is_playable(x, y, color):
                        playable.append((x, y))
        return playable

    def run_game(self, max_turn: Optional[int] = 1000, max_duration: Optional[int] = None) -> Player:
        """Runs a game on this board between two players. The players have to be linked to the board with :func:`join` before

        Args:
            max_turn: The maximum number of move before ending the game
            max_duration: The maximum number of seconds before ending the game

        Raises:
            ValueError: Not enough players to start the game
            TypeError: A player returns an invalid move type

        Returns:
            The player who wins the game"""
        if len(self._players) < 2:
            raise ValueError("The board needs at least two players to be run")
        if max_turn is None and max_duration is None:
            warnings.warn("max_turn and max_duration are both to None, game might run forever")
        c = 0
        starting_time = time.time()
        while (not c or c < max_turn) and (not max_duration or time.time() - starting_time < max_duration):
            move = self._current_player.play()
            if move is None:
                if self.skip(color=self._current_player.color):
                    return self.winner()
            elif isinstance(move, (tuple, list, np.ndarray)) and len(move) == 2:
                self.play(*move, color=self._current_player.color)
            else:
                raise TypeError("play method must return None or a 2-tuple")
            c += 1
        return self.winner()

    def play(self, x: int, y: int, *, color: Color) -> None:
        """Play a move manually without using Player object

        Args:
            x: The x coordinate of the move to play
            y: The y coordinate of the move to play
            color: The color of the move to play

        Raises:
            ValueError: The move is invalid, or it's the wrong player"""
        self._verify_color_before_playing(color)

        if not self.is_playable(x, y, color):
            raise ValueError('You cannot play here')

        self._last_grid = np.copy(self._grid)
        self._grid[x, y] = color
        if self._players:
            self._current_player = self.next_player()

        modified = [t for t in self.territories(color) if t.is_touching(x, y)]
        for t in self._territories:
            t._update(x, y, color)
        if len(modified) >= 2:
            merge_territory = Territory.merge(*modified, with_vertice=(x, y))
            for t in modified:
                self._territories.remove(t)
            self._territories.append(merge_territory)

        for t in self.territories():
            if t.color.is_player() and (t.color is not color) and not t.freedom():
                t._color = Color.Empty
                if color not in self._prisoners:
                    self._prisoners[color] = 0
                for i, j in t.vertices:
                    self._grid[i, j] = Color.Empty
                    self._prisoners[color] += 1

        if not any(t.includes(x, y, color) for t in self._territories):
            new_territory = Territory(x=x, y=y, board=self)
            self._territories.append(new_territory)
        if self.show:
            self.display()

    def skip(self, *, color: Color) -> bool:
        """Skip a turn manually without using Player object

        Args:
            color: The color of the move to play

        Raises:
            ValueError: It's the wrong player

        Returns:
            True if the game is over because it's the second skip in a row, False otherwise"""

        self._verify_color_before_playing(color)
        if np.all(self._last_grid == self._grid) and not np.all(self._grid == Color.Empty):
            return True
        if self._players:
            self._current_player = self.next_player()
        self._last_grid = np.copy(self._grid)
        if self.show:
            self.display()
        return False

    def _verify_color_before_playing(self, color):
        if not color.is_player():
            raise ValueError(f"{color.name} is not a player color")
        if self._players:
            if color not in self._players:
                warnings.warn(f'{color.name} is not the color of a joined player')
            if color is not self._current_player.color:
                warnings.warn(f'The {color.name} player  is not supposed to play now')

    def winner(self) -> Player:
        """Returns the current winner of the board by comparing the scores of both player
        In case of equality, White wins

        Returns:
            The player who currently leads the game"""
        return max(reversed(self._players.values()), key=lambda p: self.score(p.color))

    def around(self,
               x: int,
               y: int,
               include_center: bool = False
               ) -> Generator[tuple[int, int], None, None]:
        """A quick way to get vertices around a given point

        Args:
            x: The x coordinate of the point
            y: The y coordinate of the point
            include_center: Wether to include the given point or not

        Yields:
            The points around"""
        if x > 0:
            yield x - 1, y
        if y > 0:
            yield x, y - 1
        if x < self._grid.shape[0] - 1:
            yield x + 1, y
        if y < self._grid.shape[1] - 1:
            yield x, y + 1
        if include_center:
            yield x, y

    def prisoners(self, color: Color) -> int:
        """Get the number of prisoners owned by a player

        Args:
            color: The color of the player

        Returns:
            The number of prisoners"""
        return self._prisoners.get(color, 0)

    def matrix(self) -> np.ndarray:
        """Returns the current state of the board as a numpy matrix to facilitate move calculation

        Returns:
            The matrix representing the board"""
        return np.vectorize(lambda c: c.value)(self._grid)

    def territories(self, color: Optional[Color] = None) -> list[Territory]:
        """Returns territories currently on the board. If a color is specified, only territories of the given color are returned

        Args:
            color: The color of the territories to get

        Returns:
            A list of territories"""
        if color is None:
            return self._territories
        else:
            return [x for x in self._territories if x.color is color]

    def get_territory(self,
                      x: int,
                      y: int
                      ) -> Optional[Territory]:
        """Get a territory from a vertice

        Args:
            x: The x coordinate of the territory to get
            y: The y coordinate of the territory to get

        Returns:
            The territory which owns the vertice if any"""
        for t in self._territories:
            if t.includes(x, y):
                return t
        return None

    def vertices(self, color: Color) -> list[tuple[int, int]]:
        """Get all vertices from a given color

        Args:
            color: The color of the vertices to get

        Returns:
            The list of vertices"""
        vertices = []
        for x in range(self._grid.shape[0]):
            for y in range(self._grid.shape[1]):
                if self[x, y] is color:
                    vertices.append((x, y))
        return vertices

    def score(self, color: Color) -> int:
        """Returns the score of a player i.e. the number of vertices belonging to the player + the number of his prisoners

        Args:
            color: The color of the player

        Returns:
             The score of the given player"""
        return self._prisoners.get(color, 0) + np.count_nonzero(self._grid == color)
