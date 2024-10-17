from quoridor.board import Board
from quoridor.consts import (
    COLUMN_INDEX,
    ROW_INDEX,
    WallOrientation,
)
from quoridor.player import Player
from quoridor.utils.path_finder import PathFinder
from quoridor.wall import Wall


class WallValidator:

    @classmethod
    def validate_wall_placement(cls, board: Board, players: list[Player], wall: Wall) -> bool:
        # 1. Check if the wall is within boundaries
        if not cls._is_within_boundaries(wall=wall, board_size=board.size):
            print("Err: not in boundaries")
            return False

        # 2. Check if the wall overlaps with an existing wall
        if cls._overlaps_with_existing_wall(board.walls, wall):
            print("Err: overlaps")
            return False

        # 3. Ensure no player is blocked from reaching their destination
        if not cls._players_have_paths(board, players, wall):
            print("Err: path-blocking")
            return False

        return True

    @staticmethod
    def _is_within_boundaries(wall: Wall, board_size: int) -> bool:
        row, col = wall.top_left_cell.position
        if not (0 <= row < board_size and 0 <= col < board_size):
            return False
        return True

    @staticmethod
    def _overlaps_with_existing_wall(walls: set[Wall], new_wall: Wall) -> bool:
        for wall in walls:
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
                    and wall.top_left_cell.position[COLUMN_INDEX] == new_wall.top_left_cell.position[COLUMN_INDEX]
                ):
                    return True
                # Partial overlap - horizontal
                elif (
                    new_wall.orientation == WallOrientation.HORIZONTAL
                    and wall.orientation == WallOrientation.HORIZONTAL
                    and abs(wall.top_left_cell.position[COLUMN_INDEX] - new_wall.top_left_cell.position[COLUMN_INDEX])
                    == 1
                    and wall.top_left_cell.position[ROW_INDEX] == new_wall.top_left_cell.position[ROW_INDEX]
                ):
                    return True
        return False

    @staticmethod
    def _players_have_paths(board: Board, players: list[Player], proposed_wall: Wall) -> bool:
        # Temporarily add the wall for pathfinding test
        board.walls.add(proposed_wall)
        all_players_have_paths = True

        for player in players:
            destination_set = player.destination
            path = PathFinder.shortest_path(board, player.position, destination_set)
            if path is None:
                all_players_have_paths = False
                break

        # Remove the wall after testing
        board.walls.remove(proposed_wall)
        return all_players_have_paths
