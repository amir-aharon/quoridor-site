from typing import Optional
from pydantic import BaseModel, Field
from collections import deque

from quoridor.board import Board
from quoridor.cell import Cell
from quoridor.consts import (
    COLUMN_INDEX,
    MOVEMENT_VECTORS,
    ROW_INDEX,
    Position,
)
from quoridor.utils.movement_validator import MovementValidator


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
            for direction, (row_dst, col_dst) in MovementValidator.get_position_valid_moves(
                board, current_position
            ).items():
                new_position = (row_dst, col_dst)

                # A valid move and hasn't been visited
                if new_position not in visited:
                    visited.add(new_position)
                    queue.append((new_position, path + [current_position]))
        return None
