from backend.quoridor.src.quoridor.board import Board
from backend.quoridor.src.quoridor.consts import COLUMN_INDEX, MOVEMENT_VECTORS, ROW_INDEX, Direction, Position
from backend.quoridor.src.quoridor.player import Player
from backend.quoridor.src.quoridor.wall import Wall


class MoveValidator:

    @classmethod
    def get_valid_moves(cls, board: Board, player: Player) -> dict[Direction, Position]:
        valid_moves = {}
        for direction, (row_change, col_change) in MOVEMENT_VECTORS.items():
            new_position = (player.position[ROW_INDEX] + row_change, player.position[COLUMN_INDEX] + col_change)

            # General validation
            if not cls._is_valid_move(board, player.position, new_position, can_skip=True):
                continue

            # Free cell
            if cls._is_valid_move(board, player.position, new_position, can_skip=False):
                valid_moves[direction] = new_position

            # Occupied cell
            elif board._get_cell_at(new_position).is_occupied:
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
        return valid_moves

    @classmethod
    def _is_valid_move(cls, board: Board, source: Position, destination: Position, can_skip: bool = False) -> bool:
        source_row, source_col = source
        destination_row, destination_col = destination
        # Illegal move
        if source_row != destination_row and source_col != destination_col:
            return False
        # Out of bounds
        if not (0 <= destination_row < board.size and 0 <= destination_col < board.size):
            return False
        # Occupied
        if not can_skip and board._get_cell_at(destination).is_occupied:
            return False
        # Blocked by wall
        if cls._is_blocked_by_wall(source, destination):
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
                wall_to_check = Wall(
                    top_left_cell=board._get_cell_at((source_row, source_col)), orientation=WallOrientation.VERTICAL
                )
            else:
                # Left
                wall_to_check = Wall(
                    top_left_cell=board._get_cell_at((destination_row, destination_col)),
                    orientation=WallOrientation.VERTICAL,
                )

        elif source_col == destination_col and abs(source_row - destination_row) == 1:
            # Vertical move
            if source_row < destination_row:
                # Down
                wall_to_check = Wall(
                    top_left_cell=board._get_cell_at((source_row, source_col)), orientation=WallOrientation.HORIZONTAL
                )
            else:
                # Up
                wall_to_check = Wall(
                    top_left_cell=board._get_cell_at((destination_row, destination_col)),
                    orientation=WallOrientation.HORIZONTAL,
                )

        return any(wall == wall_to_check for wall in board.walls)
