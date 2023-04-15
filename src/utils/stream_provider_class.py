import io


class StreamProvider:
    def __init__(self, stream_source: str, is_file: bool = True):
        if is_file:
            self.stream = open(stream_source, "r")
        else:
            self.stream = io.StringIO(stream_source)

    def __del__(self):
        self.stream.close()

    def get_char(self):
        return self.stream.read(1)
