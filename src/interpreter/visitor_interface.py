from __future__ import annotations
from abc import ABC, abstractmethod
from functools import singledispatch

from parser.statement_classes import *
from program.program_class import Program
from interpreter.built_in_functions import BuiltInFunction


class IVisitor(ABC):
    def __init__(self) -> None:
        self.visit = singledispatch(self.visit)
        self.visit.register(Program, self._visit_program)
        self.visit.register(BuiltInFunction, self._visit_built_in_function)

        # statements
        self.visit.register(FunctionDef, self._visit_function_definition)
        self.visit.register(BlockStatement, self._visit_block_statement)
        self.visit.register(IfStatement, self._visit_if_statement)
        self.visit.register(WhileStatement, self._visit_while_statement)
        self.visit.register(ForStatement, self._visit_for_statement)
        self.visit.register(ReturnStatement, self._visit_return_statement)
        self.visit.register(AssignmentStatement, self._visit_assignment_statement)
        self.visit.register(
            AssignmentPlusStatement, self._visit_assignment_plus_statement
        )
        self.visit.register(
            AssignmentMinusStatement, self._visit_assignment_minus_statement
        )
        self.visit.register(
            AssignmentMultiplyStatement, self._visit_assignment_multiply_statement
        )
        self.visit.register(
            AssignmentDivideStatement, self._visit_assignment_divide_statement
        )
        self.visit.register(
            AssignmentModuloStatement, self._visit_assignment_modulo_statement
        )
        self.visit.register(TryCatchStatement, self._visit_try_catch_statement)
        self.visit.register(ThrowStatement, self._visit_throw_statement)
        self.visit.register(BreakStatement, self._visit_break_statement)
        self.visit.register(ContinueStatement, self._visit_continue_statement)

        # expressions
        self.visit.register(AddExpression, self._visit_add_expression)
        self.visit.register(SubtractExpression, self._visit_subtract_expression)
        self.visit.register(MultiplyExpression, self._visit_multiply_expression)
        self.visit.register(DivideExpression, self._visit_divide_expression)
        self.visit.register(ModuloExpression, self._visit_modulo_expression)
        self.visit.register(EqualExpression, self._visit_equal_expression)
        self.visit.register(NotEqualExpression, self._visit_not_equal_expression)
        self.visit.register(LessThanExpression, self._visit_less_than_expression)
        self.visit.register(GreaterThanExpression, self._visit_greater_than_expression)
        self.visit.register(LessEqualExpression, self._visit_less_equal_expression)
        self.visit.register(
            GreaterEqualExpression, self._visit_greater_equal_expression
        )
        self.visit.register(AndExpression, self._visit_and_expression)
        self.visit.register(OrExpression, self._visit_or_expression)
        self.visit.register(
            BitwiseNegationExpression, self._visit_bitwise_negation_expression
        )
        self.visit.register(
            NumericNegationExpression, self._visit_numeric_negation_expression
        )
        self.visit.register(TypeCheckExpression, self._visit_type_check_expression)
        self.visit.register(StringLiteral, self._visit_string_literal)
        self.visit.register(IntegerLiteral, self._visit_integer_literal)
        self.visit.register(FloatLiteral, self._visit_float_literal)
        self.visit.register(BooleanLiteral, self._visit_boolean_literal)
        self.visit.register(NullLiteral, self._visit_null_literal)
        self.visit.register(IdentifierExpression, self._visit_identifier_expression)
        self.visit.register(
            FunctionCallExpression, self._visit_function_call_expression
        )
        self.visit.register(
            PropertyAccessExpression, self._visit_property_access_expression
        )
        self.visit.register(
            OptionalPropertyAccessExpression,
            self._visit_optional_property_access_expression,
        )
        self.visit.register(Argument, self._visit_argument)

    def visit(self, s):
        raise TypeError("This type isn't supported: {}".format(type(s)))

    @abstractmethod
    def _visit_program(self, node: Program):
        pass

    @abstractmethod
    def _visit_built_in_function(self, node: BuiltInFunction):
        pass

    @abstractmethod
    def _visit_add_expression(self, node: AddExpression):
        pass

    @abstractmethod
    def _visit_subtract_expression(self, node: SubtractExpression):
        pass

    @abstractmethod
    def _visit_multiply_expression(self, node: MultiplyExpression):
        pass

    @abstractmethod
    def _visit_divide_expression(self, node: DivideExpression):
        pass

    @abstractmethod
    def _visit_modulo_expression(self, node: ModuloExpression):
        pass

    @abstractmethod
    def _visit_equal_expression(self, node: EqualExpression):
        pass

    @abstractmethod
    def _visit_not_equal_expression(self, node: NotEqualExpression):
        pass

    @abstractmethod
    def _visit_less_than_expression(self, node: LessThanExpression):
        pass

    @abstractmethod
    def _visit_greater_than_expression(self, node: GreaterThanExpression):
        pass

    @abstractmethod
    def _visit_less_equal_expression(self, node: LessEqualExpression):
        pass

    @abstractmethod
    def _visit_greater_equal_expression(self, node: GreaterEqualExpression):
        pass

    @abstractmethod
    def _visit_and_expression(self, node: AndExpression):
        pass

    @abstractmethod
    def _visit_or_expression(self, node: OrExpression):
        pass

    @abstractmethod
    def _visit_bitwise_negation_expression(self, node: BitwiseNegationExpression):
        pass

    @abstractmethod
    def _visit_numeric_negation_expression(self, node: NumericNegationExpression):
        pass

    @abstractmethod
    def _visit_type_check_expression(self, node: TypeCheckExpression):
        pass

    @abstractmethod
    def _visit_string_literal(self, node: StringLiteral):
        pass

    @abstractmethod
    def _visit_integer_literal(self, node: IntegerLiteral):
        pass

    @abstractmethod
    def _visit_float_literal(self, node: FloatLiteral):
        pass

    @abstractmethod
    def _visit_boolean_literal(self, node: BooleanLiteral):
        pass

    @abstractmethod
    def _visit_null_literal(self, node: BooleanLiteral):
        pass

    @abstractmethod
    def _visit_identifier_expression(self, node: IdentifierExpression):
        pass

    @abstractmethod
    def _visit_function_call_expression(self, node: FunctionCallExpression):
        pass

    @abstractmethod
    def _visit_property_access_expression(self, node: PropertyAccessExpression):
        pass

    @abstractmethod
    def _visit_optional_property_access_expression(
        self, node: OptionalPropertyAccessExpression
    ):
        pass

    @abstractmethod
    def _visit_block_statement(self, node: BlockStatement):
        pass

    @abstractmethod
    def _visit_if_statement(self, node: IfStatement):
        pass

    @abstractmethod
    def _visit_while_statement(self, node: WhileStatement):
        pass

    @abstractmethod
    def _visit_for_statement(self, node: ForStatement):
        pass

    @abstractmethod
    def _visit_function_definition(self, node: FunctionDef):
        pass

    @abstractmethod
    def _visit_return_statement(self, node: ReturnStatement):
        pass

    @abstractmethod
    def _visit_assignment_statement(self, node: AssignmentStatement):
        pass

    @abstractmethod
    def _visit_assignment_plus_statement(self, node: AssignmentPlusStatement):
        pass

    @abstractmethod
    def _visit_assignment_minus_statement(self, node: AssignmentMinusStatement):
        pass

    @abstractmethod
    def _visit_assignment_multiply_statement(self, node: AssignmentMultiplyStatement):
        pass

    @abstractmethod
    def _visit_assignment_divide_statement(self, node: AssignmentDivideStatement):
        pass

    @abstractmethod
    def _visit_assignment_modulo_statement(self, node: AssignmentModuloStatement):
        pass

    @abstractmethod
    def _visit_try_catch_statement(self, node: TryCatchStatement):
        pass

    @abstractmethod
    def _visit_throw_statement(self, node: ThrowStatement):
        pass

    @abstractmethod
    def _visit_break_statement(self, node: BreakStatement):
        pass

    @abstractmethod
    def _visit_continue_statement(self, node: ContinueStatement):
        pass

    @abstractmethod
    def _visit_argument(self, node: Argument):
        pass
