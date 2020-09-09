import numpy as np

class BinaryReader:
    def __init__(self, data, endianness="<"):
        self.data = data
        self.endianness = endianness
        self.offset = 0

    def read(self, fmt, count=1):
        dt = np.dtype(fmt).newbyteorder(self.endianness)
        value = np.frombuffer(self.data, dt, count, self.offset)
        self.offset += dt.itemsize * count
        return value

    def readInt8(self):
        return self.read("b")[0]

    def readUInt8(self):
        return self.read("B")[0]

    def readUInt16(self):
        return self.read("h")[0]

    def readUInt16(self):
        return self.read("H")[0]

    def readInt32(self):
        return self.read("i")[0]

    def readUInt32(self):
        return self.read("I")[0]

    def readInt64(self):
        return self.read("q")[0]

    def readUInt64(self):
        return self.read("Q")[0]

    def readFloat(self):
        return self.read("f")[0]

    def readDouble(self):
        return self.read("d")[0]

    def readBool(self):
        return self.read("?")[0]

    def readVec2f(self):
        return self.read("f", 2)

    def readVec3f(self):
        return self.read("f", 3)

    def readVec4f(self):
        return self.read("f", 4)

    def readVec4b(self):
        return self.read("b", 4)

    def readQuat(self):
        return self.read("f", 4)

    def readMat2(self):
        return self.read("f", 4)

    def readMat3(self):
        return self.read("f", 9)

    def readMat4(self):
        return self.read("f", 16)

    def readString(self, n):
        return self.readBytes(n).decode()

    def readBytes(self, n):
        value = self.data[self.offset:self.offset+n]
        self.offset += n
        return value

    def readFloat16(self):
        return self.read("f2")[0]

    def seek(self, offset):
        self.offset = offset
        if self.offset < 0 or self.offset > len(self.data):
            raise IndexError()

    def skip(self, offset):
        self.seek(self.offset + offset)

    def finished(self):
        return self.offset >= len(self.data)

