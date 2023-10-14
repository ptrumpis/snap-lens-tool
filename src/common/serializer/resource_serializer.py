import numpy as np

from ..types.enums import FieldType
from ..util.binary_writer import BinaryWriter


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
        self.value_writer.write_uint16(FieldType.BEGIN.value)
        if key is not None:
            self._write_string(key)
        else:
            self.value_writer.write_uint32(0)
        self.value_writer.write_uint32(0)

    def end(self):
        self.value_writer.write_uint16(FieldType.END.value)

    def write_bytes(self, key, value):
        self.value_writer.write_uint16(FieldType.BYTES.value)
        self._write_string(key)
        self.value_writer.write_uint32(len(value))
        self.value_writer.write_uint32(self.array_writer.size)
        self.array_writer.write_bytes(value)

    def write_bytes_array(self, key, value):
        self.value_writer.write_uint16(FieldType.BYTES.value)
        self._write_string(key)
        self.value_writer.write_uint32(len(value))
        self.value_writer.write_uint32(self.array_writer.size)
        for string in value:
            self.array_writer.write_bytes(string)

    def write_string_array(self, key, value):
        self.value_writer.write_uint16(FieldType.BYTES.value)
        self._write_string(key)
        self.value_writer.write_uint32(len(value))
        self.value_writer.write_uint32(self.array_writer.size)
        for string in value:
            self.array_writer.write_uint32(len(string))
            self.array_writer.write_string(string)

    def write_bool8(self, key, value):
        self.write(FieldType.BOOL, key, np.bool8(value))

    def write_float64(self, key, value):
        self.write(FieldType.DOUBLE, key, np.float64(value))

    def write_float32(self, key, value):
        self.write(FieldType.FLOAT, key, np.float32(value))

    def write_int32(self, key, value):
        self.write(FieldType.INT32, key, np.int32(value))

    def write_uint32(self, key, value):
        self.write(FieldType.UINT32, key, np.uint32(value))

    def write_int64(self, key, value):
        self.write(FieldType.INT64, key, np.int64(value))

    def write_uint64(self, key, value):
        self.write(FieldType.UINT64, key, np.uint64(value))

    def write_vec2f(self, key, value):
        self.write(FieldType.VEC2F, key, np.array(value, dtype=np.float32))

    def write_vec3f(self, key, value):
        self.write(FieldType.VEC3F, key, np.array(value, dtype=np.float32))

    def write_vec4f(self, key, value):
        self.write(FieldType.VEC4F, key, np.array(value, dtype=np.float32))

    def write_vec4b(self, key, value):
        self.write(FieldType.VEC4B, key, np.array(value, dtype=np.int8))

    def write_mat2f(self, key, value):
        self.write(FieldType.MAT2, key, np.array(value, dtype=np.float32))

    def write_mat3f(self, key, value):
        self.write(FieldType.MAT3, key, np.array(value, dtype=np.float32))

    def write_mat4f(self, key, value):
        self.write(FieldType.MAT4, key, np.array(value, dtype=np.float32))

    def write_quatf(self, key, value):
        self.write(FieldType.QUAT, key, np.array(value, dtype=np.float32))

    def write_string(self, key, value):
        self.value_writer.write_uint16(FieldType.STRING.value)
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
