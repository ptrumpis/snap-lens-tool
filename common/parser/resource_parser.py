from enum import Enum
import numpy as np
from ..util.binary_reader import BinaryReader, BinaryReaderError
from ..types.enums import FieldType

class JsonResourceBuilder:
    def __init__(self):
        self.root = {}
        self.stack = [self.root]
        self.arrays = []
        self.parent = self.root

    def start_block(self, key=None):
        block = {}
        if key is None:
            self.parent[len(self.parent)] = block
        else:
            self.parent[key] = block
        self.stack.append(self.parent)
        self.parent = block

    def finish_block(self):
        self.parent = self.stack.pop()

    def add_value(self, key, value, *args):
        self.parent[key] = value

    def add_array(self, key, offset, size):
        arr_data = ArrayData()
        self.parent[key] = arr_data
        self.arrays.append((offset, size, arr_data))

    def infer_arrays(self, data, header_size):
        self.arrays.sort(key=lambda x: x[0])
        for (offset, size, arr), i in zip(self.arrays, range(len(self.arrays))):
            if i == len(self.arrays) - 1:
                true_size = len(data) - header_size - offset
            else:
                true_size = self.arrays[i+1][0] - offset

            arr.data = data[header_size+offset:header_size+offset+true_size]

    def finished(self):
        return len(self.stack) == 0

class ArrayData:
    def __init__(self, data=None):
        self.data = data

    def as_bytes(self):
        return self.data

    def as_strings(self):
        reader = BinaryReader(self.data)
        strings = []
        while not reader.finished():
            string_len = reader.read_uint32()
            strings.append(reader.read_string(string_len))
        return strings

    def as_dtype(self, dtype):
        reader = BinaryReader(self.data)
        count = len(self.data) // np.dtype(dtype).itemsize
        return reader.read(dtype, count)

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

    def _parse_values(self, builder):
        if self.version == 2:
            strings = self._parse_strings()

        while not builder.finished():
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
                builder.start_block(label)
            elif tag == FieldType.END:
                builder.finish_block()
            elif tag == FieldType.BOOL:
                value = self.reader.read_bool8()
                builder.add_value(label, value, "bool8")
            elif tag == FieldType.BYTES:
                offset = self.reader.read_uint32()
                builder.add_array(label, offset, size)
            elif tag == FieldType.DOUBLE:
                value = self.reader.read_float64()
                builder.add_value(label, value, "float64")
            elif tag == FieldType.FLOAT:
                value = self.reader.read_float32()
                builder.add_value(label, value, "float32")
            elif tag == FieldType.INT32:
                value = self.reader.read_int32()
                builder.add_value(label, value, "int32")
            elif tag == FieldType.INT64:
                value = self.reader.read_int64()
                builder.add_value(label, value, "int64")
            elif tag == FieldType.MAT2:
                value = self.reader.read_mat2()
                builder.add_value(label, value, "mat2f", "float32")
            elif tag == FieldType.MAT3:
                value = self.reader.read_mat3()
                builder.add_value(label, value, "mat3f", "float32")
            elif tag == FieldType.MAT4:
                value = self.reader.read_mat4()
                builder.add_value(label, value, "mat4f", "float32")
            elif tag == FieldType.QUAT:
                value = self.reader.read_quat()
                builder.add_value(label, value, "quatf", "float32")
            elif tag == FieldType.STRING:
                string_index = self.reader.read_uint32()
                value = strings[string_index-1]
                builder.add_value(label, value, "string")
            elif tag == FieldType.STRINGV1:
                string_len = self.reader.read_uint32()
                value = self.reader.read_string(string_len)
                builder.add_value(label, value, "string")
            elif tag == FieldType.UINT32:
                value = self.reader.read_uint32()
                builder.add_value(label, value, "uint32")
            elif tag == FieldType.UINT64:
                value = self.reader.read_uint64()
                builder.add_value(label, value, "uint64")
            elif tag == FieldType.VEC2F:
                value = self.reader.read_vec2f()
                builder.add_value(label, value, "vec2f", "float32")
            elif tag == FieldType.VEC3F:
                value = self.reader.read_vec3f()
                builder.add_value(label, value, "vec3f", "float32")
            elif tag == FieldType.VEC4F:
                value = self.reader.read_vec4f()
                builder.add_value(label, value, "vec4f", "float32")
            elif tag == FieldType.VEC4B:
                value = self.reader.read_vec4b()
                builder.add_value(label, value, "vec4b", "int8")
        builder.infer_arrays(self.reader.data, self.header_size)
        return builder.root

    def parse(self, builder_cls=JsonResourceBuilder):
        if self.reader is None:
            with open(self.filename, "rb") as f:
                data = f.read()
            self.reader = BinaryReader(data)
        self.version = self.reader.read_uint32()
        if self.version not in [1, 2]:
            raise NotImplementedError(f"Resource version {self.version} not supported")
        self.header_size = self.reader.read_uint32()
        self.reader.seek(0x48)
        self.json = self._parse_values(builder_cls())
        return self.json

