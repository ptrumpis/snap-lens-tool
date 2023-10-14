import os.path

from .mesh_parser import MeshParser
from .resource_parser import ResourceParser


class Asset:
    def __init__(self, name, uid):
        self.full_name = name
        self.name = os.path.splitext(os.path.basename(name))[0]
        self.uid = uid
        self.bpy = None  # used by importer


class MeshAsset(Asset):
    def __init__(self, name, uid, data):
        super().__init__(name, uid)
        self.data = data


class TextureAsset(Asset):
    def __init__(self, name, uid, data):
        super().__init__(name, uid)
        self.extension = os.path.splitext(name)[1]
        self.data = data


class MaterialAsset(Asset):
    def __init__(self, name, uid):
        super().__init__(name, uid)
        self.parsed = False

        self.base_color = None

        self.base_tex = None
        self.normal_tex = None
        self.detail_normal_tex = None
        self.material_params_tex = None
        self.opacity_tex = None
        self.reflection_tex = None
        self.rim_color_tex = None

        self.base_tex_uv = None
        self.normal_tex_uv = None
        self.detail_normal_tex_uv = None
        self.material_params_tex_uv = None
        self.opacity_tex_uv = None
        self.reflection_tex_uv = None
        self.rim_color_tex_uv = None

        self.metallic = None
        self.roughness = None
        self.reflection_intensity = None

        self.rimColor = None
        self.rimIntensity = None
        self.rimExponent = None

        self.uv2_scale = None
        self.uv2_offset = None

        self.uv3_scale = None
        self.uv3_offset = None

        self.defines = {}


class SceneObject:
    def __init__(self, name, uid, location, rotation, scale):
        self.name = name
        self.uid = uid
        self.location = location
        self.rotation = rotation
        self.scale = scale
        self.components = []
        self.children = []


class Component:
    def __init__(self, name, uid):
        self.name = name
        self.uid = uid


class RenderComponent(Component):
    def __init__(self, name, uid, mesh):
        super().__init__(name, uid)
        self.mesh = mesh
        self.materials = []


class Scene:
    def __init__(self):
        self.meshes = {}  #
        self.textures = {}  # uid => filename
        self.materials = {}  #
        self.sceneobjects = []


class ScnParser(ResourceParser):
    def __init__(self, filename, data=None, files=None):
        super().__init__(filename, data)
        self.files = files or {}
        self.files_preloaded = files is not None
        self.scene = None
        self.reports = []
        self.parse_materials = True

    def parse(self):
        super().parse()
        self.scene = Scene()
        self._parse_assets()
        self._parse_sceneobjects()

        return self.scene

    def _parse_sceneobjects(self):
        for sceneobject_json in self.json["sceneobjects"].values():
            sceneobject = self._parse_sceneobject(sceneobject_json)
            self.scene.sceneobjects.append(sceneobject)

    def _parse_sceneobject(self, sceneobject_json):
        name = sceneobject_json["name"]
        uid = sceneobject_json["uid"]
        position = sceneobject_json["position"]
        rotation = sceneobject_json["rotation"]
        scale = sceneobject_json["scale"]
        sceneobject = SceneObject(name, uid, position, rotation, scale)

        if "components" in sceneobject_json:
            for component_json in sceneobject_json["components"].values():
                uid = component_json["uid"]
                name = component_json["name"]
                if component_json["type"] in ["Component.RenderMeshVisual", "Component.MeshVisual"]:
                    mesh_uid = component_json["mesh"]["uid"]
                    mesh = self._get_asset(self.scene.meshes, mesh_uid)
                    if mesh is not None:
                        component = RenderComponent(name, uid, mesh)
                        for material_json in component_json["materials"].values():
                            material_uid = material_json["material"]["uid"]
                            material = self._get_asset(self.scene.materials, material_uid)
                            component.materials.append(material)
                        sceneobject.components.append(component)

        if "children" in sceneobject_json:
            for child_json in sceneobject_json["children"].values():
                child = self._parse_sceneobject(child_json)
                sceneobject.children.append(child)

        return sceneobject

    def _parse_assets(self):
        meshes_json = []
        textures_json = []
        materials_json = []

        for asset in self.json["assets"].values():
            if asset["type"] == "Asset.RenderMesh":
                meshes_json.append(asset)
            elif asset["type"] == "Asset.Texture":
                textures_json.append(asset)
            elif asset["type"] == "Asset.Material":
                materials_json.append(asset)

        for mesh_json in meshes_json:
            name = mesh_json["name"]
            uid = mesh_json["uid"]
            if mesh_json["provider"]["type"] == "Provider.FileRenderObjectProvider":
                filename = mesh_json["provider"]["filename"]
                if name == "":
                    name = filename
                file = self._get_file(filename)
                if file is not None:
                    parser = MeshParser(None, data=file)
                    mesh_data = parser.parse()
                    mesh = MeshAsset(name, uid, mesh_data)
                    self.scene.meshes[uid] = mesh
            else:
                self.reports.append(({"INFO"}, f"Skipped mesh asset {name}"))

        for texture_json in textures_json:
            name = os.path.basename(texture_json["name"])
            uid = texture_json["uid"]
            if texture_json["provider"]["type"] == "Provider.FileTextureProvider":
                filename = texture_json["provider"]["filename"]
                if name == "":
                    name = filename
                file = self._get_file(filename)
                if file is not None:
                    texture = TextureAsset(name, uid, file)
                    self.scene.textures[uid] = texture
            else:
                self.reports.append(({"INFO"}, f"Skipped texture asset {name}"))

        for material_json in materials_json:
            name = material_json["name"]
            uid = material_json["uid"]
            material = MaterialAsset(name, uid)
            self.scene.materials[uid] = material
            if self.parse_materials:
                self._build_material(material, material_json)

    def _build_material(self, material, material_json):
        material.parsed = True
        for define in material_json["passes"][0]["defines"].as_strings():
            name_value = define.split()
            if len(name_value) == 1:
                name_value.append(None)
            material.defines[name_value[0]] = name_value[1]

        props = {prop["name"]: prop for prop in material_json["passes"][0]["properties"].values()}

        # gather texture properties
        tex_types = ["baseTex", "normalTex", "detailNormalTex", "materialParamsTex", "opacityTex", "reflectionTex",
                     "rimColorTex"]
        tex_values = {tex_type: [None, 0] for tex_type in tex_types}
        for tex_type in tex_types:
            if tex_type in props and "value" in props[tex_type] and "uid" in props[tex_type]["value"]:
                tex_values[tex_type][0] = self._get_asset(self.scene.textures, props[tex_type]["value"]["uid"])
                uv_define = tex_type + "UV"
                if uv_define in material.defines:
                    tex_values[tex_type][1] = int(material.defines[uv_define])
        if "ENABLE_BASE_TEX" in material.defines:
            material.base_tex, material.base_tex_uv = tex_values["baseTex"]
        if "ENABLE_NORMALMAP" in material.defines:
            material.normal_tex, material.normal_tex_uv = tex_values["normalTex"]
        if "ENABLE_DETAIL_NORMAL" in material.defines:
            material.detail_normal_tex, material.detail_normal_tex_uv = tex_values["detailNormalTex"]
        if "ENABLE_SPECULAR_LIGHTING" in material.defines:
            material.material_params_tex, material.material_params_tex_uv = tex_values["materialParamsTex"]
        if "ENABLE_OPACITY_TEX" in material.defines:
            material.opacity_tex, material.opacity_tex_uv = tex_values["opacityTex"]
        if "ENABLE_SIMPLE_REFLECTION" in material.defines:
            material.reflection_tex, material.reflection_tex_uv = tex_values["reflectionTex"]
        if "ENABLE_RIM_COLOR_TEX" in material.defines:
            material.rim_color_tex, material.rim_color_tex_uv = tex_values["rimColorTex"]

        # gather regular properties
        prop_types = ["baseColor", "metallic", "roughness", "reflectionIntensity", "rimColor", "rimIntensity",
                      "rimExponent", "uv2Scale", "uv2Offset", "uv3Scale", "uv3Offset"]
        prop_values = {prop_type: None for prop_type in prop_types}
        for prop_type in prop_types:
            if prop_type in props:
                prop_values[prop_type] = props[prop_type]["value"]
        material.base_color = prop_values["baseColor"]
        if "ENABLE_RIM_HIGHLIGHT" in material.defines:
            material.rim_color = prop_values["rimColor"]
            material.rim_intensity = prop_values["rimIntensity"]
            material.rim_exponent = prop_values["rimExponent"]
        if "ENABLE_SPECULAR_LIGHTING" in material.defines:
            material.metallic = prop_values["metallic"]
            material.roughness = prop_values["roughness"]
        if "ENABLE_SIMPLE_REFLECTION" in material.defines:
            material.reflection_intensity = prop_values["reflectionIntensity"]
        if "ENABLE_UV2" in material.defines:
            material.uv2_scale = prop_values["uv2Scale"]
            material.uv2_offset = prop_values["uv2Offset"]
        if "ENABLE_UV3" in material.defines:
            material.uv3_scale = prop_values["uv3Scale"]
            material.uv3_offset = prop_values["uv3Offset"]

    ##### helpers #####

    def _get_file(self, filename):
        if not filename.startswith("/"):
            filename = "/" + filename
        if filename in self.files:
            return self.files[filename]
        elif not self.files_preloaded:
            basedir = os.path.dirname(self.filename)
            filepath = basedir + filename
            try:
                with open(filepath, "rb") as f:
                    self.files[filename] = f.read()
            except IOError as e:
                self.reports.append(({"WARNING"}, f"Failed to read file {filename}"))
                return None
            return self.files[filename]
        else:
            self.reports.append(({"WARNING"}, f"File {filename} not found"))
            return None

    def _get_asset(self, assets, uid):
        if uid in assets:
            return assets[uid]
        else:
            self.reports.append(({"WARNING"}, f"UID {uid} not found"))
            return None
