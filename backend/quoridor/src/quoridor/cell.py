from typing import Optional
from pydantic import BaseModel

from quoridor.consts import Position
from quoridor.player import Player


class Cell(BaseModel):
    position: Position
    standing_player: Optional[Player] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def is_occupied(self) -> bool:
        return self.standing_player is not None

    def remove_player(self) -> None:
        self.standing_player = None

    def place_player(self, player: Player) -> None:
        self.standing_player = player
