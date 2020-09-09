from enum import Enum
from .resource_parser import ResourceParser
from .binary_reader import BinaryReader

class Type(Enum):
    INT8 = 1
    UINT8 = 2
    INT16 = 3
    UINT16 = 4
    FLOAT32 = 5
    FLOAT16 = 6

class MeshParser(ResourceParser):
    def parse(self):
        json = super().parse()

        attributes = list(json["vertexlayout"]["attributes"].values())
        attributes.sort(key=lambda attr: attr["index"])

        vertices = {attr["semantic"]: [] for attr in attributes}
        reader = BinaryReader(json["vertices"])
        while not reader.finished():
            for attr in attributes:
                if Type(attr["type"]) == Type.INT8:
                    vec = tuple(reader.readInt8() for _ in range(attr["componentCount"]))
                elif Type(attr["type"]) == Type.UINT8:
                    vec = tuple(reader.readUInt8() for _ in range(attr["componentCount"]))
                elif Type(attr["type"]) == Type.INT16:
                    vec = tuple(reader.readInt16() for _ in range(attr["componentCount"]))
                elif Type(attr["type"]) == Type.UINT16:
                    vec = tuple(reader.readUInt16() for _ in range(attr["componentCount"]))
                elif Type(attr["type"]) == Type.FLOAT32:
                    vec = tuple(reader.readFloat() for _ in range(attr["componentCount"]))
                elif Type(attr["type"]) == Type.FLOAT16:
                    vec = tuple(reader.readFloat16() for _ in range(attr["componentCount"]))
                else:
                    raise NotImplementedError()
                vertices[attr["semantic"]].append(vec)

        indices = []
        reader = BinaryReader(json["indices"])
        while not reader.finished():
            face = reader.read("H", 3)
            indices.append(face)

        return vertices, indices
