from utils.position_class import Position


class Array:
    def __init__(self, value: list[any]):
        self._value = value

    def add(self, value: any):
        self._value.append(value)

    def remove(self, value: any):
        self._value.remove(value)

    def removeAt(self, index: int):
        self._value.pop(index)

    def clear(self):
        self._value.clear()

    def get(self, index: int):
        return self._value[index]

    def set(self, index: int, value: any):
        self._value[index] = value

    def size(self):
        return len(self._value)

    def contains(self, value: any):
        return value in self._value

    def indexOf(self, value: any):
        return self._value.index(value)

    def __str__(self) -> str:
        return str(self._value)


class Student:
    def __init__(self, name, surname, age) -> None:
        self.name = name
        self.surname = surname
        self.age = age
