from typing import Optional
from pydantic import BaseModel, Field
from collections import deque

from backend.quoridor.src.quoridor.board import Board
from backend.quoridor.src.quoridor.cell import Cell
from backend.quoridor.src.quoridor.consts import (
    COLUMN_INDEX,
    MOVEMENT_VECTORS,
    ROW_INDEX,
    Position,
)
from backend.quoridor.src.quoridor.utils.movement_validator import MoveValidator


class PathFinder:

    @classmethod
    def shortest_path(cls, board: Board, start: Position, destination_set: set[Position]) -> Optional[list[Position]]:
        return cls.bfs(board, start, destination_set)

    @staticmethod
    def bfs(board: Board, start: Position, destination_set: set[Position]) -> Optional[list[Position]]:

        queue = deque([(start, [])])
        visited = set()
        visited.add(start)

        while queue:
            current_position, path = queue.popleft()

            # If we reach a destination, return the path
            if current_position in destination_set:
                return path + [current_position]

            # Explore all non-blocked neighboring cells
            for direction, (row_change, col_change) in MOVEMENT_VECTORS.items():
                new_position = (current_position[ROW_INDEX] + row_change, current_position[COLUMN_INDEX] + col_change)

                # A valid move and hasn't been visited
                if (
                    not MoveValidator._is_blocked_by_wall(board, current_position, new_position)
                    and new_position not in visited
                ):
                    visited.add(new_position)
                    queue.append((new_position, path + [current_position]))
        return None
