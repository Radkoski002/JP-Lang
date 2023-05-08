class Position:
    def __init__(self, line, column):
        self.line = line
        self.column = column

    def __str__(self):
        return f"Line: {self.line} Column: {self.column}"
