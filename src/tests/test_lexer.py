import pytest

from lexer.lexer_class import Lexer
from lexer.token_type_enum import TokenType
from utils.stream_provider_class import StreamProvider


def test_init():
    stream_provider = StreamProvider("", False)
    lexer = Lexer(stream_provider)
    assert lexer.current_token.type == TokenType.T_UNDEFINED
    assert lexer.current_token.position.line == 1
    assert lexer.current_token.position.column == 1


@pytest.mark.parametrize(
    "expected_token, input",
    [
        (TokenType.T_INT_LITERAL, "1"),
        (TokenType.T_INT_LITERAL, "123"),
        (TokenType.T_INT_LITERAL, "99999"),
        (TokenType.T_FLOAT_LITERAL, "1.1"),
        (TokenType.T_FLOAT_LITERAL, "1.00001"),
        (TokenType.T_STRING_LITERAL, '"string"'),
        (TokenType.T_RETURN, "return"),
        (TokenType.T_BREAK, "break"),
        (TokenType.T_CONTINUE, "continue"),
        (TokenType.T_IF, "if"),
        (TokenType.T_ELIF, "elif"),
        (TokenType.T_ELSE, "else"),
        (TokenType.T_WHILE, "while"),
        (TokenType.T_FOR, "for"),
        (TokenType.T_TRUE, "true"),
        (TokenType.T_FALSE, "false"),
        (TokenType.T_NULL, "null"),
        (TokenType.T_PLUS, "+"),
        (TokenType.T_MINUS, "-"),
        (TokenType.T_MULTIPLY, "*"),
        (TokenType.T_DIVIDE, "/"),
        (TokenType.T_MODULO, "%"),
        (TokenType.T_ASSIGN, "="),
        (TokenType.T_ASSIGN_PLUS, "+="),
        (TokenType.T_ASSIGN_MINUS, "-="),
        (TokenType.T_ASSIGN_MULTIPLY, "*="),
        (TokenType.T_ASSIGN_DIVIDE, "/="),
        (TokenType.T_ASSIGN_MODULO, "%="),
        (TokenType.T_GREATER, ">"),
        (TokenType.T_LESS, "<"),
        (TokenType.T_GREATER_EQUAL, ">="),
        (TokenType.T_LESS_EQUAL, "<="),
        (TokenType.T_EQUAL, "=="),
        (TokenType.T_NOT_EQUAL, "!="),
        (TokenType.T_AND, "&"),
        (TokenType.T_OR, "|"),
        (TokenType.T_ACCESS, "."),
        (TokenType.T_NULLABLE_ACCESS, "?."),
        (TokenType.T_NOT, "!"),
        (TokenType.T_REF, "@"),
        (TokenType.T_TYPE_CHECK, "is"),
        (TokenType.T_LEFT_BRACKET, "("),
        (TokenType.T_RIGHT_BRACKET, ")"),
        (TokenType.T_LEFT_CURLY_BRACKET, "{"),
        (TokenType.T_RIGHT_CURLY_BRACKET, "}"),
        (TokenType.T_IDENTIFIER, "id"),
        (TokenType.T_IDENTIFIER, "test"),
        (TokenType.T_IDENTIFIER, "_test"),
        (TokenType.T_IDENTIFIER, "_test_"),
        (TokenType.T_IDENTIFIER, "_test_123"),
        (TokenType.T_IDENTIFIER, "test_test"),
        (TokenType.T_IDENTIFIER, "test_test123"),
        (TokenType.T_SEMICOLON, ";"),
        (TokenType.T_COMMA, ","),
        (TokenType.T_COLON, ":"),
        (TokenType.T_OPTIONAL, "?"),
    ],
)
def test_if_valid_tokens(input, expected_token):
    stream_provider = StreamProvider(input, False)
    lexer = Lexer(stream_provider)
    lexer.build_next_token()
    assert lexer.current_token.type == expected_token
    assert lexer.current_token.position.line == 1
    assert lexer.current_token.position.column == len(input) + 1
