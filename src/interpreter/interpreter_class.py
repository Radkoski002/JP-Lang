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


class Interpreter(IVisitor):
    def __init__(self, error_handler: ErrorHandler) -> None:
        super().__init__()
        self.result: any = None
        self.error_handler: ErrorHandler = error_handler
        self.program: Program | None = None

        self.current_environment: FunctionScope | None = None
        self.call_stack: list[FunctionScope] = []

        self.loop_scopes: int = 0
        self.break_called: bool = False
        self.continue_called: bool = False
        self.return_called: bool = False

        self.is_reference: bool = False
        self.error_thrown: None | Error = None
        self.error_position: Position | None = None
        self.function_call_position: Position | None = None

        self.property_access_depth: int = 0
        self.set_property_name: bool = False
        self.property_name: str | None = None
        self.return_reference: bool = False

        self.max_call_stack_size = 100

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
        self, left: any, right: any, operator: str, position: Position, one_side=False
    ):
        if (
            not isinstance(left, (int, float))
            or not isinstance(right, (int, float))
            or isinstance(left, bool)
            or isinstance(right, bool)
        ):
            self.error_thrown = TypeError(
                position,
                f"Cannot apply operator {operator} to given values: {left}{f' and {right}' if not one_side else ''}",
            )
            return True
        return False

    def __check_boolean_types(
        self, left: any, right: any, operator: str, position: Position, one_side=False
    ):
        if not isinstance(left, bool) or not isinstance(right, bool):
            self.error_thrown = TypeError(
                position,
                f"Cannot apply operator {operator} to given values: {left}{f' and {right}' if not one_side else ''}",
            )
            return True
        return False

    def __check_division_by_zero(
        self, left: any, right: any, operator: str, position: Position
    ):
        if right == 0:
            self.error_thrown = ValueError(
                position,
                f"Cannot apply operator {operator} if right side is 0.",
            )
            return True
        return False

    def __evaluate_infix_expression(
        self, node: InfixExpression, function: function, operator: str, check_funcs=[]
    ):
        left, right = self.__get_infix_sides(node)
        for func in check_funcs:
            if func(left, right, operator, node.position):
                return
        self.result = function(left, right)

    def __evaluate_arithmetic_assignment(
        self, node: any, function: function, operator: str, check_div=False
    ):
        try:
            self.return_reference = True
            node.variable.accept(self)
            self.return_reference = False
            if self.property_name:
                parent = self.__consume_result()
                left = getattr(parent, self.property_name)
            else:
                left = self.current_environment.get_or_init_variable(node.variable.name)
        except:
            self.error_thrown = VariableError(
                node.position,
                f"Variable {node.variable.name} is not defined",
            )
            return
        self.return_reference = False
        node.expression.accept(self)
        right = self.__consume_result()
        if self.__check_arithmetic_types(left, right, operator, node.position) or (
            check_div
            and self.__check_division_by_zero(left, right, operator, node.position)
        ):
            return
        if self.property_name:
            setattr(parent, self.property_name, function(left, right))
            self.property_name = None
        else:
            self.current_environment.set_or_init_variable(
                node.variable.name, function(left, right)
            )

    def __evaluate_arguments(self, arguments: list[Argument]):
        evaluated = []
        for argument in arguments:
            argument.accept(self)
            evaluated.append(self.__consume_result())
        return evaluated

    def __evaluate_property_access(
        self, node: PropertyAccessExpression | OptionalPropertyAccessExpression
    ):
        self.property_access_depth += 1
        node.left.accept(self)
        if self.return_reference and self.property_access_depth == 1:
            self.set_property_name = True
        node.right.accept(self)
        self.property_access_depth -= 1

    def _visit_program(self, node: Program):
        self.program = node
        if function := node.functions.get("main"):
            function.accept(self)
            if self.error_thrown:
                self.error_handler.raise_critical_error(self.error_thrown)
                return
        else:
            self.error_handler.raise_critical_error(
                RuntimeError(Position(1, 1), "Program does not contain a main function")
            )

    def _visit_built_in_function(self, node: BuiltInFunction):
        arguments = (
            [self.error_position, *self.__consume_result()]
            if isinstance(node, ErrorConstructor)
            else self.__consume_result()
        )
        if node.argc != None and node.argc < len(arguments):
            self.error_thrown = ArgumentError(
                self.function_call_position,
                f"Function {node.name} takes max of {node.argc} arguments, {len(arguments)} given",
            )
            return
        self.result = node.execute(arguments)

    def _visit_function_definition(self, node: FunctionDef):
        if node.name == "main" and len(node.parameters) > 0:
            self.error_thrown = ArgumentError(
                node.position,
                "Main function cannot take any arguments",
            )
            return
        new_env = FunctionScope()
        args = self.__consume_result()
        if args != None:
            if len(args) > len(node.parameters):
                self.error_thrown = ArgumentError(
                    node.position,
                    f"Function {node.name} takes {len(node.parameters)} arguments, {len(args)} given",
                )
                return
            for param, value in zip_longest(node.parameters, args):
                if not param.is_optional and value is None:
                    self.error_thrown = ArgumentError(
                        node.position,
                        f"Parameter {param.name} is not optional",
                    )
                    return
                elif param.is_optional and value is None:
                    param.value.accept(self)
                    new_env.set_or_init_variable(param.name, self.__consume_result())
                else:
                    if isinstance(value, tuple):
                        new_env.set_or_init_variable(param.name, *value)
                    else:
                        new_env.set_or_init_variable(param.name, value)

        self.current_environment = new_env
        node.block.accept(self)
        self.return_called = False

    def _visit_argument(self, node: Argument):
        self.is_reference = node.is_reference
        node.value.accept(self)
        self.is_reference = False

    def _visit_block_statement(self, node: BlockStatement):
        self.current_environment.enter_scope(self.__consume_result())
        for statement in node.statements:
            statement.accept(self)
            self.result = None
            if (
                (self.break_called or self.continue_called)
                and self.loop_scopes > 0
                or self.return_called
                or self.error_thrown
            ):
                break
        self.current_environment.exit_scope()

    def _visit_add_expression(self, node: AddExpression):
        func = lambda a, b: a + b
        self.__evaluate_infix_expression(
            node, func, "+", [self.__check_arithmetic_types]
        )

    def _visit_subtract_expression(self, node: SubtractExpression):
        func = lambda a, b: a - b
        self.__evaluate_infix_expression(
            node, func, "-", [self.__check_arithmetic_types]
        )

    def _visit_multiply_expression(self, node: MultiplyExpression):
        func = lambda a, b: a * b
        self.__evaluate_infix_expression(
            node, func, "*", [self.__check_arithmetic_types]
        )

    def _visit_divide_expression(self, node: DivideExpression):
        func = lambda a, b: a / b
        self.__evaluate_infix_expression(
            node,
            func,
            "/",
            [self.__check_arithmetic_types, self.__check_division_by_zero],
        )

    def _visit_modulo_expression(self, node: ModuloExpression):
        func = lambda a, b: a % b
        self.__evaluate_infix_expression(
            node,
            func,
            "%",
            [self.__check_arithmetic_types, self.__check_division_by_zero],
        )

    def _visit_equal_expression(self, node: EqualExpression):
        func = lambda a, b: a == b
        self.__evaluate_infix_expression(node, func, "==")

    def _visit_not_equal_expression(self, node: NotEqualExpression):
        func = lambda a, b: a != b
        self.__evaluate_infix_expression(node, func, "!=")

    def _visit_greater_equal_expression(self, node: GreaterEqualExpression):
        func = lambda a, b: a >= b
        self.__evaluate_infix_expression(
            node, func, ">=", [self.__check_arithmetic_types]
        )

    def _visit_greater_than_expression(self, node: GreaterThanExpression):
        func = lambda a, b: a > b
        self.__evaluate_infix_expression(
            node, func, ">", [self.__check_arithmetic_types]
        )

    def _visit_less_equal_expression(self, node: LessEqualExpression):
        func = lambda a, b: a <= b
        self.__evaluate_infix_expression(
            node, func, "<=", [self.__check_arithmetic_types]
        )

    def _visit_less_than_expression(self, node: LessThanExpression):
        func = lambda a, b: a < b
        self.__evaluate_infix_expression(
            node, func, "<", [self.__check_arithmetic_types]
        )

    def _visit_and_expression(self, node: AndExpression):
        func = lambda a, b: a and b
        self.__evaluate_infix_expression(node, func, "&", [self.__check_boolean_types])

    def _visit_or_expression(self, node: OrExpression):
        func = lambda a, b: a or b
        self.__evaluate_infix_expression(node, func, "|", [self.__check_boolean_types])

    def _visit_bitwise_negation_expression(self, node: BitwiseNegationExpression):
        node.expression.accept(self)
        value = self.__consume_result()
        if self.__check_boolean_types(value, True, "!", node.position, True):
            return
        self.result = not value

    def _visit_numeric_negation_expression(self, node: NumericNegationExpression):
        node.expression.accept(self)
        value = self.__consume_result()
        if self.__check_arithmetic_types(value, 0, "-", node.position, True):
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
                if self.set_property_name:
                    self.property_name = node.name
                    self.set_property_name = False
                    return
                self.result = getattr(self.result, node.name)
            except AttributeError:
                self.error_thrown = PropertyError(
                    node.position,
                    f"Class {type(self.result).__name__} does not have a property {node.name} or it's value is None",
                )
        else:
            if self.is_reference:
                self.result = (
                    self.current_environment.get_or_init_variable(node.name),
                    node.name,
                )
                return
            self.result = self.current_environment.get_or_init_variable(node.name)

    def _visit_function_call_expression(self, node: FunctionCallExpression):
        if self.result is not None:
            built_in_class = self.__consume_result()
            try:
                function = getattr(built_in_class, node.name)
                self.result = function(*self.__evaluate_arguments(node.arguments))
            except AttributeError:
                self.error_thrown = PropertyError(
                    node.position,
                    f"Class {type(built_in_class).__name__} does not have a method {node.name}",
                )
        else:
            if node.name == "main":
                self.error_thrown = FunctionError(
                    node.position,
                    "main function cannot be called",
                )
                return
            self.result = self.__evaluate_arguments(node.arguments)
            self.function_call_position = node.position
            if len(self.call_stack) == self.max_call_stack_size:
                self.error_thrown = StackOverflowError(
                    node.position,
                    f"Maximum call stack size of {self.max_call_stack_size} exceeded",
                )
                return
            self.call_stack.append(self.current_environment)
            if function := self.program.functions.get(node.name):
                function.accept(self)
            else:
                self.error_thrown = FunctionError(
                    node.position,
                    f"Function {node.name} is not defined",
                )
            if self.error_thrown:
                return
            old_environment = self.call_stack.pop()
            for key, value in self.current_environment.references.items():
                old_environment.set_or_init_variable(
                    key, self.current_environment.get_or_init_variable(value)
                )
            self.current_environment = old_environment

    def _visit_property_access_expression(self, node: PropertyAccessExpression):
        self.__evaluate_property_access(node)

    def _visit_optional_property_access_expression(
        self, node: OptionalPropertyAccessExpression
    ):
        self.__evaluate_property_access(node)
        if isinstance(self.error_thrown, PropertyError):
            self.error_thrown = None
            self.result = None

    def _visit_if_statement(self, node: IfStatement):
        node.condition.accept(self)
        if self.error_thrown:
            return
        if self.__consume_result():
            node.block.accept(self)
        else:
            for elif_block in node.elif_statements:
                elif_block.condition.accept(self)
                if self.error_thrown:
                    return
                if self.__consume_result():
                    elif_block.block.accept(self)
                    return
            if node.else_statement is not None:
                node.else_statement.accept(self)

    # TODO: Move loop scopes to calling scope
    def _visit_while_statement(self, node: WhileStatement):
        self.loop_scopes += 1
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
                self.loop_scopes -= 1
                return

        self.loop_scopes -= 1

    def _visit_for_statement(self, node: ForStatement):
        self.loop_scopes += 1
        node.iterable.accept(self)
        iterable = self.__consume_result()
        if not isinstance(iterable, Array):
            self.error_thrown = TypeError(
                node.position, "For loop can only iterate over array"
            )
            return
        for item in iterable._value:
            self.result = {node.variable.name: item}
            node.block.accept(self)
            if self.break_called:
                self.break_called = False
                break
            if self.continue_called:
                self.continue_called = False
            if self.error_thrown:
                self.loop_scopes -= 1
                return
        self.loop_scopes -= 1

    def _visit_return_statement(self, node: ReturnStatement):
        if node.expression is not None:
            node.expression.accept(self)
        self.return_called = True

    def _visit_assignment_statement(self, node: AssignmentStatement):
        node.expression.accept(self)
        if self.error_thrown:
            return
        result = self.__consume_result()
        self.return_reference = True
        node.variable.accept(self)
        self.return_reference = False
        if self.property_name:
            setattr(self.__consume_result(), self.property_name, result)
            self.property_name = None
        else:
            self.current_environment.set_or_init_variable(node.variable.name, result)

    def _visit_assignment_plus_statement(self, node: AssignmentPlusStatement):
        func = lambda x, y: x + y
        self.__evaluate_arithmetic_assignment(node, func, "+=")

    def _visit_assignment_minus_statement(self, node: AssignmentMinusStatement):
        func = lambda x, y: x - y
        self.__evaluate_arithmetic_assignment(node, func, "-=")

    def _visit_assignment_multiply_statement(self, node: AssignmentMultiplyStatement):
        func = lambda x, y: x * y
        self.__evaluate_arithmetic_assignment(node, func, "*=")

    def _visit_assignment_divide_statement(self, node: AssignmentDivideStatement):
        func = lambda x, y: x / y
        self.__evaluate_arithmetic_assignment(node, func, "/=", True)

    def _visit_assignment_modulo_statement(self, node: AssignmentModuloStatement):
        func = lambda x, y: x % y
        self.__evaluate_arithmetic_assignment(node, func, "%=", True)

    def _visit_try_catch_statement(self, node: TryCatchStatement):
        node.try_statement.accept(self)
        if self.error_thrown:
            for catch_block in node.catch_statements:
                if not catch_block.error_types:
                    self.error_thrown = None
                    catch_block.catch_statement.accept(self)
                    return
                for error_type in catch_block.error_types:
                    if error_type.name not in self.program.functions:
                        self.error_thrown = TypeError(
                            node.position,
                            f"Unknown error type {error_type.name}",
                        )
                        return
                    if isinstance(
                        self.error_thrown.__class__, eval(error_type.name)
                    ) or issubclass(self.error_thrown.__class__, eval(error_type.name)):
                        self.result = {catch_block.error_var.name: self.error_thrown}
                        self.error_thrown = None
                        catch_block.catch_statement.accept(self)
                        return

    def _visit_throw_statement(self, node: ThrowStatement):
        self.error_position = node.position
        node.expression.accept(self)
        self.error_thrown = self.__consume_result()
        if not isinstance(self.error_thrown, Error):
            self.error_thrown = TypeError(
                node.position, "Throw statement can only throw error"
            )
        self.error_position = None

    def _visit_break_statement(self, node: BreakStatement):
        if self.loop_scopes == 0:
            self.error_thrown = ExpressionError(
                node.position,
                "break statement can only be used in loop",
            )
        self.break_called = True

    def _visit_continue_statement(self, node: ContinueStatement):
        if self.loop_scopes == 0:
            self.error_thrown = ExpressionError(
                node.position,
                "continue statement can only be used in loop",
            )
        self.continue_called = True
