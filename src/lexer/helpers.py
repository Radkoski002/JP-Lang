from typing import Dict

from token_type_enum import TokenType

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
}

keywords: Dict[str, TokenType] = {
    # Conditional statements
    "if": TokenType.T_IF,
    "else": TokenType.T_ELSE,
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
}
