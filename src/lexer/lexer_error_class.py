from enum import Enum
from lexer.token_type_enum import TokenType


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
        invalid_token: TokenType,
    ):
        self.type = error_type
        self.invalid_token = invalid_token
        self.message = f"[LEXER ERROR - {error_type.name}]: {error_type.value} at line {invalid_token.position.line}, column {invalid_token.position.column}: {invalid_token.value}"
        super().__init__(self.message)

    def __str__(self):
        return self.message
