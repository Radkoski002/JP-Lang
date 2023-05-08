from enum import Enum


class TokenType(Enum):
    # --- Literals ---
    T_INT_LITERAL = "int"
    T_FLOAT_LITERAL = "float"
    T_STRING_LITERAL = "string"

    # --- Keywords ---

    # ------ Functions ------
    T_RETURN = "return"
    T_BREAK = "break"
    T_CONTINUE = "continue"

    # ------ Statements ------
    T_IF = "if"
    T_ELIF = "elif"
    T_ELSE = "else"
    T_WHILE = "while"
    T_FOR = "for"

    # ------ Literals ------
    T_TRUE = "true"
    T_FALSE = "false"
    T_NULL = "null"

    # --- Operators ---

    # ------ Arithmetic ------
    T_PLUS = "+"
    T_MINUS = "-"
    T_MULTIPLY = "*"
    T_DIVIDE = "/"
    T_MODULO = "%"

    # ------ Assignment ------
    T_ASSIGN = "="
    T_ASSIGN_PLUS = "+="
    T_ASSIGN_MINUS = "-="
    T_ASSIGN_MULTIPLY = "*="
    T_ASSIGN_DIVIDE = "/="
    T_ASSIGN_MODULO = "%="

    # ------ Comparison ------
    T_GREATER = ">"
    T_LESS = "<"
    T_GREATER_EQUAL = ">="
    T_LESS_EQUAL = "<="
    T_EQUAL = "=="
    T_NOT_EQUAL = "!="

    # ------ Logic ------
    T_AND = "&"
    T_OR = "|"

    # ------ Access ------
    T_ACCESS = "."
    T_NULLABLE_ACCESS = "?."

    # ------ Other ------
    T_NOT = "!"
    T_REF = "@"
    T_TYPE_CHECK = "is"

    # --- Brackets ---
    T_LEFT_BRACKET = "("
    T_RIGHT_BRACKET = ")"
    T_LEFT_CURLY_BRACKET = "{"
    T_RIGHT_CURLY_BRACKET = "}"

    # --- Other ---
    T_IDENTIFIER = "id"
    T_SEMICOLON = ";"
    T_COMMA = ","
    T_COLON = ":"
    T_COMMENT = "#"
    T_OPTIONAL = "?"
    T_UNDEFINED = "undefined"
    T_EOF = "eof"
