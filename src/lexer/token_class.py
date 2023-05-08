from lexer.token_type_enum import TokenType
from utils.position_class import Position


class Token:
    def __init__(
        self,
        token_type: TokenType,
        value: str | int | float,
        position: Position,
    ):
        self.type = token_type
        self.value = value
        self.position = position
