# board.py
from typing import Optional
from pydantic import BaseModel, Field

from backend.quoridor.src.quoridor.cell import Cell
from backend.quoridor.src.quoridor.consts import COLUMN_INDEX, ROW_INDEX, SIZE, WallOrientation
from backend.quoridor.src.quoridor.player import Player
from backend.quoridor.src.quoridor.wall import Wall


class Board(BaseModel):
    board: list[list[Cell]] = Field(
        default_factory=lambda: [[Cell(position=(row, col)) for col in range(SIZE)] for row in range(SIZE)]
    )
    walls: set[Wall] = Field(default_factory=set)

    class Config:
        arbitrary_types_allowed = True

    def place_wall(self, top_left_cell: Cell, orientation: WallOrientation) -> bool:
        if top_left_cell.position[COLUMN_INDEX] >= SIZE - 1 or top_left_cell.position[ROW_INDEX] >= SIZE - 1:
            return False
        new_wall = Wall(top_left_cell=top_left_cell, orientation=orientation)
        if any({wall for wall in self.walls if wall.top_left_cell == top_left_cell}):
            return False
        self.walls.add(new_wall)
        return True

    def print_board(self):
        """Print a visual representation of the board with walls."""
        for row in range(SIZE):
            # Print cells and vertical walls
            for col in range(SIZE):
                cell = self.board[row][col]

                # Display cell content (e.g., players)
                if cell.standing_player:
                    print(f" {cell.standing_player.name[0]} ", end="")  # Player's first letter
                else:
                    print(" . ", end="")  # Empty cell

                # Check if there is a vertical wall to the right of the cell
                if col < SIZE - 1:  # Ensure we're not at the rightmost edge
                    vertical_wall_exists = any(
                        wall.orientation == WallOrientation.VERTICAL
                        and (
                            (wall.top_left_cell == self.board[row][col])
                            or (row > 0 and wall.top_left_cell == self.board[row - 1][col])
                        )
                        for wall in self.walls
                    )
                    if vertical_wall_exists:
                        print("|", end="")  # Vertical wall
                    else:
                        print(" ", end="")  # No wall

            print()  # Newline after each row of cells

            # Print horizontal walls (if not on the last row)
            if row < SIZE - 1:
                for col in range(SIZE):
                    horizontal_wall_exists = any(
                        wall.orientation == WallOrientation.HORIZONTAL
                        and (
                            (wall.top_left_cell == self.board[row][col])
                            or (col > 0 and wall.top_left_cell == self.board[row][col - 1])
                        )
                        for wall in self.walls
                    )
                    if horizontal_wall_exists:
                        print("---", end="")  # Horizontal wall
                    else:
                        print("   ", end="")  # No wall

                    # Add spacing between columns
                    if col < SIZE - 1:
                        print(" ", end="")

                print()  # Newline after each row of walls

# cell.py
from typing import Optional
from pydantic import BaseModel

from backend.quoridor.src.quoridor.consts import Position
from backend.quoridor.src.quoridor.player import Player


class Cell(BaseModel):
    position: Position
    standing_player: Optional[Player] = None

    class Config:
        arbitrary_types_allowed = True

    def is_occupied(self) -> bool:
        return self.standing_player is not None

    def remove_player(self) -> None:
        self.standing_player = None

    def place_player(self, player: Player) -> None:
        self.standing_player = player

# consts.py
from enum import Enum

from pydantic import BaseModel

SIZE = 9


Position = tuple[int, int]
ROW_INDEX = 0
COLUMN_INDEX = 1


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"
    RIGHT = "right"
    LEFT = "left"

    def opposite(self) -> "Direction":
        if self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP
        elif self == Direction.RIGHT:
            return Direction.LEFT
        elif self == Direction.LEFT:
            return Direction.RIGHT
        raise ValueError(f"Unknown direction: {self}")


MOVEMENT_VECTORS = {
    Direction.UP: (-1, 0),
    Direction.DOWN: (1, 0),
    Direction.RIGHT: (0, 1),
    Direction.LEFT: (1, 0),
}


class WallOrientation(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

# game_manager.py

# __init__.py
from .board import Board
from .player import Player
from .cell import Cell
from .consts import Direction, WallOrientation, Position, MOVEMENT_VECTORS
from .wall import Wall

# player.py
from pydantic import BaseModel, Field

from backend.quoridor.src.quoridor.consts import MOVEMENT_VECTORS, Direction, Position


class Player(BaseModel):
    name: str
    position: Position
    wall_count: int = Field(default=10)

    class Config:
        arbitrary_types_allowed = True

    def move(self, direction: Direction, skip: bool = False) -> None:
        row_change, col_change = MOVEMENT_VECTORS[direction]
        self.position = (self.row + row_change, self.column + col_change)

        if skip:
            self.position = (self.position[0] + row_change, self.position[1] + col_change)

    def use_wall(self) -> None:
        if self.wall_count > 0:
            self.wall_count -= 1

# wall.py
from pydantic import BaseModel

from backend.quoridor.src.quoridor.cell import Cell
from backend.quoridor.src.quoridor.consts import WallOrientation


class Wall(BaseModel):
    top_left_cell: Cell
    orientation: WallOrientation

    class Config:
        arbitrary_types_allowed = True

    def __eq__(self, other):
        if not isinstance(other, Wall):
            return False
        return self.top_left_cell == other.top_left_cell and self.orientation == other.orientation

    def __hash__(self):
        return hash((self.top_left_cell.position, self.orientation))

