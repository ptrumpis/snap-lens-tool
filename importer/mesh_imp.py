import bpy
import os.path
from .base_imp import BaseImporter
from ..parser.mesh_parser import MeshParser

class MeshImporter(BaseImporter):
    def __init__(self, filename, operator, data=None):
        super().__init__(filename, operator, data)

    def do_import(self):
        parser = MeshParser(self.filename, data=self.data)
        mesh = parser.parse()
        name = os.path.splitext(os.path.basename(self.filename))[0]
        bpy_mesh = self.create_mesh(mesh, name)
        bpy_object = self.create_object(bpy_mesh, name)

