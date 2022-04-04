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

cmap = ListedColormap(["white", (0.59, 0.44, 0.2), "black"])


class Board:
    """ Represents the goban of a game

    :Parameters:
        size: Union[:class:`int`, tuple[:class:`int`, :class:`int`]]
            The size of the board, either an int for a square board, or a tuple (height, width)
        show: :class:`int`
            Indicates if the board should be displayed after each move. Default to `False`

    :Notes:
        Board vertices can be accessed through indices:

        >>> b = Board()
        >>> b[0,0]
        <Color.Empty: 0>
    """
    def __init__(self, *, size: Union[int, tuple[int, int]] = 19, show: bool = False):
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
        self._next_player: Color = Color.Black
        self._prisoners: dict[Color, int] = {Color.Black: 0, Color.White: 0}
        self._territories: list[Territory] = [Territory(x=0, y=0, board=self)]
        self._players: dict[Color, Optional[Player]] = {Color.Black: None, Color.White: None}

    def __getitem__(self, name: tuple[int, int]) -> Color:
        if not (isinstance(name, tuple) and len(name) == 2):
            raise IndexError("Not a valid indice")
        return self._grid[name]

    def __repr__(self):
        return f"<{self.__class__.__name__} width={self._grid.shape[0]} height={self._grid.shape[1]}>"

    @staticmethod
    def other_player(color: Color) -> Color:
        """Returns the other color (black for white and white for black)"""
        if color is Color.Empty:
            raise ValueError("Player cannot be Empty")
        return Color.Black if color is Color.White else Color.White

    def join(self, player: 'Player') -> None:
        """Links a player to the board for a game

        :Parameters:
            player: :class:`Player`
                The player to link

        :Raises:
            :class:`ValueError`
                There are already two players linked"""
        if not self._players[Color.Black]:
            self._players[Color.Black] = player
            player._initiate(self, Color.Black)
        elif not self._players[Color.White]:
            self._players[Color.White] = player
            player._initiate(self, Color.White)
        else:
            raise ValueError("Both player are already joined")

    def remove_player(self, player: 'Player') -> None:
        """Unlinks a player from the board

        :Parameters:
            player: :class:`Player`
                The player to unlink

        :Raises:
            :class:`ValueError`
                This player is not linked to the board"""
        if player is self._players[Color.Black]:
            self._players[Color.Black]._clear_state()
            self._players[Color.Black] = None
        elif player is self._players[Color.White]:
            self._players[Color.White] = None
            self._players[Color.White]._clear_state()
        else:
            raise ValueError("Player is not joined")

    def clear_players(self) -> None:
        """Unlinks all players from the board"""
        for player in self._players.values():
            player._clear_state()
        self._players = {Color.Black: None, Color.White: None}

    @classmethod
    def from_grid(cls, grid: np.ndarray):
        """Initialize a board from an 2D array of :class:`Color`

        :Parameters:
            grid: :class:`np.ndarray`
                A 2D array of :class:`Color` representing the state of the board

        :Returns:
            The new created board"""
        new_board = cls()
        new_board._grid = grid
        new_board._last_grid = np.full(grid.shape, Color.Empty)
        new_board._init_territories()
        return new_board

    def clone(self) -> 'Board':
        """Returns a deep copy of the board"""
        new_board = Board()
        new_board.show = self.show
        new_board._grid = np.copy(self._grid)
        new_board._next_player = self._next_player
        new_board._prisoners = dict(self._prisoners)
        new_board._territories = [t.clone(new_board) for t in self._territories]
        return new_board

    def _init_territories(self) -> None:
        self._territories = []
        for x in range(self._grid.shape[0]):
            for y in range(self._grid.shape[1]):
                if not any((x, y) in t._vertices for t in self._territories):
                    self._territories.append(Territory(x=x, y=y, board=self))

    def display(self) -> None:
        """Displays the board as a numpy matrix"""
        plt.imshow(self.matrix(Color.Black), cmap=cmap, vmin=-1, vmax=1)
        plt.pause(0.1)

    def is_playable(self, x: int, y: int, color: Color) -> bool:
        """
        Checks if a move is valid

        :Parameters:
            x: :class:`int`
                The x coordinate to check
            y: :class:`int`
                The y coordinate to check
            color: :class:`int`
                The color of the player to check

        :Returns:
            Indicates if the move is valid
        """
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

        :Parameters:
            color: :class:`Color`
                The player

        :Returns:
            A list of all vertices where the player can play
        """
        playable = []
        for t in self._territories:
            if t.color is Color.Empty:
                for x, y in t._vertices:
                    if self.is_playable(x, y, color):
                        playable.append((x, y))
        return playable

    def run_game(self, max_turn: Optional[int] = 1000, max_duration: Optional[int] = None) -> 'Player':
        """Runs a game on this board between two players. The players have to be linked to the board with :func:`join` before

        :Parameters:
            max_turn: Optional[:class:`int`]
                The maximum number of move before ending the game
            max_duration: Optional[:class:`int`]
                The maximum number of seconds before ending the game

        :Raises:
            :class:`ValueError`
                Not enough players to start the game
            :class:`TypeError`
                A player returns an invalid move type

        :Returns:
            The player who wins the game"""
        if any(player is None for player in self._players):
            raise ValueError("The board needs two players to be run")
        if max_turn is None and max_duration is None:
            warnings.warn("max_turn and max_duration are both to None, game might run forever")
        c = 0
        starting_time = time.time()
        while (not c or c < max_turn) and (not max_duration or time.time()-starting_time < max_duration):
            move = self._players[self._next_player].play()
            if move is None:
                if self.skip(player=self._next_player):
                    return self.winner()
            elif isinstance(move, (tuple, list, np.ndarray)) and len(move) == 2:
                self.play(*move, color=self._next_player)
            else:
                raise TypeError("play method must return None or a 2-tuple")
            c += 1
        return self.winner()

    def play(self, x: int, y: int, *, color: Color) -> None:
        """Play a move manually without using Player object

        :Parameters:
            x: :class:`int`
                The x coordinate of the move to play
            y: :class:`int`
                The y coordinate of the move to play
            color: :class:`Color`
                The color of the move to play

        :Raises:
            :class:`ValueError`
                The move is invalid, or it's the wrong player"""
        if color is not self._next_player:
            raise ValueError('Wrong player')

        if not self.is_playable(x, y, color):
            raise ValueError('You cannot play here')

        self._last_grid = np.copy(self._grid)
        self._grid[x, y] = color
        self._next_player = self.other_player(self._next_player)

        modified = [t for t in self.territories(color) if t.is_touching(x, y)]
        for t in self._territories:
            t._update(x, y, color)
        if len(modified) >= 2:
            merge_territory = Territory.merge(*modified, with_vertice=(x, y))
            for t in modified:
                self._territories.remove(t)
            self._territories.append(merge_territory)

        for t in self.territories(self.other_player(color)):
            if not t.freedom:
                self._territories.remove(t)
                for i, j in t._vertices:
                    self._grid[i, j] = 0
                    self._prisoners[color] += 1

        if not any(t.includes(x, y, color) for t in self._territories):
            new_territory = Territory(x=x, y=y, board=self)
            self._territories.append(new_territory)
        if self.show:
            self.display()

    def skip(self, *, player: Color, show: Optional[bool] = None) -> Optional[bool]:
        """Skip a turn manually without using Player object

            :Raises:
                :class:`ValueError`
                    It's the wrong player"""
        if player is not self._next_player:
            raise ValueError('Wrong player')
        if np.all(self._last_grid is self._grid):
            return True
        self._next_player = self.other_player(player)
        if show is True or (show is None and self.show):
            self.display()

    def winner(self) -> 'Player':
        """Returns the current winner of the board by comparing the scores of both player
        In case of equality, White wins

        :Returns:
            The player who currently leads the game"""
        if self.score(Color.Black) > self.score(Color.White):
            return self._players[Color.Black]
        return self._players[Color.White]

    def around(self,
               x: int,
               y: int,
               include_center: bool = False
               ) -> Generator[tuple[int, int], None, None]:
        """A quick way to get vertices around a given point

        :Parameters:
            x: :class:`int`
                The x coordinate of the point
            y: :class:`int`
                The y coordinate of the point
            include_center: :class:`bool`
                Wether to include the given point or not

        :Yields:
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

        :Parameters:
            color: :class:`Color`
                The color of the player

        :Returns:
            The number of prisoners"""
        return self._prisoners[color]

    def matrix(self, color: Color) -> np.ndarray:
        """Returns the current state of the board as a numpy matrix

        * 0 is an empty vertice
        * 1 is a vertice the player owns
        * -1 is a vertice owned by the opponent

        :Parameters:
            color: :class:`Color`
                The color of the player

        :Returns:
            The matrix representing the board
        """
        grid = np.vectorize(lambda x: x.value)(self._grid)
        return -grid if color is Color.White else grid

    def territories(self, color: Optional[Color] = None) -> list[Territory]:
        """Returns territories currently on the board. If a color is specified, only territories of the given color are returned

        :Parameters:
            color: Optional[:class:`Color`]
                The color of the territories to get

        :Returns:
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

        :Parameters:
            x: :class:`int`
                The x coordinate of the territory to get
            y: :class:`int`
                The y coordinate of the territory to get

        :Returns:
            The territory which owns the vertice if any"""
        for t in self._territories:
            if t.includes(x, y):
                return t
        return None

    def vertices(self, color: Color) -> list[tuple[int, int]]:
        """Get all vertices from a given color

        :Parameters:
            color: :class:`Color`
                The color of the vertices to get

        :Returns:
            The list of vertices"""
        vertices = []
        for x in range(self._grid.shape[0]):
            for y in range(self._grid.shape[1]):
                if self[x, y] is color:
                    vertices.append((x, y))
        return vertices

    def score(self, color: Color) -> int:
        """Returns the score of a player i.e. the number of vertices belonging to the player + the number of his prisoners

        :Parameters:
            color: :class:`Color`
                The color of the player

        :Returns:
            The score of the given player"""
        return self._prisoners[color] + np.count_nonzero(self._grid is color)
