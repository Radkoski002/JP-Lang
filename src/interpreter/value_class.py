from functools import singledispatch


class Value:
    def __init__(self, value) -> None:
        self.__get_type = singledispatch(self.__get_type)
        self.__get_type.register(str, self.__get_string_type)
        self.__get_type.register(int, self.__get_int_type)
        self.__get_type.register(float, self.__get_float_type)
        self.__get_type.register(bool, self.__get_bool_type)
        self.__get_type.register(type(None), self.__get_null_type)

        self._value = value
        self._type = self.__get_type(value)

    def __get_type(self, value):
        return type(value).__name__

    def __get_string_type(self, value: str):
        return "String"

    def __get_int_type(self, value: int):
        return "Int"

    def __get_float_type(self, value: float):
        return "Float"

    def __get_bool_type(self, value: bool):
        return "Boolean"

    def __get_null_type(self, value: None):
        return "Null"

    def __str__(self) -> str:
        if self._type == "Null":
            return "null"
        return str(self._value)

    def __repr__(self) -> str:
        return str(self._value)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Value):
            return self._value == __value._value
        return self._value == __value

    def set_value(self, value: any):
        self._value = value
        self._type = self.__get_type(value)
