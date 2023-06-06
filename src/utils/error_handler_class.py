class ErrorHandler:
    def __init__(self):
        self.errors = []

    def add_error(self, error: Exception):
        self.errors.append(error)

    def raise_critical_error(self, error: Exception):
        self.add_error(error)
        self.raise_errors()

    def has_errors(self):
        return len(self.errors) > 0

    def raise_errors(self):
        for error in self.errors:
            print(error)
