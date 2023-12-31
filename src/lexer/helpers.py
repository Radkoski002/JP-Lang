from typing import Dict

from lexer.token_type_enum import TokenType

single_char_tokens: Dict[str, TokenType] = {
    "(": TokenType.T_LEFT_BRACKET,
    ")": TokenType.T_RIGHT_BRACKET,
    "{": TokenType.T_LEFT_CURLY_BRACKET,
    "}": TokenType.T_RIGHT_CURLY_BRACKET,
    ",": TokenType.T_COMMA,
    ";": TokenType.T_SEMICOLON,
    "&": TokenType.T_AND,
    "|": TokenType.T_OR,
    "@": TokenType.T_REF,
    ":": TokenType.T_COLON,
    ".": TokenType.T_ACCESS,
}

keywords: Dict[str, TokenType] = {
    # Conditional statements
    "if": TokenType.T_IF,
    "else": TokenType.T_ELSE,
    "elif": TokenType.T_ELIF,
    "while": TokenType.T_WHILE,
    "for": TokenType.T_FOR,
    # Functions
    "break": TokenType.T_BREAK,
    "continue": TokenType.T_CONTINUE,
    "return": TokenType.T_RETURN,
    # Literals
    "true": TokenType.T_TRUE,
    "false": TokenType.T_FALSE,
    "null": TokenType.T_NULL,
    # Operators
    "is": TokenType.T_TYPE_CHECK,
    "try": TokenType.T_TRY,
    "catch": TokenType.T_CATCH,
    "throw": TokenType.T_THROW,
}

maybe_two_char_token: Dict[str, tuple] = {
    "+": ("=", TokenType.T_PLUS, TokenType.T_ASSIGN_PLUS),
    "-": ("=", TokenType.T_MINUS, TokenType.T_ASSIGN_MINUS),
    "*": ("=", TokenType.T_MULTIPLY, TokenType.T_ASSIGN_MULTIPLY),
    "/": ("=", TokenType.T_DIVIDE, TokenType.T_ASSIGN_DIVIDE),
    "%": ("=", TokenType.T_MODULO, TokenType.T_ASSIGN_MODULO),
    "!": ("=", TokenType.T_NOT, TokenType.T_NOT_EQUAL),
    "=": ("=", TokenType.T_ASSIGN, TokenType.T_EQUAL),
    ">": ("=", TokenType.T_GREATER, TokenType.T_GREATER_EQUAL),
    "<": ("=", TokenType.T_LESS, TokenType.T_LESS_EQUAL),
    "?": (".", TokenType.T_OPTIONAL, TokenType.T_NULLABLE_ACCESS),
}

escaped_chars: Dict[str, str] = {
    "t": "\t",
    "r": "\r",
    "n": "\n",
    "\\": "\\",
    "'": "'",
    '"': '"',
    "0": "\0",
    "b": "\b",
    "f": "\f",
    "v": "\v",
}
