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
