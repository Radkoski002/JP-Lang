from utils.position_class import Position


class IExpression:
    def __init__(self, position: Position = None) -> None:
        self.position: Position = position

    def __eq__(self, other):
        return type(self) == type(other)


class InfixExpression(IExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(position)
        self.left: IExpression = left
        self.right: IExpression = right

    def __eq__(self, other):
        if isinstance(other, InfixExpression):
            return (
                super().__eq__(other)
                and self.left == other.left
                and self.right == other.right
            )
        return False


class OrExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class AndExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class EqualExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class NotEqualExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class GreaterThanExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class GreaterEqualExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class LessThanExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class LessEqualExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class AddExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class SubtractExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class MultiplyExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class DivideExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class ModuloExpression(InfixExpression):
    def __init__(
        self, left: IExpression, right: IExpression, position: Position = None
    ) -> None:
        super().__init__(left, right, position)


class BitwiseNegationExpression(IExpression):
    def __init__(self, expression: IExpression, position: Position = None) -> None:
        super().__init__(position)
        self.expression: IExpression = expression


class NumericNegationExpression(IExpression):
    def __init__(self, expression: IExpression, position: Position = None) -> None:
        super().__init__(position)
        self.expression: IExpression = expression


class TypeCheckExpression(IExpression):
    def __init__(
        self, expression: IExpression, type_name: str, position: Position = None
    ) -> None:
        super().__init__(position)
        self.expression: IExpression = expression
        self.type_name: str = type_name


class LiteralExpression(IExpression):
    def __init__(self, value: any, position: Position = None) -> None:
        super().__init__(position)
        self.value: any = value

    def __eq__(self, other):
        if isinstance(other, LiteralExpression):
            return self.value == other.value
        return False


class NullLiteral(LiteralExpression):
    def __init__(self, position: Position = None) -> None:
        super().__init__(None, position)


class IntegerLiteral(LiteralExpression):
    def __init__(self, value: int, position: Position = None) -> None:
        super().__init__(value, position)


class FloatLiteral(LiteralExpression):
    def __init__(self, value: float, position: Position = None) -> None:
        super().__init__(value, position)


class StringLiteral(LiteralExpression):
    def __init__(self, value: str, position: Position = None) -> None:
        super().__init__(value, position)


class BooleanLiteral(LiteralExpression):
    def __init__(self, value: bool, position: Position = None) -> None:
        super().__init__(value, position)


class FalseLiteral(BooleanLiteral):
    def __init__(self, position: Position = None) -> None:
        super().__init__(False, position)


class TrueLiteral(BooleanLiteral):
    def __init__(self, position: Position = None) -> None:
        super().__init__(True, position)


class IdentifierExpression(IExpression):
    def __init__(self, name: str, position: Position = None) -> None:
        super().__init__(position)
        self.name: str = name

    def __eq__(self, other):
        if isinstance(other, IdentifierExpression):
            return self.name == other.name
        return False


class FunctionCallExpression(IExpression):
    def __init__(
        self, name: str, arguments: list[IExpression], position: Position = None
    ) -> None:
        super().__init__(position)
        self.name: str = name
        self.arguments: list[Argument] = arguments

    def __eq__(self, other):
        if isinstance(other, FunctionCallExpression):
            return (
                super().__eq__(other)
                and self.name == other.name
                and self.arguments == other.arguments
            )
        return False


class PropertyAccessExpression(InfixExpression):
    def __init__(
        self,
        main_object: FunctionCallExpression | IdentifierExpression,
        property: FunctionCallExpression | IdentifierExpression,
        position: Position = None,
    ) -> None:
        super().__init__(main_object, property, position)


class OptionalPropertyAccessExpression(InfixExpression):
    def __init__(
        self,
        main_object: FunctionCallExpression | IdentifierExpression,
        property: FunctionCallExpression | IdentifierExpression,
        position: Position = None,
    ) -> None:
        super().__init__(main_object, property, position)


class IStatement:
    def __init__(self, position: Position = None) -> None:
        self.position: Position = position

    def __eq__(self, other):
        return type(self) == type(other)


class BlockStatement:
    def __init__(self, statements: list[IStatement], position: Position = None) -> None:
        self.statements: list[IStatement] = statements
        self.position: Position = position

    def __eq__(self, other):
        if isinstance(other, BlockStatement):
            return self.statements == other.statements
        return False


class ConditionalStatement(IStatement):
    def __init__(
        self, condition: IExpression, block: BlockStatement, position: Position = None
    ) -> None:
        super().__init__(position)
        self.condition: IExpression = condition
        self.block: BlockStatement = block

    def __eq__(self, other):
        if isinstance(other, ConditionalStatement):
            return (
                super().__eq__(other)
                and self.condition == other.condition
                and self.block == other.block
            )
        return False


class IfStatement(ConditionalStatement):
    def __init__(
        self,
        condition: IExpression,
        block: BlockStatement,
        elif_statements: list[ConditionalStatement] = [],
        else_statement: BlockStatement = None,
        position: Position = None,
    ) -> None:
        super().__init__(condition, block, position)
        self.elif_statements: list[BlockStatement] = elif_statements
        self.else_statement: BlockStatement = else_statement

    def __eq__(self, other):
        return super().__eq__(other) and (
            self.elif_statements == other.elif_statements
            and self.else_statement == other.else_statement
        )


class WhileStatement(ConditionalStatement):
    def __init__(
        self, condition: IExpression, block: BlockStatement, position: Position = None
    ) -> None:
        super().__init__(condition, block, position)


class ForStatement(IStatement):
    def __init__(
        self,
        variable_name: str,
        iterable: IExpression,
        block: BlockStatement,
        position: Position = None,
    ) -> None:
        super().__init__(position)
        self.variable_name: str = variable_name
        self.iterable: IExpression = iterable
        self.block: BlockStatement = block

    def __eq__(self, other):
        if isinstance(other, ForStatement):
            return (
                super().__eq__(other)
                and self.variable_name == other.variable_name
                and self.iterable == other.iterable
                and self.block == other.block
            )
        return False


class ReturnStatement(IStatement):
    def __init__(
        self, expression: IExpression = None, position: Position = None
    ) -> None:
        super().__init__(position)
        self.expression: IExpression = expression

    def __eq__(self, other):
        if isinstance(other, ReturnStatement):
            return self.expression == other.expression
        return False


class AssignmentStatement(IStatement):
    def __init__(
        self,
        variable: IdentifierExpression,
        expression: IExpression,
        position: Position = None,
    ) -> None:
        super().__init__(position)
        self.variable: IdentifierExpression = variable
        self.expression: IExpression = expression

    def __eq__(self, other):
        if isinstance(other, AssignmentStatement):
            return (
                super().__eq__(other)
                and self.variable == other.variable
                and self.expression == other.expression
            )
        return False


class AssignmentPlusStatement(AssignmentStatement):
    def __init__(
        self,
        variable: IdentifierExpression,
        expression: IExpression,
        position: Position = None,
    ) -> None:
        super().__init__(variable, expression, position)


class AssignmentMinusStatement(AssignmentStatement):
    def __init__(
        self,
        variable: IdentifierExpression,
        expression: IExpression,
        position: Position = None,
    ) -> None:
        super().__init__(variable, expression, position)


class AssignmentMultiplyStatement(AssignmentStatement):
    def __init__(
        self,
        variable: IdentifierExpression,
        expression: IExpression,
        position: Position = None,
    ) -> None:
        super().__init__(variable, expression, position)


class AssignmentDivideStatement(AssignmentStatement):
    def __init__(
        self,
        variable: IdentifierExpression,
        expression: IExpression,
        position: Position = None,
    ) -> None:
        super().__init__(variable, expression, position)


class AssignmentModuloStatement(AssignmentStatement):
    def __init__(
        self,
        variable: IdentifierExpression,
        expression: IExpression,
        position: Position = None,
    ) -> None:
        super().__init__(variable, expression, position)


class CatchStatement(IStatement):
    def __init__(
        self,
        catch_statement: BlockStatement,
        error_types: list[IdentifierExpression] = [],
        error_var: IdentifierExpression = None,
        position: Position = None,
    ) -> None:
        super().__init__(position)
        self.catch_statement: BlockStatement = catch_statement
        self.error_types: list[IdentifierExpression] = error_types
        self.error_var: IdentifierExpression = error_var

    def __eq__(self, other):
        if isinstance(other, CatchStatement):
            return (
                super().__eq__(other)
                and self.catch_statement == other.catch_statement
                and self.error_types == other.error_types
                and self.error_var == other.error_var
            )
        return False


class TryCatchStatement(IStatement):
    def __init__(
        self,
        try_statement: BlockStatement,
        catch_statements: list[CatchStatement],
        position: Position = None,
    ) -> None:
        super().__init__(position)
        self.try_statement: BlockStatement = try_statement
        self.catch_statements: list[CatchStatement] = catch_statements

    def __eq__(self, other):
        if isinstance(other, TryCatchStatement):
            return (
                super().__eq__(other)
                and self.try_statement == other.try_statement
                and self.catch_statements == other.catch_statements
            )
        return False


class ThrowStatement(IStatement):
    def __init__(self, expression: IExpression, position: Position = None) -> None:
        super().__init__(position)
        self.expression: IExpression = expression


class BreakStatement(IStatement):
    def __init__(self, position: Position = None) -> None:
        super().__init__(position)


class ContinueStatement(IStatement):
    def __init__(self, position: Position = None) -> None:
        super().__init__(position)


class Argument:
    def __init__(
        self, value: IExpression, is_reference: bool = False, position: Position = None
    ) -> None:
        self.value: IExpression = value
        self.is_reference: bool = is_reference
        self.position: Position = position

    def __eq__(self, other):
        if isinstance(other, Argument):
            return self.value == other.value and self.is_reference == other.is_reference
        return False


class Parameter:
    def __init__(
        self,
        name: str,
        is_optional: bool = False,
        value: LiteralExpression = None,
        position: Position = None,
    ) -> None:
        self.name: str = name
        self.is_optional: bool = is_optional
        self.value: LiteralExpression = value
        self.position: Position = position

    def __eq__(self, other):
        if isinstance(other, Parameter):
            return (
                self.name == other.name
                and self.is_optional == other.is_optional
                and self.value == other.value
            )
        return False


class FunctionDef:
    def __init__(
        self,
        parameters: list[Parameter],
        block: BlockStatement,
        position: Position = None,
    ) -> None:
        self.parameters: list[Parameter] = parameters
        self.block: BlockStatement = block
        self.position: Position = position

    def __eq__(self, other):
        if isinstance(other, FunctionDef):
            return self.parameters == other.parameters and self.block == other.block
        return False
