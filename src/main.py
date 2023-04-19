from asyncio import sleep
import sys
import io
from xml.sax import ErrorHandler

from lexer.lexer_class import Lexer


def main():
    if len(sys.argv) == 1:
        with io.StringIO("1 + 2") as stream_provider:
            lexer = Lexer(stream_provider)
            while lexer.build_next_token():
                sleep(1)
                print(lexer.current_token.type)
                print(lexer.current_token.value)
                print(lexer.current_token.position)

    if len(sys.argv) == 2:
        errorHandler = ErrorHandler()
        with open(sys.argv[1], "r") as stream_provider:
            lexer = Lexer(stream_provider)
            lexer.build_next_token()
            print(lexer.current_token.type)
            print(lexer.current_token.value)


if __name__ == "__main__":
    main()
