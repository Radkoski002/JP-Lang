from token_type_enum import TokenType


class Token:
    def __init__(self, type: TokenType, value: str | float):
        self.type = type
        self.value = value
