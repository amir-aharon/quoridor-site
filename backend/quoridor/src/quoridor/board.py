from typing import Iterable, Optional
from pydantic import BaseModel, Field, model_validator
from collections import deque

from quoridor.cell import Cell
from quoridor.consts import (
    COLUMN_INDEX,
    MOVEMENT_VECTORS,
    ROW_INDEX,
    SIZE,
    Position,
    WallOrientation,
)
from quoridor.player import Player
from quoridor.wall import Wall


class Board(BaseModel):
    size: int
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

    def set_occupation_state(self, players: set[Player]) -> None:
        for row in self.board:
            for cell in row:
                if cell.position in {player.position for player in players}:
                    cell.place_player(next(player for player in players if player.position == cell.position))
                else:
                    cell.remove_player()

    def _get_cell_at(self, position: Position) -> Cell:
        return self.board[position[ROW_INDEX]][position[COLUMN_INDEX]]
