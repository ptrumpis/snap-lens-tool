from enum import Enum
import numpy as np
from ..util.binary_reader import BinaryReader

class Type(Enum):
    BEGIN = 0x0e
    END = 0x00
    BOOL = 0x01
    BYTES = 0x0f
    DOUBLE = 0x05
    FLOAT = 0x03
    INT32 = 0x02
    INT64 = 0x10
    MAT2 = 0x16
    MAT3 = 0x0a
    MAT4 = 0x0b
    QUAT = 0x0c
    STRING = 0x18
    STRINGV1 = 0x04
    UINT32 = 0x06
    UINT64 = 0x11
    VEC2F = 0x07
    VEC3F = 0x08
    VEC4F = 0x09
    VEC4B = 0x17

class ArrayData:
    def __init__(self, data, offset, size, endianness):
        self.reader = BinaryReader(data, endianness)
        self.reader.seek(offset)
        self.size = size

    def as_bytes(self):
        return self.reader.read_bytes(self.size)

    def as_strings(self):
        strings = []
        for i in range(self.size):
            string_len = self.reader.read_uint32()
            strings.append(self.reader.read_string(string_len))
        return strings

    def as_dtype(self, dtype):
        count = self.size // np.dtype(dtype).itemsize
        return self.reader.read(dtype, count)

class ResourceParser:
    def __init__(self, filename, data=None):
        self.filename = filename
        self.reader = data and BinaryReader(data)
        self.version = None
        self.header_size = None
        self.json = None

    def _parse_strings(self):
        string_count = self.reader.read_uint32()
        strings = []
        for i in range(string_count):
            str_len = self.reader.read_uint32()
            strings.append(self.reader.read_string(str_len))
        return strings

    def _parse_values(self):
        if self.version == 2:
            strings = self._parse_strings()

        root_dict = {}
        dict_stack = [root_dict]
        byte_pool = self.reader.data[self.header_size:]

        while len(dict_stack) > 0:
            cur_dict = dict_stack[-1]

            tag = Type(self.reader.read_uint16())
            if tag != Type.END:
                if self.version == 1:
                    label_len = self.reader.read_uint32()
                    label = self.reader.read_string(label_len) if label_len > 0 else None
                elif self.version == 2:
                    label_index = self.reader.read_uint32()
                    label = strings[label_index-1] if label_index > 0 else None
                size = self.reader.read_uint32()

            if tag == Type.BEGIN:
                new_dict = {}
                dict_stack.append(new_dict)
                if label is None:
                    cur_dict[len(cur_dict)] = new_dict
                else:
                    cur_dict[label] = new_dict
            elif tag == Type.END:
                dict_stack.pop()
            elif tag == Type.BOOL:
                cur_dict[label] = self.reader.read_bool8()
            elif tag == Type.BYTES:
                offset = self.reader.read_uint32()
                cur_dict[label] = ArrayData(byte_pool, offset, size, self.reader.endianness)
            elif tag == Type.DOUBLE:
                cur_dict[label] = self.reader.read_float64()
            elif tag == Type.FLOAT:
                cur_dict[label] = self.reader.read_float32()
            elif tag == Type.INT32:
                cur_dict[label] = self.reader.read_int32()
            elif tag == Type.INT64:
                cur_dict[label] = self.reader.read_int64()
            elif tag == Type.MAT2:
                cur_dict[label] = self.reader.read_mat2()
            elif tag == Type.MAT3:
                cur_dict[label] = self.reader.read_mat3()
            elif tag == Type.MAT4:
                cur_dict[label] = self.reader.read_mat4()
            elif tag == Type.QUAT:
                cur_dict[label] = self.reader.read_quat()
            elif tag == Type.STRING:
                string_index = self.reader.read_uint32()
                string = strings[string_index-1]
                cur_dict[label] = string
            elif tag == Type.STRINGV1:
                string_len = self.reader.read_uint32()
                string = self.reader.read_string(string_len)
                cur_dict[label] = string
            elif tag == Type.UINT32:
                cur_dict[label] = self.reader.read_uint32()
            elif tag == Type.UINT64:
                cur_dict[label] = self.reader.read_uint64()
            elif tag == Type.VEC2F:
                cur_dict[label] = self.reader.read_vec2f()
            elif tag == Type.VEC3F:
                cur_dict[label] = self.reader.read_vec3f()
            elif tag == Type.VEC4F:
                cur_dict[label] = self.reader.read_vec4f()
            elif tag == Type.VEC4B:
                cur_dict[label] = self.reader.read_vec4b()
        return root_dict

    def parse(self):
        if self.reader is None:
            with open(self.filename, "rb") as f:
                data = f.read()
            self.reader = BinaryReader(data)
        self.version = self.reader.read_uint32()
        if self.version not in [1, 2]:
            raise NotImplementedError(f"Resource version {self.version} not supported")
        self.header_size = self.reader.read_uint32()
        self.reader.seek(0x48)
        self.json = self._parse_values()
        return self.json

