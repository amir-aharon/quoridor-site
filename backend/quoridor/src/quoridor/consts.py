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
    Direction.LEFT: (1, 0),
}


class WallOrientation(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
