import numpy as np
from .resource_parser import ResourceParser
from ..util.binary_reader import BinaryReader
from ..types.enums import AttrType, attr_type_to_symbol

class Mesh:
    def __init__(self):
        self.vertices = None
        self.indices = None

class MeshParser(ResourceParser):
    def parse(self):
        json = super().parse()

        vert_dtype, attributes = MeshParser.build_dtype(json)

        reader = BinaryReader(json["vertices"].as_bytes())
        num_verts = len(reader.data) // np.dtype(vert_dtype).itemsize
        parsed_verts = reader.read(vert_dtype, num_verts)
        mesh = Mesh()
        mesh.vertices = {}
        for i, attr in zip(range(len(attributes)), attributes):
            mesh.vertices[attr["semantic"]] = [vert[i] for vert in parsed_verts]

        face_dtype = [("face", ("H", 3))]
        reader = BinaryReader(json["indices"].as_bytes())
        num_faces = len(reader.data) // np.dtype(face_dtype).itemsize
        parsed_faces = reader.read(face_dtype, num_faces)
        mesh.indices = [face[0] for face in parsed_faces]

        return mesh

    def build_dtype(json):
        attributes = list(json["vertexlayout"]["attributes"].values())
        attributes.sort(key=lambda attr: attr["index"])
        vert_dtype = []
        for attr in attributes:
            name = attr["semantic"]
            comp_type = AttrType(attr["type"])
            comp_count = attr["componentCount"]
            type_symbol = attr_type_to_symbol[comp_type]
            vert_dtype.append((name, (type_symbol, comp_count)))
        return vert_dtype, attributes
