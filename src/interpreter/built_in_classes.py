from interpreter.base_datatypes import Int


class Array:
    def __init__(self, value: list[any]):
        self._value = value

    def add(self, value: any):
        self._value.append(value)

    def remove(self, value: any):
        self._value.remove(value)

    def removeAt(self, index: Int):
        self._value.pop(index._value)

    def clear(self):
        self._value.clear()

    def get(self, index: Int):
        return self._value[index._value]

    def set(self, index: Int, value: any):
        self._value[index._value] = value

    def size(self):
        return Int(len(self._value))

    def contains(self, value: any):
        return value in self._value

    def indexOf(self, value: any):
        return self._value.index(value)

    def __str__(self) -> str:
        return "[" + ", ".join([str(x) for x in self._value]) + "]"


class Student:
    def __init__(self, name, surname, age) -> None:
        self.name = name
        self.surname = surname
        self.age = age
        self._value = self

    def __str__(self) -> str:
        return f"Student - {self.name} {self.surname} {self.age}"
