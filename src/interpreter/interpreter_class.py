from __future__ import annotations
from interpreter.visitor_interface import IVisitor
from typing import TYPE_CHECKING
from interpreter.built_in_classes import Array
from itertools import zip_longest
from interpreter.built_in_functions import *
from interpreter.interpreter_error_classes import *
from interpreter.function_scope_class import FunctionScope
from utils.error_handler_class import ErrorHandler

if TYPE_CHECKING:
    from program.program_class import Program
    from parser.statement_classes import *
    from interpreter.built_in_functions import BuiltInFunction

infix_functions = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "%": lambda a, b: a % b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "&": lambda a, b: a and b,
    "|": lambda a, b: a or b,
}


class Interpreter(IVisitor):
    def __init__(self, error_handler: ErrorHandler) -> None:
        super().__init__()
        self.result: any = None
        self.error_handler: ErrorHandler = error_handler
        self.program: Program | None = None

        self.current_environment: FunctionScope | None = None
        self.call_stack: list[FunctionScope] = []

        self.is_in_loop: bool = False
        self.is_reference: bool = False
        self.break_called: bool = False
        self.continue_called: bool = False
        self.return_called: bool = False
        self.error_thrown: bool = False

        self.error_position: Position | None = None
        self.function_call_position: Position | None = None

    def __consume_result(self) -> any:
        value = self.result
        self.result = None
        return value

    def __get_infix_sides(self, expression: InfixExpression) -> tuple[any, any]:
        expression.left.accept(self)
        left = self.__consume_result()
        expression.right.accept(self)
        right = self.__consume_result()
        return left, right

    def __check_arithmetic_types(
        self, left: any, right: any, operator: str, position: Position
    ):
        if (
            not isinstance(left, (int, float))
            or not isinstance(right, (int, float))
            or isinstance(left, bool)
            or isinstance(right, bool)
        ):
            self.__throw_error(
                TypeError,
                position,
                f"Cannot apply operator {operator} to given values: {left} and {right}",
            )
            return True
        return False

    def __check_boolean_types(
        self, left: any, right: any, operator: str, position: Position
    ):
        if not isinstance(left, bool) or not isinstance(right, bool):
            self.__throw_error(
                TypeError,
                position,
                f"Cannot apply operator {operator} to given values: {left} and {right}",
            )
            return True
        return False

    def __evaluate_infix_expression(
        self, node: InfixExpression, operator: str, check_func=None
    ):
        left, right = self.__get_infix_sides(node)
        if check_func and check_func(left, right, operator, node.position):
            return
        self.result = infix_functions[operator](left, right)

    def __evaluate_arithmetic_assignment(self, node: any, operator: str):
        node.expression.accept(self)
        left = self.__expect_value(node)
        if self.error_thrown:
            return
        right = self.__consume_result()
        self.__check_arithmetic_types(left, right, "+", node.position)
        self.current_environment.set_variable(
            node.variable.name, infix_functions[operator](left, right)
        )

    def __evaluate_arguments(self, arguments: list[Argument]):
        evaluated = []
        for argument in arguments:
            argument.accept(self)
            evaluated.append(self.__consume_result())
        return evaluated

    def __evaluate_new_scope(self, block: BlockStatement):
        self.current_environment.enter_scope()
        block.accept(self)
        self.current_environment.exit_scope()

    def __evaluate_property_access(
        self, node: PropertyAccessExpression | OptionalPropertyAccessExpression
    ):
        node.left.accept(self)
        left = self.__consume_result()
        self.result = left
        node.right.accept(self)
        return left

    def __expect_value(self, node: any):
        try:
            return self.current_environment.expect_and_get_variable(node.variable.name)
        except:
            self.__throw_error(
                VariableError,
                node.position,
                f"Variable {node.variable.name} is not defined",
            )

    def __throw_error(self, constructor: Error, position: Position, message: str):
        self.error_thrown = True
        self.result = constructor(position, message)

    def _visit_program(self, node: Program):
        self.program = node
        if function := node.functions.get("main"):
            function.accept(self)
            if self.error_thrown:
                self.error_thrown = False
                self.error_handler.raise_critical_error(self.__consume_result())
        else:
            self.error_handler.raise_critical_error(
                RuntimeError(Position(1, 1), "Program does not contain a main function")
            )

    def _visit_built_in_function(self, node: BuiltInFunction):
        arguments = self.__consume_result()
        if node.argc != None and node.argc < len(arguments):
            self.__throw_error(
                ArgumentError,
                self.function_call_position,
                f"Function {node.name} takes max of {node.argc} arguments, {len(arguments)} given",
            )
            return
        evaluated_arguments = [self.error_position] if self.error_position else []
        for argument in arguments:
            argument.accept(self)
            if self.error_thrown:
                return
            arg = self.__consume_result()
            if isinstance(arg, tuple):
                evaluated_arguments.append(arg[0])
            else:
                evaluated_arguments.append(arg)
        self.result = node.execute(evaluated_arguments)

    def _visit_function_definition(self, node: FunctionDef):
        new_env = FunctionScope()
        args = self.__consume_result()
        if args != None:
            if len(args) >= len(node.parameters):
                self.__throw_error(
                    ArgumentError,
                    node.position,
                    f"Function {node.name} takes {len(node.parameters)} arguments, {len(args)} given",
                )
                return
            evaluated_args = self.__evaluate_arguments(args)
            for param, value in zip_longest(node.parameters, evaluated_args):
                if not param.is_optional and value is None:
                    self.__throw_error(
                        ArgumentError,
                        node.position,
                        f"Parameter {param.name} is not optional",
                    )
                    return
                elif param.is_optional and value is None:
                    param.value.accept(self)
                    new_env.set_variable(param.name, self.__consume_result())
                else:
                    if isinstance(value, tuple):
                        new_env.set_variable(param.name, *value)
                    else:
                        new_env.set_variable(param.name, value)

        self.current_environment = new_env
        node.block.accept(self)
        self.return_called = False

    def _visit_argument(self, node: Argument):
        self.is_reference = node.is_reference
        node.value.accept(self)
        self.is_reference = False

    def _visit_block_statement(self, node: BlockStatement):
        for statement in node.statements:
            if (
                (self.break_called or self.continue_called)
                and self.is_in_loop
                or self.return_called
                or self.error_thrown
            ):
                break
            statement.accept(self)

    def _visit_add_expression(self, node: AddExpression):
        self.__evaluate_infix_expression(node, "+", self.__check_arithmetic_types)

    def _visit_subtract_expression(self, node: SubtractExpression):
        self.__evaluate_infix_expression(node, "-", self.__check_arithmetic_types)

    def _visit_multiply_expression(self, node: MultiplyExpression):
        self.__evaluate_infix_expression(node, "*", self.__check_arithmetic_types)

    def _visit_divide_expression(self, node: DivideExpression):
        self.__evaluate_infix_expression(node, "/", self.__check_arithmetic_types)

    def _visit_modulo_expression(self, node: ModuloExpression):
        self.__evaluate_infix_expression(node, "%", self.__check_arithmetic_types)

    def _visit_equal_expression(self, node: EqualExpression):
        self.__evaluate_infix_expression(node, "==")

    def _visit_not_equal_expression(self, node: NotEqualExpression):
        self.__evaluate_infix_expression(node, "!=")

    def _visit_greater_equal_expression(self, node: GreaterEqualExpression):
        self.__evaluate_infix_expression(node, ">=", self.__check_arithmetic_types)

    def _visit_greater_than_expression(self, node: GreaterThanExpression):
        self.__evaluate_infix_expression(node, ">", self.__check_arithmetic_types)

    def _visit_less_equal_expression(self, node: LessEqualExpression):
        self.__evaluate_infix_expression(node, "<=", self.__check_arithmetic_types)

    def _visit_less_than_expression(self, node: LessThanExpression):
        self.__evaluate_infix_expression(node, "<", self.__check_arithmetic_types)

    def _visit_and_expression(self, node: AndExpression):
        self.__evaluate_infix_expression(node, "&", self.__check_boolean_types)

    def _visit_or_expression(self, node: OrExpression):
        self.__evaluate_infix_expression(node, "|", self.__check_boolean_types)

    def _visit_bitwise_negation_expression(self, node: BitwiseNegationExpression):
        node.expression.accept(self)
        value = self.__consume_result()
        if self.__check_boolean_types(value, True, "!", node.position):
            return
        self.result = not value

    def _visit_numeric_negation_expression(self, node: NumericNegationExpression):
        node.expression.accept(self)
        value = self.__consume_result()
        if self.__check_arithmetic_types(value, 0, "-", node.position):
            return
        self.result = -value

    def _visit_type_check_expression(self, node: TypeCheckExpression):
        node.expression.accept(self)
        value = self.__consume_result()
        self.result = type(value).__name__ == node.type_name

    def _visit_string_literal(self, node: StringLiteral):
        self.result = node.value

    def _visit_integer_literal(self, node: IntegerLiteral):
        self.result = node.value

    def _visit_float_literal(self, node: FloatLiteral):
        self.result = node.value

    def _visit_boolean_literal(self, node: BooleanLiteral):
        self.result = node.value

    def _visit_null_literal(self, node: NullLiteral):
        self.result = node.value

    def _visit_identifier_expression(self, node: IdentifierExpression):
        if self.result is not None:
            try:
                self.result = getattr(self.result, node.name)
            except AttributeError:
                self.__throw_error(
                    PropertyError,
                    node.position,
                    f"Class {type(self.result).__name__} does not have a property {node.name} or it's value is None",
                )
        else:
            if self.is_reference:
                self.result = (
                    self.current_environment.get_variable(node.name),
                    node.name,
                )
                return
            self.result = self.current_environment.get_variable(node.name)

    def _visit_function_call_expression(self, node: FunctionCallExpression):
        if self.result is not None:
            built_in_class = self.__consume_result()
            try:
                function = getattr(built_in_class, node.name)
                self.result = function(*self.__evaluate_arguments(node.arguments))
            except AttributeError:
                self.__throw_error(
                    PropertyError,
                    node.position,
                    f"Class {type(built_in_class).__name__} does not have a method {node.name}",
                )
        else:
            self.result = node.arguments
            self.function_call_position = node.position
            self.call_stack.append(self.current_environment)
            if function := self.program.functions.get(node.name):
                function.accept(self)
            else:
                self.__throw_error(
                    FunctionError,
                    node.position,
                    f"Function {node.name} is not defined",
                )
            if self.error_thrown:
                return
            old_environment = self.call_stack.pop()
            for key, value in self.current_environment.references.items():
                old_environment.set_variable(
                    key, self.current_environment.variables.get(value)
                )
            self.current_environment = old_environment

    def _visit_property_access_expression(self, node: PropertyAccessExpression):
        self.__evaluate_property_access(node)

    def _visit_optional_property_access_expression(
        self, node: OptionalPropertyAccessExpression
    ):
        self.__evaluate_property_access(node)
        if self.error_thrown:
            self.error_thrown = False
            self.result = None

    def _visit_if_statement(self, node: IfStatement):
        node.condition.accept(self)
        if self.error_thrown:
            return
        if self.__consume_result():
            self.__evaluate_new_scope(node.block)
        else:
            for elif_block in node.elif_statements:
                elif_block.condition.accept(self)
                if self.error_thrown:
                    return
                if self.__consume_result():
                    self.__evaluate_new_scope(elif_block.block)
                    return
            if node.else_statement is not None:
                self.__evaluate_new_scope(node.else_statement)

    def _visit_while_statement(self, node: WhileStatement):
        self.is_in_loop = True
        while True:
            node.condition.accept(self)
            if not self.__consume_result():
                break
            node.block.accept(self)
            if self.break_called:
                self.break_called = False
                break
            if self.continue_called:
                self.continue_called = False
            if self.error_thrown:
                self.is_in_loop = False
                return

        self.is_in_loop = False

    def _visit_for_statement(self, node: ForStatement):
        self.is_in_loop = True
        node.iterable.accept(self)
        iterable = self.__consume_result()
        if not isinstance(iterable, Array):
            self.__throw_error(
                TypeError, node.position, "For loop can only iterate over array"
            )
            return
        self.current_environment.enter_scope()
        for item in iterable._value:
            self.current_environment.set_variable(node.variable.name, item)
            node.block.accept(self)
            if self.break_called:
                self.break_called = False
                break
            if self.continue_called:
                self.continue_called = False
            if self.error_thrown:
                self.is_in_loop = False
                return

        self.current_environment.exit_scope()
        self.is_in_loop = False

    def _visit_return_statement(self, node: ReturnStatement):
        node.expression.accept(self)
        self.return_called = True

    def _visit_assignment_statement(self, node: AssignmentStatement):
        node.expression.accept(self)
        if self.error_thrown:
            return
        self.current_environment.set_variable(
            node.variable.name, self.__consume_result()
        )

    def _visit_assignment_plus_statement(self, node: AssignmentPlusStatement):
        self.__evaluate_arithmetic_assignment(node, "+")

    def _visit_assignment_minus_statement(self, node: AssignmentMinusStatement):
        self.__evaluate_arithmetic_assignment(node, "-")

    def _visit_assignment_multiply_statement(self, node: AssignmentMultiplyStatement):
        self.__evaluate_arithmetic_assignment(node, "*")

    def _visit_assignment_divide_statement(self, node: AssignmentDivideStatement):
        self.__evaluate_arithmetic_assignment(node, "/")

    def _visit_assignment_modulo_statement(self, node: AssignmentModuloStatement):
        self.__evaluate_arithmetic_assignment(node, "%")

    def _visit_try_catch_statement(self, node: TryCatchStatement):
        node.try_statement.accept(self)
        if self.error_thrown:
            error_class: Error = self.__consume_result()
            for catch_block in node.catch_statements:
                if not catch_block.error_types:
                    self.error_thrown = False
                    self.current_environment.enter_scope()
                    catch_block.catch_statement.accept(self)
                    self.current_environment.exit_scope()
                    return
                for error_type in catch_block.error_types:
                    if error_type.name not in self.program.functions:
                        self.__throw_error(
                            TypeError,
                            node.position,
                            f"Unknown error type {error_type.name}",
                        )
                        return
                    if isinstance(
                        error_class.__class__, eval(error_type.name)
                    ) or issubclass(error_class.__class__, eval(error_type.name)):
                        self.error_thrown = False
                        self.current_environment.enter_scope()
                        self.current_environment.set_variable(
                            catch_block.error_var.name, error_class
                        )
                        catch_block.catch_statement.accept(self)
                        self.current_environment.exit_scope()
                        return
            self.result = error_class

    def _visit_throw_statement(self, node: ThrowStatement):
        self.error_position = node.position
        node.expression.accept(self)
        error_class = self.result
        if not isinstance(error_class, Error):
            self.__throw_error(
                TypeError, node.position, "Throw statement can only throw error"
            )
        self.error_thrown = True
        self.error_position = None

    def _visit_break_statement(self, node: BreakStatement):
        if not self.is_in_loop:
            self.__throw_error(
                ExpressionError,
                node.position,
                "break statement can only be used in loop",
            )
        self.break_called = True

    def _visit_continue_statement(self, node: ContinueStatement):
        if not self.is_in_loop:
            self.__throw_error(
                ExpressionError,
                node.position,
                "continue statement can only be used in loop",
            )
        self.continue_called = True
