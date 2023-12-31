from interpreter.value_class import Value


class FunctionScope:
    def __init__(self):
        self.variables_stack: list[dict[str, any]] = [{}]
        self.loop_depth = 0

    def get_or_init_variable(self, name: str) -> any:
        for variables in self.variables_stack:
            if name in variables:
                return variables[name]
        self.variables_stack[-1][name] = Value(None)
        return self.variables_stack[-1][name]

    def set_or_init_variable(self, name: str, value: any):
        for variables in self.variables_stack:
            if name in variables:
                variables[name] = value
                return
        self.variables_stack[-1][name] = value

    def expect_and_set_variable(self, name: str, value: any = None) -> any:
        if self.__get_variable(name) is None:
            raise Exception(f"Variable {name} is not defined")
        for variables in self.variables_stack:
            if name in variables:
                variables[name] = value
                return
        self.variables_stack[-1][name] = value

    def enter_scope(self, vars: dict[str, any] = {}):
        if vars is None:
            vars = {}
        self.variables_stack.append(vars)

    def exit_scope(self):
        if len(self.variables_stack) != 0:
            del self.variables_stack[-1]
