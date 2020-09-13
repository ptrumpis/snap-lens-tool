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

type_to_symbol = {
    Type.INT8: "b",
    Type.UINT8: "B",
    Type.INT16: "h",
    Type.UINT16: "H",
    Type.FLOAT32: "f",
    Type.FLOAT16: "f2"
}

class Mesh:
    def __init__(self):
        self.vertices = None
        self.indices = None

class MeshParser(ResourceParser):
    def parse(self):
        json = super().parse()

        vert_dtype, attributes = MeshParser.build_dtype(json)

        reader = BinaryReader(json["vertices"].as_bytes())
        parsed_verts = reader.read(vert_dtype, -1)
        mesh = Mesh()
        mesh.vertices = {}
        for i, attr in zip(range(len(attributes)), attributes):
            mesh.vertices[attr["semantic"]] = [vert[i] for vert in parsed_verts]

        face_dtype = [("face", ("H", 3))]
        reader = BinaryReader(json["indices"].as_bytes())
        parsed_faces = reader.read(face_dtype, -1)
        mesh.indices = [face[0] for face in parsed_faces]

        return mesh

    def build_dtype(json):
        attributes = list(json["vertexlayout"]["attributes"].values())
        attributes.sort(key=lambda attr: attr["index"])
        vert_dtype = []
        for attr in attributes:
            name = attr["semantic"]
            comp_type = Type(attr["type"])
            comp_count = attr["componentCount"]
            type_symbol = type_to_symbol[comp_type]
            vert_dtype.append((name, (type_symbol, comp_count)))
        return vert_dtype, attributes
