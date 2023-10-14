from enum import Enum


class AttrType(Enum):
    INT8 = 1
    UINT8 = 2
    INT16 = 3
    UINT16 = 4
    FLOAT32 = 5
    FLOAT16 = 6


attr_type_to_symbol = {
    AttrType.INT8: "b",
    AttrType.UINT8: "B",
    AttrType.INT16: "h",
    AttrType.UINT16: "H",
    AttrType.FLOAT32: "f",
    AttrType.FLOAT16: "f2"
}


class FieldType(Enum):
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
