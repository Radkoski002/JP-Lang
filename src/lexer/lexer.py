def is_identifier_first_char(char: str) -> bool:
    return char.isalpha() or char == "_"


def is_identifier_char(char: str) -> bool:
    return is_identifier_first_char(char) or char.isdigit()


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            pass

    def skip_comment(self):
        if self.current_char == "#":
            while self.current_char is not None and self.current_char != "\n":
                pass

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
