from interpreter.built_in_classes import Array
from utils.position_class import Position


class Error:
    def __init__(self, position: Position, message: str, args=()):
        self.message = message
        self.args = Array(list(args))
        self.position = position
        self.error_name = self.__class__.__name__

    def __str__(self):
        args = self.args._value
        params = ", ".join([str(arg) for arg in args]) + " "
        return f"[{self.error_name}]: {self.message} {params if len(args) > 0 else ''}at line {self.position.line} column {self.position.column}"


class ArgumentError(Error):
    def __init__(self, position: Position, message: str, *args):
        super().__init__(position, message, args)


class TypeError(Error):
    def __init__(self, position: Position, message: str, *args):
        super().__init__(position, message, args)


class ExpressionError(Error):
    def __init__(self, position: Position, message: str, *args):
        super().__init__(position, message, args)


class VariableError(Error):
    def __init__(self, position: Position, message: str, *args):
        super().__init__(position, message, args)


class RuntimeError(Error):
    def __init__(self, position: Position, message: str, *args):
        super().__init__(position, message, args)


class PropertyError(Error):
    def __init__(self, position: Position, message: str, *args):
        super().__init__(position, message, args)


class FunctionError(Error):
    def __init__(self, position: Position, message: str, *args):
        super().__init__(position, message, args)


class StackOverflowError(Error):
    def __init__(self, position: Position, message: str, *args):
        super().__init__(position, message, args)


class ValueError(Error):
    def __init__(self, position: Position, message: str, *args):
        super().__init__(position, message, args)
