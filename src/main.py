from asyncio import sleep
import sys
import io
from lexer.lexer_error_class import LEXER_ERROR_TYPES
from utils.error_handler_class import ErrorHandler

from lexer.lexer_class import Lexer


def main():
    error_handler = ErrorHandler()
    if len(sys.argv) == 1:
        with io.StringIO(
            "1.11111111111111111111111111111111111111111111111"
        ) as stream_provider:
            lexer = Lexer(stream_provider, error_handler)
            while lexer.build_next_token():
                print(lexer.current_token.type)
                print(lexer.current_token.value)
                print(lexer.current_token.position)
        for error in error_handler.errors:
            print(error.type == LEXER_ERROR_TYPES.UNKNOWN_TOKEN)
    if len(sys.argv) == 2:
        with open(sys.argv[1], "r") as stream_provider:
            lexer = Lexer(stream_provider, error_handler)
            while lexer.build_next_token():
                pass


if __name__ == "__main__":
    main()
