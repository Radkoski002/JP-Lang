class Error:
    def __init__(self, message: str, args: list[any] = None):
        self.message = message
        self.args = args


class ArgumentError(Error):
    def __init__(self, message: str, args: list[any] = None):
        super().__init__(message, args)


class TypeError(Error):
    def __init__(self, message: str, args: list[any] = None):
        super().__init__(message, args)


class ExpressionError(Error):
    def __init__(self, message: str, args: list[any] = None):
        super().__init__(message, args)


class VariableError(Error):
    def __init__(self, message: str, args: list[any] = None):
        super().__init__(message, args)


class RuntimeError(Error):
    def __init__(self, message: str, args: list[any] = None):
        super().__init__(message, args)


class PropertyError(Error):
    def __init__(self, message: str, args: list[any] = None):
        super().__init__(message, args)
