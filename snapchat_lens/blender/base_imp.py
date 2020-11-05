import bpy
from bpy_extras.io_utils import axis_conversion
import os
from tempfile import TemporaryDirectory
import mathutils

class BaseImporter:
    def __init__(self, filename, operator, data=None):
        self.filename = filename
        self.operator = operator
        self.data = data
        self.scale_matrix = mathutils.Matrix.Scale(self.operator.opt_scale, 4)
        self.conversion_matrix = axis_conversion(from_forward="Z", from_up="Y", to_forward="-Y", to_up="Z").to_4x4()

    def do_import(self):
        raise NotImplementedError("Function stub")

    def create_mesh(self, mesh, name):
        bpy_mesh = bpy.data.meshes.new(name)
        bpy_mesh.from_pydata(mesh.vertices["position"], [], mesh.indices)
        if "normal" in mesh.vertices:
            bpy_mesh.use_auto_smooth = True
            bpy_mesh.normals_split_custom_set_from_vertices(mesh.vertices["normal"])
        if "texture0" in mesh.vertices:
            uvlayer = bpy_mesh.uv_layers.new()
            bpy_mesh.uv_layers.active = uvlayer
            for face in bpy_mesh.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    uvlayer.data[loop_idx].uv = mesh.vertices["texture0"][vert_idx]
            bpy_mesh.calc_tangents(uvmap=uvlayer.name)
        if "color" in mesh.vertices:
            vert_colors = bpy_mesh.vertex_colors.new()
            for face in bpy_mesh.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    vert_colors.data[loop_idx].color = mesh.vertices["color"][vert_idx]
        bpy_mesh.update()

        return bpy_mesh

    def create_skeleton(self, bones, name):
        bpy_arm = bpy.data.armatures.new(name)
        bpy_arm_obj = self.create_object(bpy_arm, name)
        bpy_arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = bpy_arm_obj
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in bones:
            bpy_bone = bpy_arm.edit_bones.new(bone.name)
            bpy_bone.select = True
            bpy_bone.tail[0] = 1
            mat_basis = bpy_bone.matrix
            bpy_bone.matrix = mathutils.Matrix(bone.invmat).inverted_safe() @ mat_basis
            bpy_bone.select = False
        bpy.ops.object.mode_set(mode='OBJECT')
        return bpy_arm_obj

    def create_object(self, bpy_mesh, name):
        bpy_object = bpy.data.objects.new(name, bpy_mesh)
        bpy.context.collection.objects.link(bpy_object)
        return bpy_object

    def create_image(self, image, name):
        # bpy doesn't support reading images from memory,
        # so temporarily write it to a file
        with TemporaryDirectory() as tempdir:
            tempfile_path = os.path.join(tempdir, name)
            with open(tempfile_path, "wb") as tempfile:
                tempfile.write(image)
            bpy_image = bpy.data.images.load(tempfile_path)
            bpy_image.name = name
            bpy_image.pack()
        return bpy_image

    def create_material(self, material, name):
        bpy_mat = bpy.data.materials.new(name)

        if not material.parsed:
            return bpy_mat

        bpy_mat.use_nodes = True
        node_tree = bpy_mat.node_tree
        nodes = node_tree.nodes
        bsdf = nodes["Principled BSDF"]

        # create UV transform nodes
        uv_transform_nodes = [None, None]
        if "ENABLE_UV2" in material.defines:
            uv_transform_nodes[0] = nodes.new("ShaderNodeMapping")
            uv_transform_nodes[0].inputs["Location"].default_value[:2] = material.uv2_offset
            uv_transform_nodes[0].inputs["Scale"].default_value[:2] = material.uv2_scale
            coord_node = nodes.new("ShaderNodeTexCoord")
            node_tree.links.new(coord_node.outputs["UV"], uv_transform_nodes[0].inputs["Vector"])
        if "ENABLE_UV3" in material.defines:
            uv_transform_nodes[1] = nodes.new("ShaderNodeMapping")
            uv_transform_nodes[1].inputs["Location"].default_value[:2] = material.uv3_offset
            uv_transform_nodes[1].inputs["Scale"].default_value[:2] = material.uv3_scale
            coord_node = nodes.new("ShaderNodeTexCoord")
            node_tree.links.new(coord_node.outputs["UV"], uv_transform_nodes[1].inputs["Vector"])

        # create base color nodes
        output_node = bsdf
        input1 = "Base Color"
        input2 = input1
        if material.base_tex is not None and material.base_color is not None:
            mix_node = nodes.new("ShaderNodeMixRGB")
            mix_node.blend_type = "MULTIPLY"
            mix_node.inputs["Fac"].default_value = 1
            node_tree.links.new(mix_node.outputs["Color"], output_node.inputs[input1])
            output_node = mix_node
            input1 = "Color1"
            input2 = "Color2"
        if material.base_tex is not None:
            image_node = nodes.new("ShaderNodeTexImage")
            image_node.image = material.base_tex.bpy
            node_tree.links.new(image_node.outputs["Color"], output_node.inputs[input1])
            if material.base_tex_uv > 0:
                i = material.base_tex_uv - 2
                if uv_transform_nodes[i] is not None:
                    node_tree.links.new(uv_transform_nodes[i].outputs["Vector"], image_node.inputs["Vector"])
        if material.base_color is not None:
            output_node.inputs[input2].default_value = material.base_color

        # create normal map nodes
        output_node = bsdf
        input1 = "Normal"
        input2 = input1
        if material.normal_tex is not None and material.detail_normal_tex is not None:
            mix_node = nodes.new("ShaderNodeMixRGB")
            mix_node.blend_type = "OVERLAY"
            mix_node.inputs["Fac"].default_value = 1
            node_tree.links.new(mix_node.outputs["Color"], output_node.inputs[input1])
            output_node = mix_node
            input1 = "Color1"
            input2 = "Color2"
        if material.normal_tex is not None:
            normal_node = nodes.new("ShaderNodeNormalMap")
            image_node = nodes.new("ShaderNodeTexImage")
            image_node.image = material.normal_tex.bpy
            material.normal_tex.bpy.colorspace_settings.name = "Non-Color"
            node_tree.links.new(image_node.outputs["Color"], normal_node.inputs["Color"])
            node_tree.links.new(normal_node.outputs["Normal"], output_node.inputs[input1])
            if material.normal_tex_uv > 0:
                i = material.normal_tex_uv - 2
                if uv_transform_nodes[i] is not None:
                    node_tree.links.new(uv_transform_nodes[i].outputs["Vector"], image_node.inputs["Vector"])
        if material.detail_normal_tex is not None:
            normal_node = nodes.new("ShaderNodeNormalMap")
            image_node = nodes.new("ShaderNodeTexImage")
            image_node.image = material.detail_normal_tex.bpy
            material.normal_tex.bpy.colorspace_settings.name = "Non-Color"
            node_tree.links.new(image_node.outputs["Color"], normal_node.inputs["Color"])
            node_tree.links.new(normal_node.outputs["Normal"], output_node.inputs[input2])
            if material.detail_normal_tex_uv > 0:
                i = material.detail_normal_tex_uv - 2
                if uv_transform_nodes[i] is not None:
                    node_tree.links.new(uv_transform_nodes[i].outputs["Vector"], image_node.inputs["Vector"])

        # create roughness/metallic nodes
        if material.material_params_tex is None:
            if material.roughness is not None:
                bsdf.inputs["Roughness"].default_value = material.roughness
            if material.metallic is not None:
                bsdf.inputs["Metallic"].default_value = material.metallic
        else:
            image_node = nodes.new("ShaderNodeTexImage")
            rgb_node = nodes.new("ShaderNodeSeparateRGB")
            image_node.image = material.material_params_tex.bpy
            material.material_params_tex.bpy.colorspace_settings.name = "Non-Color"
            node_tree.links.new(rgb_node.inputs["Image"], image_node.outputs["Color"])
            roughness_node = nodes.new("ShaderNodeMath")
            roughness_node.operation = "MULTIPLY"
            roughness_node.inputs[1].default_value = material.roughness
            metallic_node = nodes.new("ShaderNodeMath")
            metallic_node.operation = "MULTIPLY"
            metallic_node.inputs[1].default_value = material.metallic
            node_tree.links.new(rgb_node.outputs["G"], roughness_node.inputs[0])
            node_tree.links.new(rgb_node.outputs["R"], metallic_node.inputs[0])
            node_tree.links.new(roughness_node.outputs["Value"], bsdf.inputs["Roughness"])
            node_tree.links.new(metallic_node.outputs["Value"], bsdf.inputs["Metallic"])
            if material.material_params_tex_uv > 0:
                i = material.material_params_tex_uv - 2
                if uv_transform_nodes[i] is not None:
                    node_tree.links.new(uv_transform_nodes[i].outputs["Vector"], image_node.inputs["Vector"])

        # create opacity map
        if material.opacity_tex is not None:
            image_node = nodes.new("ShaderNodeTexImage")
            image_node.image = material.opacity_tex.bpy
            material.opacity_tex.bpy.colorspace_settings.name = "Non-Color"
            node_tree.links.new(image_node.outputs["Color"], bsdf.inputs["Alpha"])
            bpy_mat.blend_method = "BLEND"
            if material.opacity_tex_uv > 0:
                i = material.opacity_tex_uv - 2
                if uv_transform_nodes[i] is not None:
                    node_tree.links.new(uv_transform_nodes[i].outputs["Vector"], image_node.inputs["Vector"])

        return bpy_mat
