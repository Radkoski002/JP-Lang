from io import TextIOWrapper
from utils.error_handler_class import ErrorHandler
from lexer.config import LEXER_CONFIG
from lexer.helpers import (
    escaped_chars,
    keywords,
    maybe_two_char_token,
    single_char_tokens,
)
from lexer.lexer_error_class import LEXER_ERROR_TYPES, LexerError
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
        self.error_handler: ErrorHandler = error_handler

    def __add_error(self, error_type: LEXER_ERROR_TYPES, token_value: str) -> None:
        self.current_token = Token(
            TokenType.T_UNDEFINED, token_value, self.current_token_position
        )
        self.error_handler.add_error(LexerError(error_type, self.current_token))
        self.__advance()

    def __check_end_of_line(self) -> bool:
        if self.current_char not in ["\n", "\r"]:
            return False
        escape_char = self.current_char
        valid_second_char = "\n" if self.current_char == "\r" else "\r"
        self.__advance()
        if self.current_char == valid_second_char:
            escape_char += valid_second_char
            self.__advance()
        if not self.end_of_line_char:
            self.end_of_line_char = escape_char
        elif self.end_of_line_char != escape_char:
            self.__add_error(LEXER_ERROR_TYPES.INVALID_EOL, escape_char)
            return True
        self.position.line += 1
        self.position.column = 1
        return True

    def __skip_whitespace(self) -> bool:
        if self.current_char in end_of_file_chars or not self.current_char.isspace():
            return False
        while (
            self.current_char not in end_of_file_chars and self.current_char.isspace()
        ):
            if self.__check_end_of_line():
                pass
            else:
                self.__advance()
        return True

    def __skip_comment(self) -> bool:
        if not self.current_char == "#":
            return False
        while self.current_char not in end_of_file_chars and self.current_char != "\n":
            self.__advance()
        return True

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

    def __check_if_two_char_token(
        self,
        expected_char: str,
        one_char_token: TokenType,
        two_char_token: TokenType,
        prefix: str,
    ) -> Token:
        if self.current_char == expected_char:
            self.__advance()
            return Token(
                two_char_token,
                prefix + expected_char,
                self.current_token_position,
            )
        else:
            return Token(one_char_token, prefix, self.current_token_position)

    def __try_build_two_char_operator_token(self) -> bool:
        if params := maybe_two_char_token.get(self.current_char):
            prefix = self.current_char
            self.__advance()
            self.current_token = self.__check_if_two_char_token(*params, prefix=prefix)
            return True
        return False

    def __try_build_indetifier_or_keyword_token(self) -> bool:
        if not is_identifier_first_char(self.current_char):
            return False
        identifier_or_keyword = [self.current_char]
        self.__advance()
        while is_identifier_char(self.current_char):
            if len(identifier_or_keyword) == LEXER_CONFIG.MAX_IDENTIFIER_LENGTH.value:
                self.__add_error(
                    LEXER_ERROR_TYPES.TOO_LONG_ID, "".join(identifier_or_keyword)
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
        while is_digit(self.current_char):
            if (
                number_of_digits := number_of_digits + 1
            ) > LEXER_CONFIG.MAX_NUM_LENGTH.value:
                self.__add_error(LEXER_ERROR_TYPES.TOO_LONG_NUMBER, f"{temp_value}")
                return True
            temp_value = 10 * temp_value + ord(self.current_char) - zero
            self.__advance()
            if number_of_digits > 1 and 0 < temp_value < 10:
                self.__add_error(
                    LEXER_ERROR_TYPES.LEADING_ZEROS,
                    f"{'0'*(number_of_digits - 1)}",
                )
                return True
        if number_of_digits > 1 and temp_value == 0:
            self.__add_error(
                LEXER_ERROR_TYPES.LEADING_ZEROS,
                f"{'0'*number_of_digits}",
            )
            return True
        if not self.current_char == ".":
            self.current_token = Token(
                TokenType.T_INT_LITERAL, temp_value, self.current_token_position
            )
            return True

        decimal = 0
        self.__advance()
        if number_of_digits + 1 > LEXER_CONFIG.MAX_NUM_LENGTH.value:
            self.__add_error(LEXER_ERROR_TYPES.TOO_LONG_NUMBER, f"{temp_value}.")
            return True
        if not is_digit(self.current_char):
            self.__add_error(LEXER_ERROR_TYPES.INVALID_FLOAT, f"{temp_value}.")
            return True
        while is_digit(self.current_char):
            if (
                number_of_digits := number_of_digits + 1
            ) > LEXER_CONFIG.MAX_NUM_LENGTH.value:
                self.__add_error(
                    LEXER_ERROR_TYPES.TOO_LONG_NUMBER, f"{temp_value / 10 ** decimal}"
                )
                return True
            temp_value = 10 * temp_value + ord(self.current_char) - zero
            decimal += 1
            self.__advance()
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
            if self.current_char in end_of_file_chars:
                self.__add_error(
                    LEXER_ERROR_TYPES.UNTERMINATED_STRING, f'"{temp_string}'
                )
                return True
            if self.current_char == "\\":
                self.__advance()
                if escaped_char := escaped_chars.get(self.current_char):
                    temp_string += escaped_char
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
        while self.__skip_whitespace() or self.__skip_comment():
            pass
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
        self.__add_error(LEXER_ERROR_TYPES.UNKNOWN_TOKEN, self.current_char)
        return True
