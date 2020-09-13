import numpy as np

class BinaryWriter:
    def __init__(self, endianness="<"):
        self.endianness = endianness
        self.data = []
        self.size = 0

    def to_file(self, filename):
        joined_data = self.get_bytes()
        with open(filename, "wb") as f:
            f.write(joined_data)

    def get_bytes(self):
        return b"".join(self.data)

    def write(self, np_value):
        b = np_value.tobytes()
        self.data.append(b)
        self.size += len(b)
        return len(b)

    def write_uint32(self, value):
        return self.write(np.uint32(value))

    def write_bytes(self, value):
        self.data.append(value)
        self.size += len(value)
        return len(value)

    def write_string(self, value):
        b = value.encode()
        self.data.append(b)
        self.size += len(b)
        return len(b)
