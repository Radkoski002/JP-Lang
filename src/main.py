import sys
import io
from parser.parser_class import Parser
from interpreter.interpreter_class import Interpreter
from utils.error_handler_class import ErrorHandler

from lexer.lexer_class import Lexer


def main():
    error_handler = ErrorHandler()
    if len(sys.argv) == 1:
        with io.StringIO("main() {x=1;}") as stream_provider:
            lexer = Lexer(stream_provider, error_handler)
            parser = Parser(lexer)
            program = parser.parse()
    if len(sys.argv) == 2:
        with open(sys.argv[1], "r") as stream_provider:
            lexer = Lexer(stream_provider, error_handler)
            parser = Parser(lexer)
            program = parser.parse()
            if error_handler.has_errors():
                error_handler.raise_errors()
                exit(1)
            interpreter = Interpreter(error_handler)
            interpreter.visit(program)


if __name__ == "__main__":
    main()
