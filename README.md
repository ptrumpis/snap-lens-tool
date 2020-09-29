# Snapchat Lens Importer/Exporter

This is a Blender addon for importing/exporting content from Snapchat lenses.

## Features

Currently implemented:
- Import meshes from a Snapchat lens into Blender.
- Import the entire scene graph from a Snapchat lens.
- Experimental support for importing materials (see *Notes*).
- Extract files from a Snapchat lens (see *Additional Tools*).
- Convert binary resource files to human-readable XML (see *Additional Tools*).

Not currently implemented:
- Import bones/animations.
- Import animated textures.

## Installation

1. Download the latest release or zip the snapchat\_lens directory.

2. In Blender, navigate to `Edit > Preferences... > Add-ons > Install...` and select the zip file.

3. `Snapchat Mesh` should appear in import/export menus.

4. To import from an LNS file, you need to install the `zstandard` module in Blender's Python installation. See [here](https://blender.stackexchange.com/a/122337) for instructions on how to do this, replacing `scipy` with `zstandard`.

## Snapchat Lens Files

### File Formats

Snapchat lenses are packaged into LNS files. LNS is Snapchat's own archive format that uses zstd compression.

Certain resources (such as .scn and .mesh files) use another proprietary binary file format. I refer to files in this format as "resource files."

Snapchat lenses will often contain a scene.scn file, which contains materials and scene graph information. It can be converted to human-readable XML using `resource_tool.py`.

### Retrieving Lens Files

Retrieving a lense's LNS file requires a jailbroken iOS device or a rooted Android device. On iOS, LNS files can be found in `/var/mobile/Containers/Data/Application/<id>/Library/Caches/Lenses`. I don't have a rootable Android device, so I'm not sure where they would be located on Android.

## Additional Tools

The root project directory contains some additional tools for working with lens files. Modules needed to run these tools are listed in `requirements.txt`.

`lns_tool.py`: Extracts and creates LNS archives. You can put modified LNS archives back on your device and the modifications will show up when you use the lens.

`resource_tool.py`: Converts resource files to and from human-readable XML. This is especially useful for viewing and modifying scene.scn files.

`hash.py`: Hashes a file using Snapchat's hashing method. Note that Snapchat doesn't seem to verify the hashes in scene.scn, so there's probably no need to use this tool.

## Notes

### Materials
Due to the way materials are represented in Snapchat lenses, it's not really feasible to accurately recreate them in Blender automatically. There is an experimental option to import materials, but most of the time they won't look quite right. Material information is shared between the scene.scn file and glsl files, so if you want to fix materials by hand you can reference those.

