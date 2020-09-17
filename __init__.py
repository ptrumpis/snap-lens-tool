bl_info = {
    "name": "Snapchat Mesh Importer",
    "author": "Connor Virostek",
    "blender": (2, 80, 0),
    "version": (1, 0, 0),
    "location": "File > Import > Snapchat Mesh (.mesh/.scn/.lns)",
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
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty
from bpy.types import Operator

import os
import traceback
from .importer.mesh_imp import MeshImporter
from .importer.lns_imp import LnsImporter
from .importer.scn_imp import ScnImporter
from .importer.base_imp import BaseImporter
from .exporter.mesh_exp import MeshExporter

class ImportSnapchatMesh(Operator, ImportHelper):
    """Import a Snapchat mesh."""
    bl_idname = "import_mesh.snapchat_mesh"
    bl_label = "Import Snapchat Mesh"

    filename_ext = ""

    filter_glob: StringProperty(
        default="*.mesh;*.lns;*.scn",
        options={'HIDDEN'}
    )

    opt_batch: BoolProperty(
        name="Batch import",
        description="Imports all .mesh files in same directory",
        default=False,
    )

    opt_scale: FloatProperty(
        name="Scale",
        description="Scales meshes/scene",
        default=0.1,
    )

    opt_materials: BoolProperty(
        name="Import materials",
        description="Attempts to reconstruct materials (experimental)",
        default=False,
    )

    def execute(self, context):
        ext = os.path.splitext(self.filepath)[1]
        if ext == ".mesh":
            if self.opt_batch:
                dirname = os.path.dirname(self.filepath)
                filepaths = [os.path.join(dirname, file) for file in os.listdir(dirname) if file.endswith(".mesh")]
            else:
                filepaths = [self.filepath]
            for filepath in filepaths:
                try:
                    imp = MeshImporter(filepath, self)
                    imp.do_import()
                except Exception as e:
                    self.report({"ERROR"}, traceback.format_exc())
                    self.report({"ERROR"}, f"Failed to load {filepath}")
        elif ext == ".lns" or ext == "":
            imp = LnsImporter(self.filepath, self)
            imp.do_import()
        elif ext == ".scn":
            imp = ScnImporter(self.filepath, self)
            imp.do_import()

        return {'FINISHED'}

class ExportSnapchatMesh(Operator, ImportHelper):
    """Export a Snapchat mesh."""
    bl_idname = "export_mesh.snapchat_mesh"
    bl_label = "Export Snapchat Mesh"

    filename_ext = ""

    filter_glob: StringProperty(
        default="*.mesh",
        options={'HIDDEN'}
    )

    opt_scale: FloatProperty(
        name="Scale",
        description="Scales mesh",
        default=10,
    )

    opt_export_selected: BoolProperty(
        name="Export selected",
        description="Exports the selected object",
        default=False,
    )

    def execute(self, context):
        exp = MeshExporter(self.filepath, self)
        exp.do_export()

        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportSnapchatMesh.bl_idname, text="Snapchat Mesh (.mesh/.scn/.lns)")

def menu_func_export(self, context):
    self.layout.operator(ExportSnapchatMesh.bl_idname, text="Snapchat Mesh (.mesh)")

def register():
    bpy.utils.register_class(ImportSnapchatMesh)
    bpy.utils.register_class(ExportSnapchatMesh)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ImportSnapchatMesh)
    bpy.utils.unregister_class(ExportSnapchatMesh)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    bpy.ops.import_mesh.snapchat_mesh('INVOKE_DEFAULT')
