import os.path
import bpy
from bpy_extras.io_utils import axis_conversion
from .mesh_imp import MeshImporter
from ..parser.mesh_parser import MeshParser
from ..parser.lns_parser import LnsParser
from ..parser.resource_parser import ResourceParser

class LnsImporter(MeshImporter):
    def __init__(self, filename, operator):
        super().__init__(filename, operator)

    def do_import(self):
        self._import_lns()

    def _import_lns(self):
        parser = LnsParser(self.filename)
        files = parser.parse()
        if "/scene.scn" not in files:
            raise NotImplementedError("LNS without scene.scn file not supported")

        parser = ResourceParser(None, data=files["/scene.scn"])
        scene = parser.parse()
        assets = self.create_assets(scene, files)
        self.create_scene(scene["sceneobjects"], assets)

    def create_assets(self, scene, files):
        assets = {}
        for asset in scene["assets"].values():
            if asset["type"] == "Asset.RenderMesh":
                filename = asset["provider"]["filename"]
                if not filename.startswith("/"):
                    filename = "/" + filename
                if filename not in files:
                    self.operator.report({"WARNING"}, f"File {filename} not found")
                    continue
                parser = MeshParser(None, data=files[filename])
                mesh = parser.parse()
                name = os.path.basename(asset["name"])
                assets[asset["uid"]] = super().create_mesh(mesh, name)
        return assets

    def create_scene(self, sceneobjects, assets):
        for sceneobject in sceneobjects.values():
            self._create_sceneobjects(sceneobject, None, assets)

    def _create_sceneobjects(self, sceneobject, parent_bpy_obj, assets):
        bpy_mesh = None
        if "components" in sceneobject:
            for component in sceneobject["components"].values():
                if component["type"] == "Component.RenderMeshVisual":
                    bpy_mesh = assets[component["mesh"]["uid"]]
                    break
        bpy_obj = self.create_object(bpy_mesh, sceneobject["name"])
        bpy_obj.location = sceneobject["position"]
        bpy_obj.scale = sceneobject["scale"]
        bpy_obj.rotation_mode = "QUATERNION"
        rotation = sceneobject["rotation"]
        bpy_obj.rotation_quaternion = [rotation[3], *rotation[:3]]
        bpy_obj.parent = parent_bpy_obj
        if "children" in sceneobject:
            for child in sceneobject["children"].values():
                self._create_sceneobjects(child, bpy_obj, assets)
