import bpy
import mathutils
from .base_imp import BaseImporter
from ..parser.scn_parser import ScnParser, RenderComponent

class ScnImporter(BaseImporter):
    def __init__(self, filename, operator, data=None, files=None):
        super().__init__(filename, operator, data)
        self.files = files
        self.scene = None

    def do_import(self):
        parser = ScnParser(self.filename, self.data, self.files)
        parser.parse_materials = self.operator.opt_materials
        self.scene = parser.parse()
        self.files = parser.files
        for report in parser.reports:
            self.operator.report(*report)
        self._create_assets()
        self._create_scene()

    def _create_assets(self):
        for mesh in self.scene.meshes.values():
            mesh.bpy = self.create_mesh(mesh.data, mesh.name)

        for texture in self.scene.textures.values():
            texture.bpy = self.create_image(texture.data, texture.name)

        for material in self.scene.materials.values():
            material.bpy = self.create_material(material, material.name)


    def _create_scene(self):
        for sceneobject in self.scene.sceneobjects:
            self._create_sceneobjects(sceneobject)

    def _create_sceneobjects(self, sceneobject, parent_bpy_obj=None):
        bpy_mesh = None
        for component in sceneobject.components:
            bpy_mesh = component.mesh.bpy
            if bpy_mesh.users > 0:
                bpy_mesh = bpy_mesh.copy()
                bpy_mesh.materials.clear()
            for material in component.materials:
                bpy_mesh.materials.append(material.bpy)
        bpy_obj = self.create_object(bpy_mesh, sceneobject.name)
        bpy_obj.location = sceneobject.location
        bpy_obj.scale = sceneobject.scale
        bpy_obj.rotation_mode = "QUATERNION"
        bpy_obj.rotation_quaternion = [sceneobject.rotation[3], *sceneobject.rotation[:3]]
        bpy_obj.parent = parent_bpy_obj
        if parent_bpy_obj is None:
            bpy_obj.matrix_world = self.scale_matrix @ self.conversion_matrix @ bpy_obj.matrix_world
        for child in sceneobject.children:
            self._create_sceneobjects(child, bpy_obj)
