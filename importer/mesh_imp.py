import bpy
import os.path
from ..parser.mesh_parser import MeshParser

class MeshImporter:
    def __init__(self, filename, options):
        self.filename = filename
        self.options = options

    def do_import(self):
        self._import_mesh()

    def _import_mesh(self):
        parser = MeshParser(self.filename)
        vertices, faces = parser.parse()
        name = os.path.splitext(os.path.basename(self.filename))[0]
        new_mesh = bpy.data.meshes.new(name)
        new_mesh.from_pydata(vertices["position"], [], faces)
        new_mesh.update()
        if "normal" in vertices:
            new_mesh.normals_split_custom_set_from_vertices(vertices["normal"])
        new_object = bpy.data.objects.new(name, new_mesh)
        bpy.context.collection.objects.link(new_object)

    def _import_scene(self):
        raise NotImplementedError()

    def _import_lns(self):
        raise NotImplementedError()
