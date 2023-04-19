import io
import pytest

from lexer.lexer_class import Lexer
from lexer.token_type_enum import TokenType
from src.utils.error_handler_class import ErrorHandler


def test_init():
    error_handler = ErrorHandler()
    with io.StringIO("") as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
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
        (TokenType.T_STRING_LITERAL, r'"string \n"'),
        (TokenType.T_STRING_LITERAL, r'"string \t"'),
        (TokenType.T_STRING_LITERAL, r'"\"string\""'),
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
    error_handler = ErrorHandler()
    with io.StringIO(input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        lexer.build_next_token()
    assert lexer.current_token.type == expected_token
    assert lexer.current_token.position.line == 1
    assert lexer.current_token.position.column == 1


@pytest.mark.parametrize(
    "input, expected_value",
    [
        (r'"\n"', "\n"),
        (r'"\r"', "\r"),
        (r'"\t"', "\t"),
        (r'"\\"', "\\"),
        (r'"\'"', "'"),
        (r'"\""', '"'),
        (r'"\0"', "\0"),
        (r'"\b"', "\b"),
        (r'"\f"', "\f"),
        (r'"\v"', "\v"),
        (
            r'"test \n test \t test \\ test \r test \' test \" test \0 test \b test \f test \v"',
            "test \n test \t test \\ test \r test ' test \" test \0 test \b test \f test \v",
        ),
    ],
)
def test_sting_escape(input, expected_value):
    error_handler = ErrorHandler()
    with io.StringIO(input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        lexer.build_next_token()
    assert lexer.current_token.type == TokenType.T_STRING_LITERAL
    assert lexer.current_token.value == expected_value


# TODO: Add more tests cases


@pytest.mark.parametrize("input", [("1.1.1")])
def test_error_handling(input):
    error_handler = ErrorHandler()
    with io.StringIO(input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        lexer.build_next_token()
    assert input == input


# TODO: Add more test cases for position checking
# TODO: Add test cases for raw strings
@pytest.mark.parametrize(
    "input, line, column",
    [
        ("", 1, 1),
        (" ", 1, 2),
        ("\n", 2, 1),
        ("a\n", 2, 1),
        ("\n\n\n", 4, 1),
        ("a\nb", 2, 2),
        ("\n\r", 2, 1),
        ("a\n\r", 2, 1),
        ("a\n\rb", 2, 2),
        ("\n\r \n\r \n\r", 4, 1),
        ("\r\n", 2, 1),
        ("a\r\n", 2, 1),
        ("a\r\nb", 2, 2),
        ("\r\n \r\n \r\n", 4, 1),
        ("\n \n\r", 2, 4),
        ("\n \r\n", 2, 4),
        ("\r\n \n", 2, 3),
        ("\r\n \n\r", 2, 4),
        ("\n\r \r\n", 2, 4),
        ("\n\r \n", 2, 3),
    ],
)
def test_current_position(input, line, column):
    error_handler = ErrorHandler()
    with io.StringIO(input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        while lexer.build_next_token():
            pass
    assert lexer.current_token.position.line == line
    assert lexer.current_token.position.column == column
