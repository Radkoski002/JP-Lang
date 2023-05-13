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
end_of_line_chars = ["\n", "\r"]


class Lexer:
    def __init__(self, stream_provider: TextIOWrapper, error_handler: ErrorHandler):
        self.stream_provider: TextIOWrapper = stream_provider
        self.current_position: Position = Position(1, 1)
        self.current_token_position: Position = self.current_position
        self.current_char: str = self.stream_provider.read(1)
        self.end_of_line_sequence: str | None = None
        self.error_handler: ErrorHandler = error_handler

    def __add_error(self, error_type: LEXER_ERROR_TYPES, token_value: str) -> None:
        self.error_handler.add_error(
            LexerError(error_type, token_value, self.current_position)
        )
        self.__advance()

    def __skip_whitespace(self) -> bool:
        if not self.current_char.isspace():
            return False
        while self.current_char.isspace():
            self.__advance()
        return True

    def __skip_comment(self) -> bool:
        if not self.current_char == "#":
            return False
        current_line = self.current_position.line
        while (
            self.current_char not in end_of_file_chars
            and self.current_position.line == current_line
        ):
            self.__advance()
        return True

    def __try_build_single_char_operator_token(self) -> Token | None:
        if token_type := single_char_tokens.get(self.current_char):
            token = Token(
                token_type,
                self.current_char,
                self.current_token_position,
            )
            self.__advance()
            return token
        return None

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

    def __try_build_two_char_operator_token(self) -> Token | None:
        if params := maybe_two_char_token.get(self.current_char):
            prefix = self.current_char
            self.__advance()
            return self.__check_if_two_char_token(*params, prefix=prefix)
        return None

    def __try_build_indetifier_or_keyword_token(self) -> Token | None:
        if not is_identifier_first_char(self.current_char):
            return None
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
            return Token(
                keywords[identifier_or_keyword],
                identifier_or_keyword,
                self.current_token_position,
            )
        else:
            return Token(
                TokenType.T_IDENTIFIER,
                identifier_or_keyword,
                self.current_token_position,
            )

    def __try_build_number_token(self) -> Token | None:
        if not is_digit(self.current_char):
            return False
        zero = ord("0")
        temp_value = ord(self.current_char) - zero
        number_of_digits = 1
        self.__advance()
        if temp_value != 0:
            while is_digit(self.current_char):
                if (
                    number_of_digits := number_of_digits + 1
                ) > LEXER_CONFIG.MAX_NUM_LENGTH.value:
                    self.__add_error(LEXER_ERROR_TYPES.TOO_LONG_NUMBER, f"{temp_value}")
                    break
                temp_value = 10 * temp_value + ord(self.current_char) - zero
                self.__advance()

        if not self.current_char == ".":
            return Token(
                TokenType.T_INT_LITERAL, temp_value, self.current_token_position
            )

        decimal = 0
        self.__advance()
        if not is_digit(self.current_char):
            self.__add_error(LEXER_ERROR_TYPES.INVALID_FLOAT, f"{temp_value}.")
            return True
        while is_digit(self.current_char):
            if number_of_digits == LEXER_CONFIG.MAX_NUM_LENGTH.value:
                self.__add_error(
                    LEXER_ERROR_TYPES.TOO_LONG_NUMBER,
                    f"{temp_value / 10 ** decimal if decimal != 0 else temp_value}",
                )
                break
            temp_value = 10 * temp_value + ord(self.current_char) - zero
            decimal += 1
            number_of_digits += 1
            self.__advance()
        temp_value /= 10**decimal
        return Token(TokenType.T_FLOAT_LITERAL, temp_value, self.current_token_position)

    def __check_escape_char_in_string(self) -> str:
        self.__advance()
        if escaped_char := escaped_chars.get(self.current_char):
            temp_char = escaped_char
        else:
            # TODO Add edge cases handling
            temp_char = self.current_char
        return temp_char

    def __try_build_string_token(self) -> Token | None:
        if self.current_char != '"':
            return None
        self.__advance()
        temp_string = []
        temp_char = ""
        while self.current_char != '"':
            if self.current_char in end_of_file_chars:
                self.__add_error(
                    LEXER_ERROR_TYPES.UNTERMINATED_STRING, "".join(temp_string)
                )
                break
            if self.current_char == "\\":
                temp_char = self.__check_escape_char_in_string()
            else:
                temp_char = self.current_char
            temp_string.append(temp_char)
            self.__advance()
        self.__advance()
        return Token(
            TokenType.T_STRING_LITERAL,
            "".join(temp_string),
            self.current_token_position,
        )

    def __try_build_comment_token(self) -> Token | None:
        if self.current_char != "#":
            return None
        current_line = self.current_position.line
        temp_comment = []
        self.__advance()
        while (
            self.current_char not in end_of_file_chars
            and self.current_position.line == current_line
        ):
            temp_comment.append(self.current_char)
            self.__advance()
        return Token(
            TokenType.T_COMMENT, "".join(temp_comment), self.current_token_position
        )

    def __go_one_char_forward(self) -> None:
        self.current_position.column += 1
        self.current_char = self.stream_provider.read(1)

    def __check_end_of_line(self) -> None:
        escape_char = self.current_char
        valid_second_char = "\n" if self.current_char == "\r" else "\r"
        self.__go_one_char_forward()
        if self.current_char == valid_second_char:
            escape_char += valid_second_char
            self.__go_one_char_forward()
        if not self.end_of_line_sequence:
            self.end_of_line_sequence = escape_char
        elif self.end_of_line_sequence != escape_char:
            self.__add_error(LEXER_ERROR_TYPES.INVALID_EOL, escape_char)
            return
        self.current_position.line += 1
        self.current_position.column = 1

    def __advance(self) -> None:
        if self.current_char in end_of_line_chars:
            self.__check_end_of_line()
        else:
            self.__go_one_char_forward()

    def __try_build_token(self) -> Token | None:
        return (
            self.__try_build_single_char_operator_token()
            or self.__try_build_two_char_operator_token()
            or self.__try_build_indetifier_or_keyword_token()
            or self.__try_build_number_token()
            or self.__try_build_string_token()
            or self.__try_build_comment_token()
        )

    def __check_if_token_is_valid(self) -> Token:
        self.current_token_position = Position(
            self.current_position.line, self.current_position.column
        )
        if self.current_char in end_of_file_chars:
            return Token(TokenType.T_EOF, "", self.current_token_position)

        if token := self.__try_build_token():
            return token
        self.__add_error(LEXER_ERROR_TYPES.UNKNOWN_TOKEN, self.current_char)
        return Token(
            TokenType.T_UNDEFINED, self.current_char, self.current_token_position
        )

    def build_next_token(self) -> Token:
        while self.__skip_whitespace():
            pass
        return self.__check_if_token_is_valid()

    def build_next_token_without_comments(self) -> Token:
        while self.__skip_whitespace() or self.__skip_comment():
            pass
        return self.__check_if_token_is_valid()
