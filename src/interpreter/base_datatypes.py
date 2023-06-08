from functools import singledispatch


class BaseDataType:
    def __init__(self, value: any):
        self._value = value

    def __str__(self) -> str:
        return str(self._value)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, BaseDataType):
            return self._value == __value._value
        return self._value == __value


class String(BaseDataType):
    def __init__(self, value: str):
        super().__init__(str(value))


class Int(BaseDataType):
    def __init__(self, value: int):
        super().__init__(int(value))


class Float(BaseDataType):
    def __init__(self, value: float):
        super().__init__(float(value))


class Boolean(BaseDataType):
    def __init__(self, value: bool):
        super().__init__(value)


class Null(BaseDataType):
    def __init__(self):
        super().__init__(None)

    def __str__(self) -> str:
        return "null"


class LiteralConstructor:
    def __init__(self) -> None:
        self.get = singledispatch(self.get)
        self.get.register(str, self._get_string)
        self.get.register(int, self._get_integer)
        self.get.register(float, self._get_float)
        self.get.register(bool, self._get_boolean)
        self.get.register(type(None), self._get_null)

    def get(self, s):
        raise TypeError("This type isn't base datatype: {}".format(type(s)))

    def _get_string(self, value: str) -> String:
        return String(value)

    def _get_integer(self, value: int) -> Int:
        return Int(value)

    def _get_float(self, value: float) -> Float:
        return Float(value)

    def _get_boolean(self, value: bool) -> Boolean:
        return Boolean(value)

    def _get_null(self, value: None) -> Null:
        return Null()
