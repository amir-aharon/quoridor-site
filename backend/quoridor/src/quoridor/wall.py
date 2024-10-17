from pydantic import BaseModel

from quoridor.cell import Cell
from quoridor.consts import WallOrientation


class Wall(BaseModel):
    top_left_cell: Cell
    orientation: WallOrientation

    class Config:
        arbitrary_types_allowed = True

    def __eq__(self, other):
        if not isinstance(other, Wall):
            return False
        return self.top_left_cell == other.top_left_cell and self.orientation == other.orientation

    def __hash__(self):
        return hash((self.top_left_cell.position, self.orientation))
