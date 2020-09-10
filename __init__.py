bl_info = {
    "name": "Snapchat Mesh Importer",
    "author": "Connor Virostek",
    "blender": (2, 80, 0),
    "version": (1, 0, 0),
    "location": "File > Import > Snapchat Mesh (.mesh)",
    "description": "Importer for Snapchat's mesh format used in Lenses.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

# Script reloading (if the user calls 'Reload Scripts' from Blender)
# source: https://github.com/KhronosGroup/glTF-Blender-IO/
def reload_package(module_dict_main):
    import importlib
    from pathlib import Path

    def reload_package_recursive(current_dir, module_dict):
        for path in current_dir.iterdir():
            if "__init__" in str(path) or path.stem not in module_dict:
                continue

            if path.is_file() and path.suffix == ".py":
                importlib.reload(module_dict[path.stem])
            elif path.is_dir():
                reload_package_recursive(path, module_dict[path.stem].__dict__)

    reload_package_recursive(Path(__file__).parent, module_dict_main)

if "bpy" in locals():
    reload_package(locals())

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

import os
import traceback
from .importer.mesh_imp import MeshImporter
from .importer.lns_imp import LnsImporter

class ImportLensMesh(Operator, ImportHelper):
    """Import a Snapchat mesh."""
    bl_idname = "import_mesh.snap_mesh"
    bl_label = "Import Snapchat Mesh"

    filename_ext = ""

    filter_glob: StringProperty(
        default="*.mesh;*.lns;*.scn",
        options={'HIDDEN'}
    )

    batch: BoolProperty(
        name="Batch import",
        description="Imports the whole directory",
        default=False,
    )

    def execute(self, context):
        if self.filepath.endswith(".mesh"):
            if self.batch:
                dirname = os.path.dirname(self.filepath)
                filepaths = [os.path.join(dirname, file) for file in os.listdir(dirname) if file.endswith(".mesh")]
            else:
                filepaths = [self.filepath]
            for filepath in filepaths:
                try:
                    imp = MeshImporter(filepath, self)
                    imp.do_import()
                except Exception as e:
                    self.report({"ERROR"}, f"Failed to load {filepath}")
        elif self.filepath.endswith(".lns"):
            imp = LnsImporter(self.filepath, self)
            imp.do_import()
        elif self.filepath.endswith(".scn"):
            raise NotImplementedError(".scn import not supported")

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportLensMesh.bl_idname, text="Snapchat Mesh (.mesh)")


def register():
    bpy.utils.register_class(ImportLensMesh)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportLensMesh)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    bpy.ops.import_mesh.snap_mesh('INVOKE_DEFAULT')
