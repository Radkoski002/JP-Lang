from enum import Enum

from lexer.token_type_enum import TokenType
from parser.statement_classes import *
from parser.parser_error_class import PARSER_ERROR_TYPES


class INFIX_EXPRESSIONS(Enum):
    OR = "or"
    AND = "and"
    COMPARISON = "comparison"
    ADDITION = "addition"
    MULTIPLICATION = "multiplication"
    PROPERTY_ACCESS = "property_access"


type_check_token_to_constructor: dict[TokenType, TypeCheckExpression] = {
    TokenType.T_TYPE_CHECK: TypeCheckExpression,
}

identifier_token_to_constructor: dict[TokenType, IdentifierExpression] = {
    TokenType.T_IDENTIFIER: IdentifierExpression
}

or_token_to_constructor: dict[TokenType, OrExpression] = {
    TokenType.T_OR: OrExpression,
}

and_token_to_constructor: dict[TokenType, AndExpression] = {
    TokenType.T_AND: AndExpression,
}

assignment_token_to_constructor: dict[TokenType, AssignmentStatement] = {
    TokenType.T_ASSIGN: AssignmentStatement,
    TokenType.T_ASSIGN_PLUS: AssignmentPlusStatement,
    TokenType.T_ASSIGN_MINUS: AssignmentMinusStatement,
    TokenType.T_ASSIGN_MULTIPLY: AssignmentMultiplyStatement,
    TokenType.T_ASSIGN_DIVIDE: AssignmentDivideStatement,
    TokenType.T_ASSIGN_MODULO: AssignmentModuloStatement,
}

comparison_token_to_constructor: dict[TokenType, InfixExpression] = {
    TokenType.T_EQUAL: EqualExpression,
    TokenType.T_NOT_EQUAL: NotEqualExpression,
    TokenType.T_GREATER: GreaterThanExpression,
    TokenType.T_GREATER_EQUAL: GreaterEqualExpression,
    TokenType.T_LESS: LessThanExpression,
    TokenType.T_LESS_EQUAL: LessEqualExpression,
}

additive_token_to_constructor: dict[TokenType, InfixExpression] = {
    TokenType.T_PLUS: AddExpression,
    TokenType.T_MINUS: SubtractExpression,
}

multiplicative_token_to_constructor: dict[TokenType, InfixExpression] = {
    TokenType.T_MULTIPLY: MultiplyExpression,
    TokenType.T_DIVIDE: DivideExpression,
    TokenType.T_MODULO: ModuloExpression,
}

access_token_to_constructor: dict[TokenType, PropertyAccessExpression] = {
    TokenType.T_ACCESS: PropertyAccessExpression,
    TokenType.T_NULLABLE_ACCESS: OptionalPropertyAccessExpression,
}

literal_with_value_token_to_constructor: dict[TokenType, LiteralExpression] = {
    TokenType.T_INT_LITERAL: IntegerLiteral,
    TokenType.T_FLOAT_LITERAL: FloatLiteral,
    TokenType.T_STRING_LITERAL: StringLiteral,
}

literal_without_value_token_to_constructor: dict[TokenType, LiteralExpression] = {
    TokenType.T_TRUE: TrueLiteral,
    TokenType.T_FALSE: FalseLiteral,
    TokenType.T_NULL: NullLiteral,
}

negation_token_to_constructor: dict[TokenType, IExpression] = {
    TokenType.T_NOT: BitwiseNegationExpression,
    TokenType.T_MINUS: NumericNegationExpression,
}


token_to_error: dict[TokenType, PARSER_ERROR_TYPES] = {
    TokenType.T_LEFT_BRACKET: PARSER_ERROR_TYPES.MISSING_OPENING_BRACKET,
    TokenType.T_RIGHT_BRACKET: PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET,
    TokenType.T_LEFT_CURLY_BRACKET: PARSER_ERROR_TYPES.MISSING_BLOCK_START,
    TokenType.T_RIGHT_CURLY_BRACKET: PARSER_ERROR_TYPES.MISSING_BLOCK_END,
    TokenType.T_SEMICOLON: PARSER_ERROR_TYPES.MISSING_SEMICOLON,
    TokenType.T_CATCH: PARSER_ERROR_TYPES.MISSING_CATCH_KEYWORD,
    TokenType.T_COLON: PARSER_ERROR_TYPES.MISSING_FOR_LOOP_COLON,
    TokenType.T_IDENTIFIER: PARSER_ERROR_TYPES.MISSING_TYPE_NAME,
}
