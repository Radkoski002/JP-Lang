import sys

from lexer.helpers import single_char_tokens
from lexer.lexer_class import Lexer
from utils.stream_provider_class import StreamProvider


def main():
    if len(sys.argv) == 1:
        print(":" in single_char_tokens)
        print(single_char_tokens[":"])

        print("Please provide a file to read from")
        return
    if len(sys.argv) == 2:
        # stream_provider = StreamProvider(sys.argv[1])
        stream_provider = StreamProvider("<= >= ==", is_file=False)
        lexer = Lexer(stream_provider)
        lexer.build_next_token()
        print(lexer.current_token.type)


if __name__ == "__main__":
    main()
