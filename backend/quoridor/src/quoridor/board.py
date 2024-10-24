from typing import Optional
from pydantic import BaseModel, Field, model_validator
from collections import deque

from backend.quoridor.src.quoridor.cell import Cell
from backend.quoridor.src.quoridor.consts import (
    COLUMN_INDEX,
    MOVEMENT_VECTORS,
    ROW_INDEX,
    SIZE,
    Position,
    WallOrientation,
)
from backend.quoridor.src.quoridor.player import Player
from backend.quoridor.src.quoridor.wall import Wall


class Board(BaseModel):
    size: int = Field(default=SIZE)
    board: list[list[Cell]] = Field(default_factory=list)
    walls: set[Wall] = Field(default_factory=set)

    @model_validator(mode="before")
    def initialize_board(cls, values):
        size = values.get("size", SIZE)
        values["board"] = [[Cell(position=(row, col)) for col in range(size)] for row in range(size)]
        return values

    class Config:
        arbitrary_types_allowed = True

    def place_wall(self, top_left_cell: Cell, orientation: WallOrientation) -> bool:
        new_wall = Wall(top_left_cell=top_left_cell, orientation=orientation)
        if any({wall for wall in self.walls if wall.top_left_cell == top_left_cell}):
            return False
        self.walls.add(new_wall)
        return True
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

    def print_board(self, players: iter[Player]):
        """Print a visual representation of the board with walls."""
        for row in range(self.size):
            # Print cells and vertical walls
            for col in range(self.size):
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
                if col < self.size - 1:  # Ensure we're not at the rightmost edge
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
            if row < self.size - 1:
                for col in range(self.size):
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
                    if col < self.size - 1:
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
