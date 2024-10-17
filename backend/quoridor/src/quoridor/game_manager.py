import sys
from typing import Callable, Iterable, Optional
from pydantic import BaseModel, Field
from quoridor.consts import SIZE, Direction, Position, WallOrientation
from quoridor.player import Player
from quoridor.board import Board
from quoridor.player_state import PlayerState
from quoridor.utils.movement_validator import MovementValidator
from quoridor.utils.wall_validator import WallValidator
from quoridor.wall import Wall


def process_position_string(s: str) -> Optional[Position]:
    s = s.split(",")
    s = [sub.strip() for sub in s]
    s = [int(sub) for sub in s if sub.isnumeric()]
    return tuple(s) if len(s) == 2 else None


class GameManager:
    def __init__(self, size: int = SIZE) -> None:
        self.board = Board(size=size)
        self.player_states: list[PlayerState] = [
            PlayerState(
                player=Player(
                    name="A".capitalize(),
                    position=(0, int(size / 2)),
                    destination={(size - 1, i) for i in range(size)},
                )
            ),
            PlayerState(
                player=Player(
                    name="B".capitalize(),
                    position=(size - 1, int(size / 2)),
                    destination={(0, i) for i in range(size)},
                )
            ),
        ]
        self.current_player_index = 0
        self.current_player_state = self.player_states[self.current_player_index]
        self.current_player = self.current_player_state.player
        self.turn = 1
        self.reload_state()

    def prompt(self, validator: any, message: str, try_again: str) -> str:
        op = input(message)
        while not validator(op):
            op = input(try_again)
        return op

    def movement_turn(self) -> bool:
        direction_name = self.prompt(
            validator=lambda op: not self.where_this_goes(op) is None,
            message="Enter direction: ",
            try_again="This direction is not valid, enter another: ",
        )
        dst_position = self.where_this_goes(direction_name)
        self.current_player.jump(dst_position)
        return self.check_win()

    def _validate_wall_position(self, wall_position: str, orientation: WallOrientation) -> bool:
        if process_position_string(wall_position) is None:
            return False
        return WallValidator.validate_wall_placement(
            self.board,
            [ps.player for ps in self.player_states],
            Wall(
                top_left_cell=self.board._get_cell_at(process_position_string(wall_position)), orientation=orientation
            ),
        )

    def wall_turn(self) -> None:
        orientation_name = self.prompt(
            validator=lambda op: op in ("H", "V"), message="H for horizontal, V for vertical: ", try_again="H/V: "
        )
        orientation = WallOrientation.HORIZONTAL if orientation_name == "H" else WallOrientation.VERTICAL

        position_name = self.prompt(
            validator=lambda op: self._validate_wall_position(op, orientation),
            message="Enter the wall's top-left-cell position - row, col: ",
            try_again="This position is not valid, enter another: ",
        )
        self.board.place_wall(self.board._get_cell_at(process_position_string(position_name)), orientation)

    def play(self) -> None:
        winner = None
        while winner is None:
            self.reload_state()
            self.reload_screen()

            op = self.prompt(
                validator=lambda op: op in ("M", "W"), message="M for movement, W for wall: ", try_again="M/F: "
            )

            if op == "M":
                winner = self.movement_turn()
            elif op == "W":
                self.wall_turn()

            self.next_turn()

    def check_win(self) -> Optional[Player]:
        for ps in self.player_states:
            if ps.player.position in ps.player.destination:
                print(f"{ps.player.name} Won!")
                return ps.player

    def where_this_goes(self, dirstring: str) -> Position:
        str_rep = {d.value: d for d in self.current_player_state.possible_movements.keys()}
        if dirstring in str_rep.keys():
            d = str_rep[dirstring]
            return self.current_player_state.possible_movements[d]
        return None

    def next_turn(self) -> None:
        self.turn += 1
        self.current_player_index = abs(self.current_player_index - 1)
        self.current_player = self.player_states[self.current_player_index].player
        self.current_player_state = self.player_states[self.current_player_index]

    def reload_state(self) -> None:
        self.board.set_occupation_state({ps.player for ps in self.player_states})
        for ps in self.player_states:
            ps.possible_movements = MovementValidator.get_player_valid_moves(self.board, ps.player)

    def reload_screen(self):
        self.print_game()

    def print_game(self):
        possible_movements = [
            {pm: ps.player.name.lower() for pm in ps.possible_movements.items()} for ps in self.player_states
        ]

        for row in range(self.board.size):
            # Print cells and vertical walls
            for col in range(self.board.size):
                cell = self.board._get_cell_at((row, col))

                # Display cell content (e.g., players)
                if cell.standing_player:
                    print(f" {cell.standing_player.name[0]} ", end="")  # Player's first letter
                else:
                    value = "."
                    for ps in self.player_states:
                        if ps.player.position == (row, col):
                            value = ps.player.name

                    for pm, s in possible_movements[self.current_player_index].items():
                        # print((row, col) == pm[1])
                        # exit
                        if (row, col) == pm[1]:
                            value = s

                    print(f" {value} ", end="")  # Empty cell

                # Check if there is a vertical wall to the right of the cell
                if col < self.board.size - 1:  # Ensure we're not at the rightmost edge
                    vertical_wall_exists = any(
                        wall.orientation == WallOrientation.VERTICAL
                        and (
                            (wall.top_left_cell == self.board._get_cell_at((row, col)))
                            or (row > 0 and wall.top_left_cell == self.board._get_cell_at((row - 1, col)))
                        )
                        for wall in self.board.walls
                    )
                    if vertical_wall_exists:
                        print("|", end="")  # Vertical wall
                    else:
                        print(" ", end="")  # No wall

            print()  # Newline after each row of cells

            # Print horizontal walls (if not on the last row)
            if row < self.board.size - 1:
                for col in range(self.board.size):
                    horizontal_wall_exists = any(
                        wall.orientation == WallOrientation.HORIZONTAL
                        and (
                            (wall.top_left_cell == self.board._get_cell_at((row, col)))
                            or (col > 0 and wall.top_left_cell == self.board._get_cell_at((row, col - 1)))
                        )
                        for wall in self.board.walls
                    )
                    if horizontal_wall_exists:
                        print("---", end="")  # Horizontal wall
                    else:
                        print("   ", end="")  # No wall

                    # Add spacing between columns
                    if col < self.board.size - 1:
                        print(" ", end="")

                print()  # Newline after each row of walls
        print(f"{self.current_player.name}'s turn")
