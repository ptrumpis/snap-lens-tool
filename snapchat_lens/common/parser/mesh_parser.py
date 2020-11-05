import numpy as np
from .resource_parser import ResourceParser
from ..util.binary_reader import BinaryReader
from ..types.enums import AttrType, attr_type_to_symbol

class Bone:
    def __init__(self, name, invmat):
        self.name = name
        self.invmat = invmat
        self.indices = []
        self.weights = []

class Mesh:
    def __init__(self):
        self.vertices = {}
        self.indices = []
        self.bones = []

class MeshParser(ResourceParser):
    def parse(self):
        json = super().parse()

        # vertices
        vert_dtype, attributes = MeshParser.build_dtype(json)
        reader = BinaryReader(json["vertices"].as_bytes())
        num_verts = len(reader.data) // np.dtype(vert_dtype).itemsize
        parsed_verts = reader.read(vert_dtype, num_verts)
        mesh = Mesh()
        for i, attr in zip(range(len(attributes)), attributes):
            mesh.vertices[attr["semantic"]] = [vert[i] for vert in parsed_verts]

        # faces
        face_dtype = [("face", ("H", 3))]
        reader = BinaryReader(json["indices"].as_bytes())
        num_faces = len(reader.data) // np.dtype(face_dtype).itemsize
        parsed_faces = reader.read(face_dtype, num_faces)
        mesh.indices = [face[0] for face in parsed_faces]

        # bones
        for i in range(len(json["skinbones"])):
            bone_json = json["skinbones"][i]
            invmat = bone_json["invtm"].reshape(4, 4, order="F")
            bone = Bone(bone_json["boneName"], invmat)
            mesh.bones.append(bone)

        if "rgroups" in json:
            indices_flat = np.array(mesh.indices).flat
        dups = set()
        for rgroup_json in json["rgroups"].values():
            index_offset = rgroup_json["indexOffset"]
            index_count = rgroup_json["indexCount"]
            for index in np.unique(indices_flat[index_offset:index_offset+index_count]):
                for bone_data in mesh.vertices["boneData"][index]:
                    weight = bone_data - np.floor(bone_data)
                    bone_map_index = int(bone_data)
                    bone_index = rgroup_json["bonesremaping"][bone_map_index]["boneIndex"]
                    if weight != 0 and bone_index != 0 and (bone_index, index) not in dups:
                        dups.add((bone_index, index))
                        mesh.bones[bone_index].weights.append(weight)
                        mesh.bones[bone_index].indices.append(index)

        return mesh

    # create numpy dtype from mesh vertexlayout.
    # return dtype and attributes json sorted by index
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
