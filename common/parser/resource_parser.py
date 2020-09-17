from enum import Enum
import numpy as np
from ..util.binary_reader import BinaryReader
from ..types.enums import FieldType

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

            tag = FieldType(self.reader.read_uint16())
            if tag != FieldType.END:
                if self.version == 1:
                    label_len = self.reader.read_uint32()
                    label = self.reader.read_string(label_len) if label_len > 0 else None
                elif self.version == 2:
                    label_index = self.reader.read_uint32()
                    label = strings[label_index-1] if label_index > 0 else None
                size = self.reader.read_uint32()

            if tag == FieldType.BEGIN:
                new_dict = {}
                dict_stack.append(new_dict)
                if label is None:
                    cur_dict[len(cur_dict)] = new_dict
                else:
                    cur_dict[label] = new_dict
            elif tag == FieldType.END:
                dict_stack.pop()
            elif tag == FieldType.BOOL:
                cur_dict[label] = self.reader.read_bool8()
            elif tag == FieldType.BYTES:
                offset = self.reader.read_uint32()
                cur_dict[label] = ArrayData(byte_pool, offset, size, self.reader.endianness)
            elif tag == FieldType.DOUBLE:
                cur_dict[label] = self.reader.read_float64()
            elif tag == FieldType.FLOAT:
                cur_dict[label] = self.reader.read_float32()
            elif tag == FieldType.INT32:
                cur_dict[label] = self.reader.read_int32()
            elif tag == FieldType.INT64:
                cur_dict[label] = self.reader.read_int64()
            elif tag == FieldType.MAT2:
                cur_dict[label] = self.reader.read_mat2()
            elif tag == FieldType.MAT3:
                cur_dict[label] = self.reader.read_mat3()
            elif tag == FieldType.MAT4:
                cur_dict[label] = self.reader.read_mat4()
            elif tag == FieldType.QUAT:
                cur_dict[label] = self.reader.read_quat()
            elif tag == FieldType.STRING:
                string_index = self.reader.read_uint32()
                string = strings[string_index-1]
                cur_dict[label] = string
            elif tag == FieldType.STRINGV1:
                string_len = self.reader.read_uint32()
                string = self.reader.read_string(string_len)
                cur_dict[label] = string
            elif tag == FieldType.UINT32:
                cur_dict[label] = self.reader.read_uint32()
            elif tag == FieldType.UINT64:
                cur_dict[label] = self.reader.read_uint64()
            elif tag == FieldType.VEC2F:
                cur_dict[label] = self.reader.read_vec2f()
            elif tag == FieldType.VEC3F:
                cur_dict[label] = self.reader.read_vec3f()
            elif tag == FieldType.VEC4F:
                cur_dict[label] = self.reader.read_vec4f()
            elif tag == FieldType.VEC4B:
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

