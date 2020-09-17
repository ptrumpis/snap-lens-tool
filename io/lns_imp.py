from .base_imp import BaseImporter
from .scn_imp import ScnImporter
from ..common.parser.lns_parser import LnsParser

class LnsImporter(BaseImporter):
    def __init__(self, filename, operator, data=None):
        super().__init__(filename, operator, data)

    def do_import(self):
        parser = LnsParser(self.filename)
        files = parser.parse()

        if "/scene.scn" in files:
            scn_importer = ScnImporter(None, self.operator, data=files["/scene.scn"], files=files)
            scn_importer.do_import()
        else:
            self.operator.report({"WARNING"}, "LNS archive does not contain a scene.scn")

        '''
    def _import_lns(self):
        parser = LnsParser(self.filename)
        files = parser.parse()
        return files

        parser = ResourceParser(None, data=files["/scene.scn"])
        scene = parser.parse()
        assets = self.create_assets(scene, files)
        self.create_scene(scene["sceneobjects"], assets)

    def create_assets(self, scene, files):
        assets = {}
        materials_tmp = []
        for asset in scene["assets"].values():
            # process materials after textures
            if asset["type"] == "Asset.Material":
                materials_tmp.append(asset)

            elif "provider" in asset and "filename" in asset["provider"]:
                # fetch file if asset has one
                filename = asset["provider"]["filename"]
                if filename == "":
                    continue
                if not filename.startswith("/"):
                    filename = "/" + filename
                if filename not in files:
                    self.operator.report({"WARNING"}, f"File {filename} not found")
                    continue
                file = files[filename]

                # mesh/image creation
                if asset["type"] == "Asset.RenderMesh":
                    parser = MeshParser(None, data=file)
                    mesh = parser.parse()
                    name = os.path.splitext(os.path.basename(asset["name"]))[0]
                    assets[asset["uid"]] = super().create_mesh(mesh, name)
                elif asset["type"] == "Asset.Texture":
                    name = os.path.basename(asset["name"])
                    assets[asset["uid"]] = self.create_image(file, name)

        # material creation
        for material in materials_tmp:
            assets[material["uid"]] = self.create_material(material, assets)
        return assets

    def create_image(self, image, name):
        # bpy doesn't support reading images from memory,
        # so temporarily write it to a file
        extension = os.path.splitext(name)[1]
        with NamedTemporaryFile(suffix=extension) as temp:
            temp.write(image)
            temp.flush()
            bpy_image = bpy.data.images.load(temp.name)
            bpy_image.name = name
            bpy_image.pack()
        return bpy_image

    def create_material(self, asset, assets):
        name = os.path.basename(asset["name"])
        props = {prop["name"]: prop for prop in asset["passes"][0]["properties"].values()}

        bpy_mat = bpy.data.materials.new(name)
        bpy_mat.use_nodes = True
        node_tree = bpy_mat.node_tree
        nodes = node_tree.nodes
        bsdf = nodes["Principled BSDF"]

        mapping_node = None
        if "uv2Offset" in props or "uv2Scale" in props:
            tex_coord_node = nodes.new("ShaderNodeTexCoord")
            mapping_node = nodes.new("ShaderNodeMapping")
            node_tree.links.new(tex_coord_node.outputs["UV"], mapping_node.inputs["Vector"])
            if "uv2Offset" in props:
                mapping_node.inputs["Location"].default_value[:2] = props["uv2Offset"]["value"]
            if "uv2Scale" in props:
                mapping_node.inputs["Scale"].default_value[:2] = props["uv2Scale"]["value"]


        if "baseTex" in props and "baseColor" not in props:
            uid = props["baseTex"]["value"]["uid"]
            tex_node = nodes.new("ShaderNodeTexImage")
            if uid in assets:
                tex_node.image = assets[uid]
            node_tree.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
            if mapping_node is not None:
                node_tree.links.new(mapping_node.outputs["Vector"], tex_node.inputs["Vector"])

        if "baseColor" in props and "baseTex" not in props:
            bsdf.inputs["Base Color"].default_value = props["baseColor"]["value"]

        if "baseTex" in props and "baseColor" in props:
            tex_uid = props["baseTex"]["value"]["uid"]
            tex_node = nodes.new("ShaderNodeTexImage")
            if tex_uid in assets:
                tex_node.image = assets[tex_uid]
            mix_node = nodes.new("ShaderNodeMixRGB")
            mix_node.inputs["Fac"].default_value = 1
            mix_node.inputs["Color2"].default_value = props["baseColor"]["value"]
            mix_node.blend_type = "MULTIPLY"
            node_tree.links.new(mix_node.outputs["Color"], bsdf.inputs["Base Color"])
            node_tree.links.new(tex_node.outputs["Color"], mix_node.inputs["Color1"])
            if mapping_node is not None:
                node_tree.links.new(mapping_node.outputs["Vector"], tex_node.inputs["Vector"])

        if "normalTex" in props and "detailNormalTex" not in props:
            uid = props["normalTex"]["value"]["uid"]
            norm_node = nodes.new("ShaderNodeNormalMap")
            tex_node = nodes.new("ShaderNodeTexImage")
            if uid in assets:
                tex_node.image = assets[uid]
                tex_node.image.colorspace_settings.name = "Non-Color"
            node_tree.links.new(norm_node.outputs["Normal"], bsdf.inputs["Normal"])
            node_tree.links.new(tex_node.outputs["Color"], norm_node.inputs["Color"])
            if mapping_node is not None:
                node_tree.links.new(mapping_node.outputs["Vector"], tex_node.inputs["Vector"])

        if "normalTex" not in props and "detailNormalTex" in props:
            pass

        if "normalTex" in props and "detailNormalTex" in props:
            #placeholder
            uid = props["normalTex"]["value"]["uid"]
            norm_node = nodes.new("ShaderNodeNormalMap")
            tex_node = nodes.new("ShaderNodeTexImage")
            if uid in assets:
                tex_node.image = assets[uid]
                tex_node.image.colorspace_settings.name = "Non-Color"
            node_tree.links.new(norm_node.outputs["Normal"], bsdf.inputs["Normal"])
            node_tree.links.new(tex_node.outputs["Color"], norm_node.inputs["Color"])
            if mapping_node is not None:
                node_tree.links.new(mapping_node.outputs["Vector"], tex_node.inputs["Vector"])

        if "materialParamsTex" not in props and "metallic" in props:
            bsdf.inputs["Metallic"].default_value = props["materialParamsTex"]["value"]

        if "materialParamsTex" not in props and "roughness" in props:
            bsdf.inputs["Roughness"].default_value = props["materialParamsTex"]["value"]

        if "materialParamsTex" in props:
            pass

        for prop_name, prop in props.items():
            if prop_name == "baseTex":
                pass
            elif prop_name == "normalTex":
                pass
            elif prop_name == "baseColor":
                pass
            elif prop_name == "opacityTex":
                pass
            elif prop_name == "reflectionTex":
                pass
            elif prop_name == "metallic":
                pass
            elif prop_name == "roughness":
                pass
            elif prop_name == "materialParamsTex":
                pass
            elif prop_name == "detailNormalTex":
                pass
            elif prop_name == "reflectionTex":
                pass
            elif prop_name == "uv2Scale":
                pass
            elif prop_name == "uv2Offset":
                pass
        return bpy_mat

    def create_scene(self, sceneobjects, assets):
        for sceneobject in sceneobjects.values():
            self._create_sceneobjects(sceneobject, None, assets)

    def _create_sceneobjects(self, sceneobject, parent_bpy_obj, assets):
        bpy_mesh = None
        if "components" in sceneobject:
            for component in sceneobject["components"].values():
                if component["type"] == "Component.RenderMeshVisual":
                    bpy_mesh = assets[component["mesh"]["uid"]]
                    if bpy_mesh.users > 0:
                        bpy_mesh = bpy_mesh.copy()
                        bpy_mesh.materials.clear()
                    for material in component["materials"].values():
                        bpy_mat = assets[material["material"]["uid"]]
                        bpy_mesh.materials.append(bpy_mat)
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
        '''
