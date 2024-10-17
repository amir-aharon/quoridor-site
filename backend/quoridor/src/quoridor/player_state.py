from pydantic import BaseModel, Field
from quoridor.consts import Direction, Position
from quoridor.player import Player


class PlayerState(BaseModel):
    player: Player
    possible_movements: dict[Direction, Position] = Field(default={})
