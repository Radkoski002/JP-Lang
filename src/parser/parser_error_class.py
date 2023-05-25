from enum import Enum
from utils.position_class import Position


class PARSER_ERROR_TYPES(Enum):
    MISSING_BLOCK_START = "Missing block start"
    MISSING_BLOCK_END = "Missing block end"
    MISSING_OPENING_BRACKET = "Missing opening bracket"
    MISSING_CLOSING_BRACKET = "Missing closing bracket"
    MISSING_FOR_LOOP_VARIABLE = "Missing variable declaration in for loop"
    MISSING_FOR_LOOP_ITERABLE = "Missing iterable in for loop"
    MISSING_FOR_LOOP_COLON = "Missing colon in for loop"
    MISSING_CONDITIONAL_EXPRESSION = "Missing conditional expression"
    MISSING_TYPE_NAME = "Missing type name"
    MISSING_ARGUMENT = "Missing argument after comma"
    MISSING_EXPRESSION = "Missing expression"
    MISSING_SEMICOLON = "Missing semicolon"
    MISSING_CATCH_KEYWORD = "Missing catch keyword"
    MISSING_ERROR_TYPE = "Missing error type"
    MISSING_ERROR_VARIABLE = "Missing error variable"
    MISSING_PARAMETER = "Missing parameter"
    INVALID_PARAMETER_VALUE = "Invalid parameter value"
    FUNCTION_ALREADY_EXIST = "Function already exist"
    PARAMETER_ALREADY_EXIST = "Parameter already exist"


class ParserError(Exception):
    def __init__(
        self,
        error_type: PARSER_ERROR_TYPES,
        position: Position,
    ):
        self.type = error_type
        self.position = position
        self.message = f"[PARSER ERROR - {error_type.name}]: {error_type.value} at line {position.line}, column {position.column}"
        super().__init__(self.message)

    def __str__(self):
        return self.message
