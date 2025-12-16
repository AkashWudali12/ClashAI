from pydantic import BaseModel
from typing import Annotated

class Game:
    pass

class Troop(BaseModel):

    name: str # i.e. witch

    """
        Position is displayed on 0 to 1 scale
        1 is the end of the horizontal or vertical part of the screen
        pos_on_screen = length_of_arena_on_screen * pos
    """
    x_position: Annotated[float, {"min_value": 0, "max_value": 1}]
    y_position: Annotated[float, {"min_value": 0, "max_value": 1}]