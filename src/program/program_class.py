from parser.statement_classes import FunctionDef


class Program:
    def __init__(self, functions: dict[str, FunctionDef]) -> None:
        self.functions = functions

    def __eq__(self, other):
        return self.functions == other.functions

    def accept(self, visitor):
        return visitor.visit_program(self)
