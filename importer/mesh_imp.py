import bpy
import os.path
from ..parser.mesh_parser import MeshParser

class MeshImporter:
    def __init__(self, filename, operator):
        self.filename = filename
        self.operator = operator

    def do_import(self):
        self._import_mesh()

    def create_mesh(self, mesh, name):
        bpy_mesh = bpy.data.meshes.new(name)
        bpy_mesh.from_pydata(mesh.vertices["position"], [], mesh.indices)
        if "normal" in mesh.vertices:
            bpy_mesh.use_auto_smooth = True
            bpy_mesh.normals_split_custom_set_from_vertices(mesh.vertices["normal"])
        if "texture0" in mesh.vertices:
            uvlayer = bpy_mesh.uv_layers.new()
            bpy_mesh.uv_layers.active = uvlayer
            for face in bpy_mesh.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    uvlayer.data[loop_idx].uv = mesh.vertices["texture0"][vert_idx]
            bpy_mesh.calc_tangents(uvmap=uvlayer.name)
        bpy_mesh.update()
        return bpy_mesh

    def create_object(self, bpy_mesh, name):
        bpy_object = bpy.data.objects.new(name, bpy_mesh)
        bpy.context.collection.objects.link(bpy_object)
        return bpy_object

    def _import_mesh(self):
        parser = MeshParser(self.filename)
        mesh = parser.parse()
        name = os.path.splitext(os.path.basename(self.filename))[0]
        bpy_mesh = self.create_mesh(mesh, name)
        bpy_object = self.create_object(bpy_mesh, name)

