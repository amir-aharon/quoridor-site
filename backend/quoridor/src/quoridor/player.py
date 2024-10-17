from pydantic import BaseModel, Field

from quoridor.consts import MOVEMENT_VECTORS, Direction, Position


class Player(BaseModel):
    name: str
    position: Position
    destination: set[Position] = Field(default={})
    wall_count: int = Field(default=10)

    class Config:
        arbitrary_types_allowed = True

    def has_reached_destination(self) -> bool:
        return self.position in self.destination

    def move(self, direction: Direction, skip: bool = False) -> None:
        row_change, col_change = MOVEMENT_VECTORS[direction]
        self.position = (self.row + row_change, self.column + col_change)

        if skip:
            self.position = (self.position[0] + row_change, self.position[1] + col_change)

    def jump(self, position: Position) -> None:
        self.position = position

    def use_wall(self) -> None:
        if self.wall_count > 0:
            self.wall_count -= 1

    def __hash__(self) -> int:
        return hash((self.name, self.position, self.wall_count))
