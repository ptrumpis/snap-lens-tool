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

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

import os
import traceback
from .importer.mesh_imp import MeshImporter

class ImportLensMesh(Operator, ImportHelper):
    """Import a Snapchat mesh."""
    bl_idname = "import_mesh.snap_mesh"
    bl_label = "Import Snapchat Mesh"

    filename_ext = ".mesh"

    filter_glob: StringProperty(
        default="*.mesh",
        options={'HIDDEN'}
    )

    batch: BoolProperty(
        name="Batch import",
        description="Imports the whole directory",
        default=False,
    )

    def execute(self, context):
        if self.batch:
            dirname = os.path.dirname(self.filepath)
            filepaths = [os.path.join(dirname, file) for file in os.listdir(dirname) if file.endswith(".mesh")]
        else:
            filepaths = [self.filepath]
        for filepath in filepaths:
            try:
                imp = MeshImporter(filepath, self.as_keywords())
                imp.do_import()
            except NotImplementedError as e:
                self.report({"ERROR"}, f"Failed to load {filepath}")

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
