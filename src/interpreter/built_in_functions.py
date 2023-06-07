from __future__ import annotations
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

from interpreter.interpreter_error_classes import *
from interpreter.built_in_classes import *

if TYPE_CHECKING:
    from interpreter.visitor_interface import IVisitor


class BuiltInFunction(ABC):
    name: str
    argc: int | None = None

    @abstractmethod
    def execute(self, args):
        pass

    def _get_optional_values(self, args: list[any]):
        return [None] * (self.argc - len(args))

    def accept(self, visitor: IVisitor):
        visitor.visit(self)


class PrintFunction(BuiltInFunction):
    def __init__(self):
        self.name = "print"

    def execute(self, args: list[any]):
        print(*args, end="", sep="")


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


def get_built_in_functions() -> dict[str, BuiltInFunction]:
    return {
        "print": PrintFunction(),
        "Array": ArrayConstructor(),
        "Student": StudentConstructor(),
        "Error": ErrorConstructor(),
        "ArgumentError": ErrorConstructor(ArgumentError),
        "TypeError": ErrorConstructor(TypeError),
        "ExpressionError": ErrorConstructor(ExpressionError),
        "VariableError": ErrorConstructor(VariableError),
        "RuntimeError": ErrorConstructor(RuntimeError),
        "PropertyError": ErrorConstructor(PropertyError),
    }
