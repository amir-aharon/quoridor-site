from typing import Optional
from pydantic import BaseModel, Field

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

    def print_board(self):
        """Print a visual representation of the board with walls."""
        for row in range(SIZE):
            # Print cells and vertical walls
            for col in range(SIZE):
                cell = self._get_cell_at((row, col))

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

    def place_wall(self, top_left_cell: Cell, orientation: WallOrientation) -> bool:
        if top_left_cell.position[COLUMN_INDEX] >= SIZE - 1 or top_left_cell.position[ROW_INDEX] >= SIZE - 1:
            return False
        new_wall = Wall(top_left_cell=top_left_cell, orientation=orientation)
        if any({wall for wall in self.walls if wall.top_left_cell == top_left_cell}):
            return False
        self.walls.add(new_wall)
        return True

    def get_valid_moves(self, player: Player) -> dict[Direction, Position]:
        valid_moves = {}
        for direction, (row_change, col_change) in MOVEMENT_VECTORS.items():
            new_position = (player.position[ROW_INDEX] + row_change, player.position[COLUMN_INDEX] + col_change)
            # Invalid
            if not self._is_valid_move(player.position, new_position, can_skip=True):
                continue
            # Occupied but skipable
            if self._get_cell_at(new_position).is_occupied:
                after_skip_position = (new_position[ROW_INDEX] + row_change, new_position[COLUMN_INDEX] + col_change)
                if self._is_valid_move(new_position, after_skip_position, can_skip=False):
                    valid_moves[direction] = after_skip_position
            # Occupied and unskipable
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
