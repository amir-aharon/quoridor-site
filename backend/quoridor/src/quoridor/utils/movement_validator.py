from quoridor.board import Board
from quoridor.consts import (
    COLUMN_INDEX,
    MOVEMENT_VECTORS,
    ROW_INDEX,
    Direction,
    Position,
    WallOrientation,
)
from quoridor.player import Player
from quoridor.wall import Wall


class MovementValidator:

    @classmethod
    def get_player_valid_moves(cls, board: Board, player: Player) -> dict[Direction, Position]:
        return cls.get_position_valid_moves(board, player.position)

    @classmethod
    def get_position_valid_moves(cls, board: Board, position: Position) -> dict[Direction, Position]:
        valid_moves = {}
        for direction, (row_change, col_change) in MOVEMENT_VECTORS.items():
            new_position = (position[ROW_INDEX] + row_change, position[COLUMN_INDEX] + col_change)

            # General validation
            if not cls._is_valid_move(board, position, new_position, can_skip=True):
                continue

            # Occupied cell
            if board._get_cell_at(new_position).is_occupied:
                after_skip_position = (new_position[ROW_INDEX] + row_change, new_position[COLUMN_INDEX] + col_change)

                # Skippable
                if cls._is_valid_move(board, new_position, after_skip_position, can_skip=False):
                    valid_moves[direction] = after_skip_position

                # Not skippable
                else:
                    orthagonals = direction.orthagonals()
                    for orthagonal_direction in orthagonals:
                        row_change, col_change = MOVEMENT_VECTORS[orthagonal_direction]
                        tested_position = (
                            new_position[ROW_INDEX] + row_change,
                            new_position[COLUMN_INDEX] + col_change,
                        )
                        # Validate corner move
                        if cls._is_valid_move(board, new_position, tested_position, can_skip=False):
                            valid_moves[direction + orthagonal_direction] = tested_position

            # Free cell
            elif cls._is_valid_move(board, position, new_position, can_skip=False):
                valid_moves[direction] = new_position

        return valid_moves

    @classmethod
    def _is_valid_move(cls, board: Board, source: Position, destination: Position, can_skip: bool = False) -> bool:
        # Illegal move
        if not cls._basic_validation(board, source, destination):
            return False
        # Occupied
        if not can_skip and board._get_cell_at(destination).is_occupied:
            return False
        # Blocked by wall
        if cls._is_blocked_by_wall(board, source, destination):
            return False
        return True

    @staticmethod
    def _basic_validation(board: Board, source: Position, destination: Position) -> bool:
        source_row, source_col = source
        destination_row, destination_col = destination
        # Illegal move
        if source_row != destination_row and source_col != destination_col:
            return False
        # Out of bounds
        if not (0 <= destination_row < board.size and 0 <= destination_col < board.size):
            return False
        return True

    @staticmethod
    def _is_blocked_by_wall(board: Board, source: Position, destination: Position) -> bool:
        source_row, source_col = source
        destination_row, destination_col = destination
        wall_to_check = None

        if source_row == destination_row and abs(source_col - destination_col) == 1:
            # Horizontal move

            if source_col < destination_col:
                # Right
                walls_to_check = {
                    Wall(
                        top_left_cell=board._get_cell_at((source_row, source_col)), orientation=WallOrientation.VERTICAL
                    )
                }
                if source_row > 0:
                    walls_to_check.add(
                        Wall(
                            top_left_cell=board._get_cell_at((source_row - 1, source_col)),
                            orientation=WallOrientation.VERTICAL,
                        )
                    )
            else:
                # Left
                walls_to_check = {
                    Wall(
                        top_left_cell=board._get_cell_at((destination_row, destination_col)),
                        orientation=WallOrientation.VERTICAL,
                    )
                }
                if destination_row > 0:
                    walls_to_check.add(
                        Wall(
                            top_left_cell=board._get_cell_at((destination_row - 1, destination_col)),
                            orientation=WallOrientation.VERTICAL,
                        )
                    )

        elif source_col == destination_col and abs(source_row - destination_row) == 1:
            # Vertical move
            if source_row < destination_row:
                # Down
                walls_to_check = {
                    Wall(
                        top_left_cell=board._get_cell_at((source_row, source_col)),
                        orientation=WallOrientation.HORIZONTAL,
                    )
                }
                if source_col > 0:
                    walls_to_check.add(
                        Wall(
                            top_left_cell=board._get_cell_at((source_row, source_col - 1)),
                            orientation=WallOrientation.HORIZONTAL,
                        )
                    )
            else:
                # Up
                walls_to_check = {
                    Wall(
                        top_left_cell=board._get_cell_at((destination_row, destination_col)),
                        orientation=WallOrientation.HORIZONTAL,
                    )
                }
                if destination_col > 0:
                    walls_to_check.add(
                        Wall(
                            top_left_cell=board._get_cell_at((destination_row, destination_col - 1)),
                            orientation=WallOrientation.HORIZONTAL,
                        )
                    )

        return any(wall in walls_to_check for wall in board.walls)
