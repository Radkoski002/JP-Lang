class ErrorHandler:
    def __init__(self):
        self.errors = []

    def add_error(self, error: Exception):
        self.errors.append(error)

    def has_errors(self):
        return len(self.errors) > 0

    def raise_errors(self):
        if self.has_errors():
            raise Exception(self.errors)
