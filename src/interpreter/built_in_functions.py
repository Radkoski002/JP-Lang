from __future__ import annotations
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

from interpreter.interpreter_error_classes import *
from interpreter.built_in_classes import *
from interpreter.base_datatypes import *

if TYPE_CHECKING:
    from interpreter.visitor_interface import IVisitor


class BuiltInFunction(ABC):
    name: str
    argc: int | None = None

    @abstractmethod
    def execute(self, args):
        pass

    def _get_optional_values(self, args: list[any]):
        return [Null()] * (self.argc - len(args))

    def accept(self, visitor: IVisitor):
        visitor.visit(self)


class PrintFunction(BuiltInFunction):
    def __init__(self):
        self.name = "print"

    def execute(self, args: list[any]):
        print(*args, end="", sep="")


class Input(BuiltInFunction):
    def __init__(self):
        self.name = "input"
        self.argc = 0

    def execute(self, args):
        return input()


class InputStringFunction(BuiltInFunction):
    def __init__(self):
        self.name = "inputString"
        self.argc = 0

    def execute(self, args):
        return input()


class InputIntFunction(BuiltInFunction):
    def __init__(self):
        self.name = "inputInt"
        self.argc = 0

    def execute(self, args):
        return int(input())


class InputFloatFunction(BuiltInFunction):
    def __init__(self):
        self.name = "inputFloat"
        self.argc = 0

    def execute(self, args):
        return float(input())


class ArrayConstructor(BuiltInFunction):
    def __init__(self):
        self.name = "Array"

    def execute(self, args: list[any]):
        return Array(args)


class StudentConstructor(BuiltInFunction):
    def __init__(self):
        self.name = "Student"
        self.argc = 3

    def execute(self, args: list[any]):
        return Student(*args, *self._get_optional_values(args))


class ErrorConstructor(BuiltInFunction):
    def __init__(self, constructor: Error = Error):
        self._constructor = constructor
        self.name = constructor.__name__

    def execute(self, args: list[any]):
        return self._constructor(*args)


class TypeCastFunction(BuiltInFunction):
    def __init__(self, constructor: BaseDataType):
        self._type_constructor = constructor
        self.name = type(constructor).__name__
        self.argc = 1

    def execute(self, args: list[any]):
        return self._type_constructor(args[0]._value)


def get_built_in_functions() -> dict[str, BuiltInFunction]:
    return {
        "print": PrintFunction(),
        "inputString": InputStringFunction(),
        "inputInt": InputIntFunction(),
        "inputFloat": InputFloatFunction(),
        "Array": ArrayConstructor(),
        "Student": StudentConstructor(),
        "Error": ErrorConstructor(),
        "ArgumentError": ErrorConstructor(ArgumentError),
        "TypeError": ErrorConstructor(TypeError),
        "ExpressionError": ErrorConstructor(ExpressionError),
        "VariableError": ErrorConstructor(VariableError),
        "RuntimeError": ErrorConstructor(RuntimeError),
        "PropertyError": ErrorConstructor(PropertyError),
        "Int": TypeCastFunction(Int),
        "Float": TypeCastFunction(Float),
        "String": TypeCastFunction(String),
        "Boolean": TypeCastFunction(Boolean),
        "Null": TypeCastFunction(Null),
    }
