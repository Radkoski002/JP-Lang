from enum import Enum


class TokenType(Enum):
    # --- Literals ---
    T_INT_LITERAL = 256
    T_FLOAT_LITERAL = 257
    T_STRING_LITERAL = 258

    # --- Keywords ---

    # ------ Functions ------
    T_RETURN = 259
    T_BREAK = 260
    T_CONTINUE = 261

    # ------ Statements ------
    T_IF = 262
    T_ELSE = 263
    T_WHILE = 264
    T_FOR = 265

    # ------ Literals ------
    T_TRUE = 266
    T_FALSE = 267
    T_NULL = 268

    # --- Operators ---

    # ------ Arithmetic ------
    T_PLUS = 269  # +
    T_MINUS = 270  # -
    T_MULTIPLY = 271  # *
    T_DIVIDE = 272  # /
    T_MODULO = 273  # %

    # ------ Assignment ------
    T_ASSIGN = 274  # =
    T_ASSIGN_PLUS = 275  # +=
    T_ASSIGN_MINUS = 276  # -=
    T_ASSIGN_MULTIPLY = 277  # *=
    T_ASSIGN_DIVIDE = 277  # /=
    T_ASSIGN_MODULO = 279  # %=

    # ------ Comparison ------
    T_GREATER = 280  # >
    T_LESS = 281  # <
    T_GREATER_EQUAL = 282  # >=
    T_LESS_EQUAL = 283  # <=
    T_EQUAL = 284  # ==
    T_NOT_EQUAL = 285  # !=

    # ------ Logic ------
    T_AND = 286  # &
    T_OR = 287  # |

    # ------ Access ------
    T_ACCESS = 288  # .
    T_NULLABLE_ACCESS = 289  # ?.

    # ------ Other ------
    T_NOT = 290  # !
    T_REF = 291  # @

    # --- Brackets ---
    T_LEFT_BRACKET = 292  # (
    T_RIGHT_BRACKET = 293  # )
    T_LEFT_CURLY_BRACKET = 294  # {
    T_RIGHT_CURLY_BRACKET = 295  # }

    # --- Other ---
    T_IDENTIFIER = 296
    T_SEMICOLON = 297  # ;
    T_COMMA = 298  # ,
    T_COLON = 299  # :
    T_COMMENT = 300
    T_OPTIONAL = 301  # ?
    T_EOF = 302
