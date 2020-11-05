import bpy
import os.path
from .base_imp import BaseImporter
from ..common.parser.mesh_parser import MeshParser

class MeshImporter(BaseImporter):
    def __init__(self, filename, operator, data=None):
        super().__init__(filename, operator, data)

    def do_import(self):
        parser = MeshParser(self.filename, data=self.data)
        mesh = parser.parse()
        name = os.path.splitext(os.path.basename(self.filename))[0]
        bpy_mesh = self.create_mesh(mesh, name)
        bpy_obj = self.create_object(bpy_mesh, name)
        if len(mesh.bones) > 0:
            bpy_arm_obj = self.create_skeleton(mesh.bones, name + "_arm")
            for bone in mesh.bones:
                vg = bpy_obj.vertex_groups.get(bone.name)
                if vg is None:
                    vg = bpy_obj.vertex_groups.new(name=bone.name)
                for i, w in zip(bone.indices, bone.weights):
                    vg.add((int(i),), w, "REPLACE")
            bpy_mod = bpy_obj.modifiers.new(name + "_arm", "ARMATURE")
            bpy_mod.object = bpy_arm_obj
            bpy_arm_obj.parent = bpy_obj
        bpy_obj.matrix_world = self.scale_matrix @ self.conversion_matrix @ bpy_obj.matrix_world

