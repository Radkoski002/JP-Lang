from enum import Enum
from utils.position_class import Position


class LEXER_ERROR_TYPES(Enum):
    TOO_LONG_ID = "Identifier is too long"
    TOO_LONG_NUMBER = "Number is too long"
    INVALID_FLOAT = "Expected digit after decimal point"
    LEADING_ZEROS = "Number cannot have leading zeros"
    UNTERMINATED_STRING = "Unterminated string"
    INVALID_EOL = "Invalid end of line character"
    UNKNOWN_TOKEN = "Unknown token"


class LexerError(Exception):
    def __init__(
        self,
        error_type: LEXER_ERROR_TYPES,
        invalid_value: str | int | float,
        position: Position,
    ):
        self.type = error_type
        self.invalid_value = invalid_value
        self.position = position
        self.message = f"[LEXER ERROR - {error_type.name}]: {error_type.value} at line {position.line}, column {position.column}: {invalid_value}"
        super().__init__(self.message)

    def __str__(self):
        return self.message
