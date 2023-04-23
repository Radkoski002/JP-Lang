import io
import pytest

from lexer.token_type_enum import TokenType
from src.lexer.config import LEXER_CONFIG
from src.lexer.lexer_class import Lexer
from src.lexer.lexer_error_class import LEXER_ERROR_TYPES
from src.utils.error_handler_class import ErrorHandler


def test_init():
    error_handler = ErrorHandler()
    with io.StringIO("") as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
    assert lexer.current_token.type == TokenType.T_UNDEFINED
    assert lexer.current_token.position.line == 1
    assert lexer.current_token.position.column == 1


@pytest.mark.parametrize(
    "expected_token, input, expected_value",
    [
        (TokenType.T_INT_LITERAL, "1", 1),
        (TokenType.T_INT_LITERAL, "123", 123),
        (TokenType.T_INT_LITERAL, "99999", 99999),
        (TokenType.T_FLOAT_LITERAL, "0.1", 0.1),
        (TokenType.T_FLOAT_LITERAL, "1.1", 1.1),
        (TokenType.T_FLOAT_LITERAL, "1.00001", 1.00001),
        (TokenType.T_STRING_LITERAL, '"string"', "string"),
        (TokenType.T_STRING_LITERAL, r'"string \n"', "string \n"),
        (TokenType.T_STRING_LITERAL, r'"string \t"', "string \t"),
        (TokenType.T_STRING_LITERAL, r'"\"string\""', '"string"'),
        (TokenType.T_RETURN, "return", "return"),
        (TokenType.T_BREAK, "break", "break"),
        (TokenType.T_CONTINUE, "continue", "continue"),
        (TokenType.T_IF, "if", "if"),
        (TokenType.T_ELIF, "elif", "elif"),
        (TokenType.T_ELSE, "else", "else"),
        (TokenType.T_WHILE, "while", "while"),
        (TokenType.T_FOR, "for", "for"),
        (TokenType.T_TRUE, "true", "true"),
        (TokenType.T_FALSE, "false", "false"),
        (TokenType.T_NULL, "null", "null"),
        (TokenType.T_PLUS, "+", "+"),
        (TokenType.T_MINUS, "-", "-"),
        (TokenType.T_MULTIPLY, "*", "*"),
        (TokenType.T_DIVIDE, "/", "/"),
        (TokenType.T_MODULO, "%", "%"),
        (TokenType.T_ASSIGN, "=", "="),
        (TokenType.T_ASSIGN_PLUS, "+=", "+="),
        (TokenType.T_ASSIGN_MINUS, "-=", "-="),
        (TokenType.T_ASSIGN_MULTIPLY, "*=", "*="),
        (TokenType.T_ASSIGN_DIVIDE, "/=", "/="),
        (TokenType.T_ASSIGN_MODULO, "%=", "%="),
        (TokenType.T_GREATER, ">", ">"),
        (TokenType.T_LESS, "<", "<"),
        (TokenType.T_GREATER_EQUAL, ">=", ">="),
        (TokenType.T_LESS_EQUAL, "<=", "<="),
        (TokenType.T_EQUAL, "==", "=="),
        (TokenType.T_NOT_EQUAL, "!=", "!="),
        (TokenType.T_AND, "&", "&"),
        (TokenType.T_OR, "|", "|"),
        (TokenType.T_ACCESS, ".", "."),
        (TokenType.T_NULLABLE_ACCESS, "?.", "?."),
        (TokenType.T_NOT, "!", "!"),
        (TokenType.T_REF, "@", "@"),
        (TokenType.T_TYPE_CHECK, "is", "is"),
        (TokenType.T_LEFT_BRACKET, "(", "("),
        (TokenType.T_RIGHT_BRACKET, ")", ")"),
        (TokenType.T_LEFT_CURLY_BRACKET, "{", "{"),
        (TokenType.T_RIGHT_CURLY_BRACKET, "}", "}"),
        (TokenType.T_IDENTIFIER, "id", "id"),
        (TokenType.T_IDENTIFIER, "test", "test"),
        (TokenType.T_IDENTIFIER, "_test", "_test"),
        (TokenType.T_IDENTIFIER, "_test_", "_test_"),
        (TokenType.T_IDENTIFIER, "_test_123", "_test_123"),
        (TokenType.T_IDENTIFIER, "test_test", "test_test"),
        (TokenType.T_IDENTIFIER, "test_test123", "test_test123"),
        (TokenType.T_SEMICOLON, ";", ";"),
        (TokenType.T_COMMA, ",", ","),
        (TokenType.T_COLON, ":", ":"),
        (TokenType.T_OPTIONAL, "?", "?"),
        (TokenType.T_COMMENT, "# comment", "# comment"),
    ],
)
def test_if_valid_tokens(input, expected_token, expected_value):
    error_handler = ErrorHandler()
    with io.StringIO(input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        lexer.build_next_token()
    assert lexer.current_token.type == expected_token
    assert lexer.current_token.value == expected_value
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
        # Non existing escape
        (r'"\1\2\3\4"', ""),
        (r'"a\1\2\3\4b"', "ab"),
    ],
)
def test_sting_escape(input, expected_value):
    error_handler = ErrorHandler()
    with io.StringIO(input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        lexer.build_next_token()
    assert lexer.current_token.type == TokenType.T_STRING_LITERAL
    assert lexer.current_token.value == expected_value


@pytest.mark.parametrize(
    "input, line, column",
    [
        # basic
        ("", 1, 1),
        (" ", 1, 2),
        # \n
        ("\n", 2, 1),
        ("\nb", 2, 2),
        ("a\n", 2, 1),
        ("\n\n\n", 4, 1),
        ("a\nb", 2, 2),
        # \r
        ("\r", 2, 1),
        ("\rb", 2, 2),
        ("a\r", 2, 1),
        ("\r\r\r", 4, 1),
        ("a\rb", 2, 2),
        # \n\r
        ("\n\r", 2, 1),
        ("\n\rb", 2, 2),
        ("a\n\r", 2, 1),
        ("a\n\rb", 2, 2),
        ("\n\r \n\r \n\r", 4, 1),
        # \r\n
        ("\r\n", 2, 1),
        ("\r\nb", 2, 2),
        ("a\r\n", 2, 1),
        ("a\r\nb", 2, 2),
        ("\r\n \r\n \r\n", 4, 1),
        # \n with another escaping sign
        ("\n \r", 2, 4),
        ("\n \n\r", 2, 5),
        ("\n \r\n", 2, 5),
        # \r with another escaping sign
        ("\r \n", 2, 4),
        ("\r \n\r", 2, 5),
        ("\r \r\n", 2, 5),
        # \r\n with another escaping sign
        ("\r\n \n", 2, 4),
        ("\r\n \r", 2, 4),
        ("\r\n \n\r", 2, 5),
        # \n\r with another escaping sign
        ("\n\r \r\n", 2, 5),
        ("\n\r \n", 2, 4),
        ("\n\r \r", 2, 4),
        # comments and whitespaces combos
        ("#test", 1, 6),
        ("#test ", 1, 7),
        (" #test", 1, 7),
        ("#test\n", 2, 1),
        ("#test \n", 2, 1),
        ("#test\n ", 2, 2),
        (" #test\n", 2, 1),
        ("\n#test", 2, 6),
        ("\n #test", 2, 7),
        ("\n#test ", 2, 7),
        (" \n#test", 2, 6),
        ("\n#test\n", 3, 1),
        ("#test\n#test", 2, 6),
        ("#test\n#test\n#test", 3, 6),
        ("\n#test\n#test\n", 4, 1),
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


@pytest.mark.parametrize(
    "input, error_value, error_type",
    [
        # invalid numbers
        ("01", "0", LEXER_ERROR_TYPES.LEADING_ZEROS),
        ("007", "00", LEXER_ERROR_TYPES.LEADING_ZEROS),
        ("00", "00", LEXER_ERROR_TYPES.LEADING_ZEROS),
        ("00000000", "00000000", LEXER_ERROR_TYPES.LEADING_ZEROS),
        ("00000000.0000000", "00000000", LEXER_ERROR_TYPES.LEADING_ZEROS),
        ("1.", "1.", LEXER_ERROR_TYPES.INVALID_FLOAT),
        ("11111111.", "11111111.", LEXER_ERROR_TYPES.INVALID_FLOAT),
        (
            "1" * LEXER_CONFIG.MAX_NUM_LENGTH.value + "1",
            "1" * LEXER_CONFIG.MAX_NUM_LENGTH.value,
            LEXER_ERROR_TYPES.TOO_LONG_NUMBER,
        ),
        (
            "1" * 256,
            "1" * LEXER_CONFIG.MAX_NUM_LENGTH.value,
            LEXER_ERROR_TYPES.TOO_LONG_NUMBER,
        ),
        (
            "1" * (LEXER_CONFIG.MAX_NUM_LENGTH.value - 2) + "." + ("1" * 3),
            "1" * (LEXER_CONFIG.MAX_NUM_LENGTH.value - 2) + "." + ("1" * 2),
            LEXER_ERROR_TYPES.TOO_LONG_NUMBER,
        ),
        (
            "1" * LEXER_CONFIG.MAX_NUM_LENGTH.value + ".1",
            "1" * LEXER_CONFIG.MAX_NUM_LENGTH.value + ".",
            LEXER_ERROR_TYPES.TOO_LONG_NUMBER,
        ),
        # too long id
        (
            "a" * LEXER_CONFIG.MAX_IDENTIFIER_LENGTH.value + "a",
            "a" * LEXER_CONFIG.MAX_IDENTIFIER_LENGTH.value,
            LEXER_ERROR_TYPES.TOO_LONG_ID,
        ),
        (
            "a" * 256,
            "a" * LEXER_CONFIG.MAX_IDENTIFIER_LENGTH.value,
            LEXER_ERROR_TYPES.TOO_LONG_ID,
        ),
        # unterminated string
        (r'"asljkfalsk', r'"asljkfalsk', LEXER_ERROR_TYPES.UNTERMINATED_STRING),
        (
            r'"asljkfalsk \r test = 1',
            '"asljkfalsk \r test = 1',
            LEXER_ERROR_TYPES.UNTERMINATED_STRING,
        ),
        # \n with another escaping sign
        ("\n \r", "\r", LEXER_ERROR_TYPES.INVALID_EOL),
        ("\n \n\r", "\n\r", LEXER_ERROR_TYPES.INVALID_EOL),
        ("\n \r\n", "\r\n", LEXER_ERROR_TYPES.INVALID_EOL),
        # \r with another escaping sign
        ("\r \n", "\n", LEXER_ERROR_TYPES.INVALID_EOL),
        ("\r \n\r", "\n\r", LEXER_ERROR_TYPES.INVALID_EOL),
        ("\r \r\n", "\r\n", LEXER_ERROR_TYPES.INVALID_EOL),
        # \r\n with another escaping sign
        ("\r\n \n", "\n", LEXER_ERROR_TYPES.INVALID_EOL),
        ("\r\n \r", "\r", LEXER_ERROR_TYPES.INVALID_EOL),
        ("\r\n \n\r", "\n\r", LEXER_ERROR_TYPES.INVALID_EOL),
        # \n\r with another escaping sign
        ("\n\r \r\n", "\r\n", LEXER_ERROR_TYPES.INVALID_EOL),
        ("\n\r \n", "\n", LEXER_ERROR_TYPES.INVALID_EOL),
        ("\n\r \r", "\r", LEXER_ERROR_TYPES.INVALID_EOL),
        # unexpected tokens
        ("[", "[", LEXER_ERROR_TYPES.UNKNOWN_TOKEN),
        ("]", "]", LEXER_ERROR_TYPES.UNKNOWN_TOKEN),
        ("^", "^", LEXER_ERROR_TYPES.UNKNOWN_TOKEN),
        ("$", "$", LEXER_ERROR_TYPES.UNKNOWN_TOKEN),
    ],
)
def test_error_handling(input, error_value, error_type):
    error_handler = ErrorHandler()
    with io.StringIO(input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        lexer.build_next_token()
    assert error_handler.has_errors()
    for error in error_handler.errors:
        assert error.type.name == error_type.name
        assert error.invalid_token.type == TokenType.T_UNDEFINED
        assert error.invalid_token.value == error_value
