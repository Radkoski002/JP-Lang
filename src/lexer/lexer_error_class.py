from utils.position_class import Position


class LexerError(Exception):
    def __init__(self, message: str, position: Position):
        self.message = (
            f"LexerError: {message} at line {position.line}, column {position.column}"
        )
        super().__init__(self.message)

    def __str__(self):
        return self.message
