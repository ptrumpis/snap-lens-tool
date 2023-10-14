import numpy as np


class BinaryReaderError(IndexError):
    pass


class BinaryReader:
    def __init__(self, data, endianness="<"):
        self.data = data
        self.endianness = endianness
        self.offset = 0

    def read(self, fmt, count=1):
        dt = np.dtype(fmt).newbyteorder(self.endianness)
        self.check_offset(self.offset + dt.itemsize * count)
        value = np.frombuffer(self.data, dt, count, self.offset)
        self.offset += dt.itemsize * count
        return value

    def read_int8(self):
        return self.read("b")[0]

    def read_uint8(self):
        return self.read("B")[0]

    def read_int16(self):
        return self.read("h")[0]

    def read_uint16(self):
        return self.read("H")[0]

    def read_int32(self):
        return self.read("i")[0]

    def read_uint32(self):
        return self.read("I")[0]

    def read_int64(self):
        return self.read("q")[0]

    def read_uint64(self):
        return self.read("Q")[0]

    def read_float32(self):
        return self.read("f")[0]

    def read_float64(self):
        return self.read("d")[0]

    def read_bool8(self):
        return self.read("?")[0]

    def read_vec2f(self):
        return self.read("f", 2)

    def read_vec3f(self):
        return self.read("f", 3)

    def read_vec4f(self):
        return self.read("f", 4)

    def read_vec4b(self):
        return self.read("b", 4)

    def read_quat(self):
        return self.read("f", 4)

    def read_mat2(self):
        return self.read("f", 4)

    def read_mat3(self):
        return self.read("f", 9)

    def read_mat4(self):
        return self.read("f", 16)

    def read_string(self, n):
        return self.read_bytes(n).decode()

    def read_bytes(self, n):
        self.check_offset(self.offset + n)
        value = self.data[self.offset:self.offset + n]
        self.offset += n
        return value

    def read_float16(self):
        return self.read("f2")[0]

    def seek(self, offset):
        self.check_offset(offset)
        self.offset = offset

    def skip(self, offset):
        self.seek(self.offset + offset)

    def check_offset(self, offset):
        if offset < 0 or offset > len(self.data):
            raise BinaryReaderError("Binary reader out of bounds")

    def finished(self):
        return self.offset >= len(self.data)
