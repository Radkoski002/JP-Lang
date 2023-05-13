from enum import Enum

from lexer.token_type_enum import TokenType
from parser.statement_classes import *


class INFIX_EXPRESSIONS(Enum):
    OR = "or"
    AND = "and"
    COMPARISON = "comparison"
    ADDITION = "addition"
    MULTIPLICATION = "multiplication"
    PROPERTY_ACCESS = "property_access"


token_to_constructor: dict[TokenType, InfixExpression] = {
    TokenType.T_OR: OrExpression,
    TokenType.T_AND: AndExpression,
    TokenType.T_EQUAL: EqualExpression,
    TokenType.T_NOT_EQUAL: NotEqualExpression,
    TokenType.T_GREATER: GreaterThanExpression,
    TokenType.T_GREATER_EQUAL: GreaterEqualExpression,
    TokenType.T_LESS: LessThanExpression,
    TokenType.T_LESS_EQUAL: LessEqualExpression,
    TokenType.T_PLUS: AddExpression,
    TokenType.T_MINUS: SubtractExpression,
    TokenType.T_MULTIPLY: MultiplyExpression,
    TokenType.T_DIVIDE: DivideExpression,
    TokenType.T_MODULO: ModuloExpression,
    TokenType.T_TYPE_CHECK: TypeCheckExpression,
    TokenType.T_IDENTIFIER: IdentifierExpression,
    TokenType.T_INT_LITERAL: IntegerLiteral,
    TokenType.T_FLOAT_LITERAL: FloatLiteral,
    TokenType.T_STRING_LITERAL: StringLiteral,
    TokenType.T_TRUE: TrueLiteral,
    TokenType.T_FALSE: FalseLiteral,
    TokenType.T_NULL: NullLiteral,
    TokenType.T_ACCESS: PropertyAccessExpression,
    TokenType.T_NULLABLE_ACCESS: OptionalPropertyAccessExpression,
    TokenType.T_ASSIGN: AssignmentStatement,
    TokenType.T_ASSIGN_PLUS: AssignmentPlusStatement,
    TokenType.T_ASSIGN_MINUS: AssignmentMinusStatement,
    TokenType.T_ASSIGN_MULTIPLY: AssignmentMultiplyStatement,
    TokenType.T_ASSIGN_DIVIDE: AssignmentDivideStatement,
    TokenType.T_ASSIGN_MODULO: AssignmentModuloStatement,
}
