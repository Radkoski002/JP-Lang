from interpreter.value_class import Value


class Array:
    def __init__(self, value: list[any]):
        self._value = value

    def add(self, value: any):
        self._value.append(value)

    def remove(self, value: any):
        self._value.remove(value)

    def removeAt(self, index: Value):
        self._value.pop(index._value)

    def clear(self):
        self._value.clear()

    def get(self, index: Value):
        return self._value[index._value]

    def set(self, index: Value, value: any):
        self._value[index._value] = value

    def size(self):
        return Value(len(self._value))

    def contains(self, value: any):
        return Value(value in self._value)

    def indexOf(self, value: any):
        return Value(self._value.index(value))

    def __str__(self) -> str:
        return "[" + ", ".join([str(x) for x in self._value]) + "]"

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Array):
            return self._value == __value._value
        return False


class Student:
    def __init__(self, name, surname, age) -> None:
        self.name = name
        self.surname = surname
        self.age = age

    def __str__(self) -> str:
        return f"Student - {self.name} {self.surname} {self.age}"

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Student):
            return (
                self.name == __value.name
                and self.surname == __value.surname
                and self.age == __value.age
            )
        return False
