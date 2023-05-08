import sys
import io
from utils.error_handler_class import ErrorHandler

from lexer.lexer_class import Lexer


def main():
    error_handler = ErrorHandler()
    if len(sys.argv) == 1:
        with io.StringIO("Test string") as stream_provider:
            lexer = Lexer(stream_provider, error_handler)
    if len(sys.argv) == 2:
        with open(sys.argv[1], "r") as stream_provider:
            lexer = Lexer(stream_provider, error_handler)


if __name__ == "__main__":
    main()
