class FunctionScope:
    def __init__(self):
        self.references: dict[str, str] = {}
        self.variables_stack: list[dict[str, any]] = [{}]

    def expect_and_get_variable(self, name: str) -> any:
        for variables in self.variables_stack:
            if name in variables:
                return variables[name]
        raise Exception(f"Variable {name} is not defined")

    def get_or_init_variable(self, name: str) -> any:
        for variables in self.variables_stack:
            if name in variables:
                return variables[name]
        self.variables_stack[-1][name] = None

    def set_variable(self, name: str, value: any, reference: str = False):
        if reference:
            self.references[reference] = name
        self.variables_stack[-1][name] = value

    def expect_and_set_variable(self, name: str, value: any = None) -> any:
        if self.__get_variable(name) is None:
            raise Exception(f"Variable {name} is not defined")
        self.variables_stack[-1][name] = value

    def enter_scope(self, vars: dict[str, any] = {}):
        if vars is None:
            vars = {}
        self.variables_stack.append(vars)

    def exit_scope(self):
        del self.variables_stack[-1]
