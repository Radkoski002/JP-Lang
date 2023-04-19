from ast import Dict
from io import TextIOWrapper
from xml.sax import ErrorHandler
from lexer.config import LEXER_CONFIG, LEXER_CONFIG_OPITONS
from lexer.helpers import (
    escaped_chars,
    keywords,
    maybe_two_char_token,
    single_char_tokens,
    two_char_token,
)
from lexer.lexer_error_class import LexerError
from lexer.token_class import Token
from lexer.token_type_enum import TokenType
from utils.position_class import Position


def is_identifier_first_char(char: str) -> bool:
    return char.isalpha() or char == "_"


def is_identifier_char(char: str) -> bool:
    return is_identifier_first_char(char) or char.isdigit()


def is_digit(char: str) -> bool:
    return char.isdecimal()


end_of_file_chars = [None, ""]


class Lexer:
    def __init__(self, stream_provider: TextIOWrapper, error_handler: ErrorHandler):
        self.stream_provider: TextIOWrapper = stream_provider
        self.position: Position = Position(1, 1)
        self.current_token_position: Position = self.position
        self.current_char: str = self.stream_provider.read(1)
        self.current_token: Token = Token(TokenType.T_UNDEFINED, "", self.position)
        self.end_of_line_char: str | None = None
        self.error_handler = error_handler

        self.maybe_two_char_token: Dict[str, TokenType] = {
            "+": TokenType.T_PLUS,
            "-": TokenType.T_MINUS,
            "*": TokenType.T_MULTIPLY,
            "/": TokenType.T_DIVIDE,
            "%": TokenType.T_MODULO,
            "!": TokenType.T_NOT,
            "=": TokenType.T_ASSIGN,
            ">": TokenType.T_GREATER,
            "<": TokenType.T_LESS,
        }

    # TODO add support for raw strings
    def __skip_whitespace(self) -> None:
        while (
            self.current_char not in end_of_file_chars and self.current_char.isspace()
        ):
            if self.current_char == "\n":
                self.__advance()
                if self.current_char == "\r":
                    if self.end_of_line_char is None or self.end_of_line_char == "\n\r":
                        self.end_of_line_char = "\n\r"
                        self.position.line += 1
                        self.position.column = 0
                    elif self.end_of_line_char != "\n\r":
                        self.__add_error("Invalid end of line character")
                    self.__advance()
                else:
                    if self.end_of_line_char is None or self.end_of_line_char == "\n":
                        self.end_of_line_char = "\n"
                        self.position.line += 1
                        self.position.column = 1
                    elif self.end_of_line_char != "\n":
                        self.__add_error("Invalid end of line character")
            elif self.current_char == "\r":
                self.__advance()
                if self.current_char == "\n":
                    if self.end_of_line_char is None or self.end_of_line_char == "\r\n":
                        self.end_of_line_char = "\r\n"
                        self.position.line += 1
                        self.position.column = 0
                    elif self.end_of_line_char != "\r\n":
                        self.__add_error("Invalid end of line character")
                    self.__advance()
                else:
                    self.__add_error("Invalid end of line character")
            else:
                self.__advance()

    # TODO: Make wrapper for this lexer that will skip comments
    def __skip_comment(self) -> None:
        if self.current_char == "#":
            while (
                self.current_char not in end_of_file_chars and self.current_char != "\n"
            ):
                self.__advance()

    # TODO change list of errors to error handler
    def __add_error(self, message: str) -> None:
        self.error_handler.add_error(LexerError(message, self.position))
        self.__advance()

    def __try_build_single_char_operator_token(self) -> bool:
        if token_type := single_char_tokens.get(self.current_char):
            self.current_token = Token(
                token_type,
                self.current_char,
                self.current_token_position,
            )
            self.__advance()
            return True
        return False

    def __try_build_two_char_operator_token(self) -> bool:
        if self.current_char not in maybe_two_char_token and self.current_char != "?":
            return False
        prefix = self.current_char
        self.__advance()
        if prefix in two_char_token:
            if self.current_char == "=":
                self.current_token = Token(
                    two_char_token[prefix],
                    prefix + self.current_char,
                    self.current_token_position,
                )
                self.__advance()
            else:
                self.current_token = Token(
                    maybe_two_char_token[prefix],
                    prefix,
                    self.current_token_position,
                )
        else:
            if self.current_char == ".":
                self.current_token = Token(
                    TokenType.T_NULLABLE_ACCESS,
                    prefix + self.current_char,
                    self.current_token_position,
                )
                self.__advance()
            else:
                self.current_token = Token(
                    TokenType.T_OPTIONAL, prefix, self.current_token_position
                )
        return True

    def __try_build_indetifier_or_keyword_token(self) -> bool:
        if not is_identifier_first_char(self.current_char):
            return False

        identifier_or_keyword = [self.current_char]
        self.__advance()
        while is_identifier_char(self.current_char):
            if (
                len(identifier_or_keyword)
                == LEXER_CONFIG[LEXER_CONFIG_OPITONS.MAX_IDENTIFIER_LENGTH]
            ):
                self.__add_error(
                    f"Identifier too long, max length is {LEXER_CONFIG[LEXER_CONFIG_OPITONS.MAX_IDENTIFIER_LENGTH]}"
                )
                break
            identifier_or_keyword.append(self.current_char)
            self.__advance()
        identifier_or_keyword = "".join(identifier_or_keyword)
        if identifier_or_keyword in keywords:
            self.current_token = Token(
                keywords[identifier_or_keyword],
                identifier_or_keyword,
                self.current_token_position,
            )
        else:
            self.current_token = Token(
                TokenType.T_IDENTIFIER,
                identifier_or_keyword,
                self.current_token_position,
            )
        return True

    def __try_build_number_token(self) -> bool:
        if not is_digit(self.current_char):
            return False
        zero = ord("0")
        temp_value = 0
        number_of_digits = 0
        while (
            is_digit(self.current_char)
            and number_of_digits < LEXER_CONFIG[LEXER_CONFIG_OPITONS.MAX_NUM_LENGTH]
        ):
            temp_value *= 10
            temp_value += ord(self.current_char) - zero
            number_of_digits += 1
            self.__advance()
            if number_of_digits > LEXER_CONFIG[LEXER_CONFIG_OPITONS.MAX_NUM_LENGTH]:
                self.__add_error("Number is too long")
                return False
        if not self.current_char == ".":
            self.current_token = Token(
                TokenType.T_INT_LITERAL, temp_value, self.current_token_position
            )
            return True

        decimal = 0
        self.__advance()
        if not is_digit(self.current_char):
            self.__add_error("Expected digit after decimal point")
            return False
        while is_digit(self.current_char):
            temp_value *= 10
            temp_value += ord(self.current_char) - zero
            decimal += 1
            number_of_digits += 1
            self.__advance()
            if number_of_digits > LEXER_CONFIG[LEXER_CONFIG_OPITONS.MAX_NUM_LENGTH]:
                self.__add_error("Number is too long")
                return False
        temp_value /= 10**decimal
        self.current_token = Token(
            TokenType.T_FLOAT_LITERAL, temp_value, self.current_token_position
        )
        return True

    def __try_build_string_token(self) -> bool:
        if self.current_char != '"':
            return False
        self.__advance()
        temp_string = ""
        while self.current_char != '"':
            if self.current_char is None:
                self.__add_error("Unterminated string")
                return False
            if self.current_char == "\\":
                self.__advance()
                # TODO: Same thing as with two char operators
                if escaped_char := escaped_chars.get(self.current_char):
                    temp_string += escaped_char
                else:
                    self.__add_error("Invalid escape sequence")
            else:
                temp_string += self.current_char
            self.__advance()
        self.current_token = Token(
            TokenType.T_STRING_LITERAL, temp_string, self.current_token_position
        )
        self.__advance()
        return True

    def __advance(self) -> None:
        self.position.column += 1
        self.current_char = self.stream_provider.read(1)

    def build_next_token(self) -> bool:
        self.__skip_whitespace()
        self.__skip_comment()
        self.current_token_position = Position(self.position.line, self.position.column)
        if self.current_char in end_of_file_chars:
            self.current_token = Token(TokenType.T_EOF, "", self.current_token_position)
            return False

        if (
            self.__try_build_single_char_operator_token()
            or self.__try_build_two_char_operator_token()
            or self.__try_build_indetifier_or_keyword_token()
            or self.__try_build_number_token()
            or self.__try_build_string_token()
        ):
            return True
        # FIXME: Throws two errors at once
        self.__add_error(f"Unexpected token: {self.current_char}")
        self.current_token = Token(
            TokenType.T_UNDEFINED, "", self.current_token_position
        )
        self.__advance()
        return True
