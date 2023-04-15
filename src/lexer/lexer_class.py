from lexer.helpers import (
    keywords,
    maybe_two_char_token,
    single_char_tokens,
    two_char_token,
)
from lexer.token_class import Token
from lexer.token_type_enum import TokenType
from utils.position_class import Position
from utils.stream_provider_class import StreamProvider


def is_identifier_first_char(char: str) -> bool:
    return char.isalpha() or char == "_"


def is_identifier_char(char: str) -> bool:
    return is_identifier_first_char(char) or char.isdigit()


def is_number(char: str) -> bool:
    return char.isdigit()


class Lexer:
    def __init__(self, stream_provider: StreamProvider):
        self.stream_provider = stream_provider
        self.position = Position(1, 1)
        self.current_char = self.stream_provider.get_char()
        self.current_token: Token = Token(TokenType.T_UNDEFINED, "", self.position)

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        if self.current_char == "#":
            while self.current_char is not None and self.current_char != "\n":
                self.advance()

    def try_build_single_char_operator_token(self) -> bool:
        if self.current_char in single_char_tokens:
            self.current_token = Token(
                single_char_tokens[self.current_char], self.current_char, self.position
            )
            self.advance()
            return True
        return False

    def try_build_two_char_operator_token(self) -> bool:
        if self.current_char not in maybe_two_char_token and self.current_char != "?":
            return False
        prefix = self.current_char
        self.advance()
        if prefix in two_char_token:
            if self.current_char == "=":
                self.current_token = Token(
                    two_char_token[prefix],
                    prefix + self.current_char,
                    self.position,
                )
                self.advance()
            else:
                self.current_token = Token(
                    maybe_two_char_token[prefix],
                    prefix,
                    self.position,
                )
        else:
            if self.current_char == ".":
                self.current_token = Token(
                    TokenType.T_NULLABLE_ACCESS,
                    prefix + self.current_char,
                    self.position,
                )
                self.advance()
            else:
                self.current_token = Token(TokenType.T_OPTIONAL, prefix, self.position)
        return True

    def try_build_indetifier_or_keyword_token(self) -> bool:
        if is_identifier_first_char(self.current_char):
            identifier_or_keyword = self.current_char
            self.advance()
            while is_identifier_char(self.current_char):
                identifier_or_keyword += self.current_char
                self.advance()
            if identifier_or_keyword in keywords:
                self.current_token = Token(
                    keywords[identifier_or_keyword],
                    identifier_or_keyword,
                    self.position,
                )
            else:
                self.current_token = Token(
                    TokenType.T_IDENTIFIER, identifier_or_keyword, self.position
                )
            return True
        return False

    def try_build_number_token(self) -> bool:
        if not is_number(self.current_char):
            return False
        temp_string = ""
        while is_number(self.current_char):
            temp_string += self.current_char
            self.advance()
        if self.current_char == ".":
            self.advance()
            if not is_number(self.current_char):
                raise Exception("Number is not built properly")
            while is_number(self.current_char):
                temp_string += self.current_char
                self.advance()
            self.current_token = Token(
                TokenType.T_FLOAT_LITERAL, float(temp_string), self.position
            )
        else:
            self.current_token = Token(
                TokenType.T_INT_LITERAL, int(temp_string), self.position
            )
        return True

    def try_build_string_token(self) -> bool:
        if self.current_char != '"':
            return False
        self.advance()
        temp_string = ""
        while self.current_char != '"':
            temp_string += self.current_char
            self.advance()
        self.current_token = Token(
            TokenType.T_STRING_LITERAL, temp_string, self.position
        )
        self.advance()
        return True

    def build_next_token(self):
        self.skip_whitespace()
        self.skip_comment()
        if self.current_char is None:
            self.current_token = Token(TokenType.T_EOF, "", self.position)
            return
        if self.try_build_single_char_operator_token():
            return
        if self.try_build_two_char_operator_token():
            return
        if self.try_build_indetifier_or_keyword_token():
            return
        if self.try_build_number_token():
            return
        if self.try_build_string_token():
            return
        raise Exception("Unknown token")

    def advance(self):
        if self.current_char == "\n":
            while self.current_char == "\n":
                self.position.column = 0
                self.position.line += 1
                self.current_char = self.stream_provider.get_char()
        else:
            self.position.column += 1
            self.current_char = self.stream_provider.get_char()
