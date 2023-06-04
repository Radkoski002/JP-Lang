class FunctionScope:
    def __init__(self):
        self.variables: dict[str, any] = {}
        self.variables_stack: list[str] = []
        self.variables_in_scope: list[int] = []
        self.current_scope_variables: int = 0

    def __expect_variable(self, name: str) -> any:
        if not name in self.variables:
            raise Exception(f"Variable {name} is not defined")

    def __add_variable_to_scope(self, name: str, value: any = None):
        self.current_scope_variables += 1
        self.variables_stack.append(name)
        self.variables[name] = value

    def get_variable(self, name: str) -> any:
        if not name in self.variables:
            self.__add_variable_to_scope(name)
        return self.variables[name]

    def expect_and_get_variable(self, name: str) -> any:
        self.__expect_variable(name)
        return self.get_variable(name)

    def set_variable(self, name: str, value: any):
        if not name in self.variables:
            self.__add_variable_to_scope(name)
        self.variables[name] = value

    def expect_and_set_variable(self, name: str, value: any = None) -> any:
        self.__expect_variable(name)
        self.variables[name] = value

    def enter_scope(self):
        self.variables_in_scope.append(self.current_scope_variables)
        self.current_scope_variables = 0

    def exit_scope(self):
        for _ in range(self.current_scope_variables):
            variable = self.variables_stack.pop()
            del self.variables[variable]
        self.current_scope_variables = self.variables_in_scope.pop()
