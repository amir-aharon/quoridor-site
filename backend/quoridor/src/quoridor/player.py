from pydantic import BaseModel, Field

from backend.quoridor.src.quoridor.consts import MOVEMENT_VECTORS, Direction, Position


class Player(BaseModel):
    name: str
    position: Position
    wall_count: int = Field(default=10)

    class Config:
        arbitrary_types_allowed = True

    def move(self, direction: Direction, skip: bool = False) -> None:
        row_change, col_change = MOVEMENT_VECTORS[direction]
        self.position = (self.row + row_change, self.column + col_change)

        if skip:
            self.position = (self.position[0] + row_change, self.position[1] + col_change)

    def use_wall(self) -> None:
        if self.wall_count > 0:
            self.wall_count -= 1
