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

try:
    import bpy
    is_blender = True
except ModuleNotFoundError:
    is_blender = False

if is_blender:
    from .blender import *
