from ..util.binary_writer import BinaryWriter
from ..parser.resource_parser import Type
import numpy as np

class ResourceSerializer:
    def __init__(self):
        self.header_writer = BinaryWriter()
        self.string_writer = BinaryWriter()
        self.value_writer = BinaryWriter()
        self.array_writer = BinaryWriter()
        self.strings = {}

    def _write_string(self, label):
        if label in self.strings:
            index = self.strings[label]
        else:
            index = len(self.strings) + 1
            self.strings[label] = index
            self.string_writer.write_uint32(len(label))
            self.string_writer.write_string(label)
        self.value_writer.write_uint32(index)

    def write(self, type_enum, key, np_value):
        self.value_writer.write_uint16(type_enum.value)
        self._write_string(key)
        self.value_writer.write_uint32(np_value.nbytes)
        self.value_writer.write(np_value)

    def begin(self, key=None):
        self.value_writer.write_uint16(Type.BEGIN.value)
        if key is not None:
            self._write_string(key)
        else:
            self.value_writer.write_uint32(0)
        self.value_writer.write_uint32(0)

    def end(self):
        self.value_writer.write_uint16(Type.END.value)

    def write_array(self, key, np_value):
        self.value_writer.write_uint16(Type.BYTES.value)
        self._write_string(key)
        self.value_writer.write_uint32(np_value.nbytes)
        self.value_writer.write_uint32(self.array_writer.size)
        self.array_writer.write_bytes(np_value.tobytes())

    def write_byte_array(self, key, value):
        self.value_writer.write_uint16(Type.BYTES.value)
        self._write_string(key)
        self.value_writer.write_uint32(len(value))
        self.value_writer.write_uint32(self.array_writer.size)
        self.array_writer.write_bytes(value)

    def write_string_array(self, key, value):
        self.value_writer.write_uint16(Type.BYTES.value)
        self._write_string(key)
        self.value_writer.write_uint32(len(value))
        self.value_writer.write_uint32(self.array_writer.size)
        for string in value:
            self.array_writer.write_uint32(len(string))
            self.array_writer.write_string(string)

    def write_bool(self, key, value):
        self.write(Type.BOOL, key, np.bool8(value))

    def write_float64(self):
        self.write(Type.DOUBLE, key, np.float64(value))

    def write_float32(self):
        self.write(Type.FLOAT, key, np.float32(value))

    def write_int32(self, key, value):
        self.write(Type.INT32, key, np.int32(value))

    def write_uint32(self, key, value):
        self.write(Type.UINT32, key, np.uint32(value))

    def write_int64(self, key, value):
        self.write(Type.INT64, key, np.int64(value))

    def write_uint64(self, key, value):
        self.write(Type.UINT64, key, np.uint64(value))

    def write_vec3f(self, key, value):
        self.write(Type.VEC3F, key, np.array(value, dtype=np.float32))

    def write_vec2f(self, key, value):
        self.write(Type.VEC2F, key, np.array(value, dtype=np.float32))

    def write_string(self, key, value):
        self.value_writer.write_uint16(Type.STRING.value)
        self._write_string(key)
        self.value_writer.write_uint32(4)
        self._write_string(value)

    def finalize(self):
        self.end()
        self.header_writer.write_uint32(2)
        self.header_writer.write_uint32(0x4c + self.string_writer.size + self.value_writer.size)
        self.header_writer.write_bytes(bytes(64))
        self.header_writer.write_uint32(len(self.strings))

    def get_bytes(self):
        return self.header_writer.get_bytes() + self.string_writer.get_bytes() + self.value_writer.get_bytes() + self.array_writer.get_bytes()

    def to_file(self, filename):
        joined_data = self.get_bytes()
        with open(filename, "wb") as f:
            f.write(joined_data)
