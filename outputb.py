# board.py
from typing import Optional
from pydantic import BaseModel, Field
from collections import deque

from backend.quoridor.src.quoridor.cell import Cell
from backend.quoridor.src.quoridor.consts import (
    COLUMN_INDEX,
    MOVEMENT_VECTORS,
    ROW_INDEX,
    SIZE,
    Direction,
    Position,
    WallOrientation,
)
from backend.quoridor.src.quoridor.player import Player
from backend.quoridor.src.quoridor.wall import Wall


class Board(BaseModel):
    board: list[list[Cell]] = Field(
        default_factory=lambda: [[Cell(position=(row, col)) for col in range(SIZE)] for row in range(SIZE)]
    )
    walls: set[Wall] = Field(default_factory=set)

    class Config:
        arbitrary_types_allowed = True

    # WALLS

    def place_wall(self, top_left_cell: Cell, orientation: WallOrientation) -> bool:
        if top_left_cell.position[COLUMN_INDEX] >= SIZE - 1 or top_left_cell.position[ROW_INDEX] >= SIZE - 1:
            return False
        new_wall = Wall(top_left_cell=top_left_cell, orientation=orientation)
        if any({wall for wall in self.walls if wall.top_left_cell == top_left_cell}):
            return False
        self.walls.add(new_wall)
        return True

    def bfs(self, start: Position, destination_set: set[Position]) -> Optional[list[Position]]:

        queue = deque([(start, [])])  # Start with the player's position
        visited = set()
        visited.add(start)

        while queue:
            current_position, path = queue.popleft()

            # If we reach a destination, return the path
            if current_position in destination_set:
                return path + [current_position]

            # Explore all valid moves (neighboring cells)
            for direction, (row_change, col_change) in MOVEMENT_VECTORS.items():
                new_position = (current_position[ROW_INDEX] + row_change, current_position[COLUMN_INDEX] + col_change)

                # If it's a valid move and hasn't been visited
                if self.is_valid_move(current_position, new_position) and new_position not in visited:
                    visited.add(new_position)
                    queue.append((new_position, path + [current_position]))

        return None  # No path found

    def validate_wall_placement(self, wall: Wall, players: list[Player]) -> bool:
        # 1. Check if the wall is within boundaries
        if not self._is_within_boundaries(wall):
            return False

        # 2. Check if the wall overlaps with an existing wall
        if self._overlaps_with_existing_wall(wall):
            return False

        # 3. Ensure no player is blocked from reaching their destination
        if not self._players_have_paths(players, wall):
            return False

        return True

    def _is_within_boundaries(self, wall: Wall) -> bool:
        row, col = wall.top_left_cell.position
        if not (0 <= row < SIZE and 0 <= col < SIZE):
            return False
        return True

    def _overlaps_with_existing_wall(self, new_wall: Wall) -> bool:
        for wall in self.walls:
            # Exact wall already exists
            if wall == new_wall:
                return True
            # Top-left cell conflict
            if wall.top_left_cell == new_wall.top_left_cell:
                return True
            else:
                # Partial overlap - vertical
                if (
                    new_wall.orientation == WallOrientation.VERTICAL
                    and wall.orientation == WallOrientation.VERTICAL
                    and abs(wall.top_left_cell.position[ROW_INDEX] - new_wall.top_left_cell.position[ROW_INDEX]) == 1
                ):
                    return True
                # Partial overlap - horizontal
                elif (
                    new_wall.orientation == WallOrientation.HORIZONTAL
                    and wall.orientation == WallOrientation.HORIZONTAL
                    and abs(wall.top_left_cell.position[COLUMN_INDEX] - new_wall.top_left_cell.position[COLUMN_INDEX])
                    == 1
                ):
                    return True
        return False

    def _players_have_paths(self, players: list[Player], proposed_wall: Wall) -> bool:
        # Temporarily add the wall for pathfinding test
        self.walls.add(proposed_wall)
        all_players_have_paths = True

        for player in players:
            destination_set = player.destination
            path = self.bfs(player.position, destination_set)
            if path is None:
                all_players_have_paths = False
                break

        # Remove the wall after testing
        self.walls.remove(proposed_wall)

        return all_players_have_paths

    ### MOVEMENT

    def get_valid_moves(self, player: Player) -> dict[Direction, Position]:
        valid_moves = {}
        for direction, (row_change, col_change) in MOVEMENT_VECTORS.items():
            new_position = (player.position[ROW_INDEX] + row_change, player.position[COLUMN_INDEX] + col_change)
            # Invalid
            if not self._is_valid_move(player.position, new_position, can_skip=True):
                continue
            # Occupied
            if self._get_cell_at(new_position).is_occupied:
                after_skip_position = (new_position[ROW_INDEX] + row_change, new_position[COLUMN_INDEX] + col_change)
                # If skippable
                if self._is_valid_move(new_position, after_skip_position, can_skip=False):
                    valid_moves[direction] = after_skip_position
                # If not skippable
                else:
                    orthagonals = direction.orthagonals()
                    for orthagonal_direction in orthagonals:
                        row_change, col_change = MOVEMENT_VECTORS[orthagonal_direction]
                        tested_position = (
                            new_position[ROW_INDEX] + row_change,
                            new_position[COLUMN_INDEX] + col_change,
                        )
                        if self._is_valid_move(new_position, tested_position, can_skip=False):
                            valid_moves[direction + orthagonal_direction] = tested_position

            elif self._is_valid_move(player.position, new_position, can_skip=False):
                valid_moves[direction] = new_position

        return valid_moves

    def _is_valid_move(self, source: Position, destination: Position, can_skip: bool = False) -> bool:
        source_row, source_col = source
        destination_row, destination_col = destination
        # Illegal move
        if source_row != destination_row and source_col != destination_col:
            return False
        # Out of bounds
        if not (0 <= destination_row < SIZE and 0 <= destination_col < SIZE):
            return False
        # Occupied
        if not can_skip and self._get_cell_at(destination).is_occupied:
            return False
        # Blocked by wall
        if self._is_blocked_by_wall(source, destination):
            return False

        return True

    def _is_blocked_by_wall(self, source: Position, destination: Position) -> bool:
        source_row, source_col = source
        destination_row, destination_col = destination
        wall_to_check = None

        if source_row == destination_row and abs(source_col - destination_col) == 1:
            # Horizontal move

            if source_col < destination_col:
                # Right
                wall_to_check = Wall(
                    top_left_cell=self._get_cell_at((source_row, source_col)), orientation=WallOrientation.VERTICAL
                )
            else:
                # Left
                wall_to_check = Wall(
                    top_left_cell=self._get_cell_at((destination_row, destination_col)),
                    orientation=WallOrientation.VERTICAL,
                )

        elif source_col == destination_col and abs(source_row - destination_row) == 1:
            # Vertical move
            if source_row < destination_row:
                # Down
                wall_to_check = Wall(
                    top_left_cell=self._get_cell_at((source_row, source_col)), orientation=WallOrientation.HORIZONTAL
                )
            else:
                # Up
                wall_to_check = Wall(
                    top_left_cell=self._get_cell_at((destination_row, destination_col)),
                    orientation=WallOrientation.HORIZONTAL,
                )

        return any(wall == wall_to_check for wall in self.walls)

    ### GENERAL UTILS

    def print_board(self, players: iter[Player]):
        """Print a visual representation of the board with walls."""
        for row in range(SIZE):
            # Print cells and vertical walls
            for col in range(SIZE):
                cell = self._get_cell_at((row, col))

                # Display cell content (e.g., players)
                if cell.standing_player:
                    print(f" {cell.standing_player.name[0]} ", end="")  # Player's first letter
                else:
                    value = "."
                    for player in players:
                        if player.position == (row, col):
                            value = player.name

                    print(f" {value} ", end="")  # Empty cell

                # Check if there is a vertical wall to the right of the cell
                if col < SIZE - 1:  # Ensure we're not at the rightmost edge
                    vertical_wall_exists = any(
                        wall.orientation == WallOrientation.VERTICAL
                        and (
                            (wall.top_left_cell == self._get_cell_at((row, col)))
                            or (row > 0 and wall.top_left_cell == self._get_cell_at((row - 1, col)))
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
                            (wall.top_left_cell == self._get_cell_at((row, col)))
                            or (col > 0 and wall.top_left_cell == self._get_cell_at((row, col - 1)))
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

    def set_occupation_state(self, players: set[Player]) -> None:
        for row in self.board:
            for cell in row:
                if cell.position in {player.position for player in players}:
                    cell.place_player(next(player for player in players if player.position == cell.position))
                else:
                    cell.remove_player()

    def _get_cell_at(self, position: Position) -> Cell:
        return self.board[position[ROW_INDEX]][position[COLUMN_INDEX]]

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

    @property
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
    UP_RIGHT = "upright"
    UP_LEFT = "upleft"
    DOWN_RIGHT = "downright"
    DOWN_LEFT = "downleft"

    def __add__(self, direction: "Direction") -> "Direction":
        try:
            try:
                return Direction(self.value + direction.value)
            except ValueError:
                return Direction(direction.value + self.value)
        except ValueError as e:
            raise ValueError(
                f"You can only add orthagonal, on-axis direction (tried to add {self.value} and {direction.value})."
            )

    def orthagonals(self) -> "Direction":
        vertical_directions = {Direction.UP, Direction.DOWN}
        horizontal_directions = {Direction.RIGHT, Direction.LEFT}
        if self in vertical_directions:
            return horizontal_directions
        elif self in horizontal_directions:
            return vertical_directions
        return {}

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
    Direction.LEFT: (0, -1),
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
    destination: set[Position] = Field(default={})
    wall_count: int = Field(default=10)

    class Config:
        arbitrary_types_allowed = True

    def has_reached_destination(self) -> bool:
        return self.position in self.destination

    def move(self, direction: Direction, skip: bool = False) -> None:
        row_change, col_change = MOVEMENT_VECTORS[direction]
        self.position = (self.row + row_change, self.column + col_change)

        if skip:
            self.position = (self.position[0] + row_change, self.position[1] + col_change)

    def use_wall(self) -> None:
        if self.wall_count > 0:
            self.wall_count -= 1

    def __hash__(self) -> int:
        return hash((self.name, self.position, self.wall_count))

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

