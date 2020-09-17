import bpy
import bpy_types
import numpy as np
import mathutils
from bpy_extras.io_utils import axis_conversion
from ..serializer.resource_serializer import ResourceSerializer
from ..parser.mesh_parser import Type

class MeshExporter:
    def __init__(self, filename, operator):
        self.filename = filename
        self.operator = operator
        self.scale_matrix = mathutils.Matrix.Scale(self.operator.opt_scale, 4)
        self.conversion_matrix = axis_conversion(from_forward="-Y", from_up="Z", to_forward="Z", to_up="Y").to_4x4()

    def do_export(self):
        if self.operator.opt_export_selected:
            bpy_objs = bpy.context.view_layer.objects.selected
        else:
            bpy_objs = bpy.context.view_layer.objects
        bpy_objs = [bpy_obj for bpy_obj in bpy_objs if isinstance(bpy_obj.data, bpy_types.Mesh)]

        if len(bpy_objs) == 0:
            if self.operator.opt_export_selected:
                self.operator.report({"ERROR"}, "No selected mesh.")
            else:
                self.operator.report({"ERROR"}, "No mesh to export.")
            return
        elif len(bpy_objs) > 1:
            if self.operator.opt_export_selected:
                self.operator.report({"ERROR"}, "Join to one mesh before exporting.")
            else:
                self.operator.report({"ERROR"}, "Join to one mesh or check 'Export selected' before exporting.")
            return
        bpy_obj = bpy_objs[0]
        bpy_mesh = bpy_objs[0].data.copy()
        bpy_mesh.transform(self.scale_matrix @ self.conversion_matrix @ bpy_obj.matrix_world)

        vert_pos = [np.array(vert.co) for vert in bpy_mesh.vertices]
        vert_norm = [np.array(vert.normal) for vert in bpy_mesh.vertices]
        if bpy_mesh.uv_layers.active is not None:
            vert_tex = [[] for _ in bpy_mesh.vertices]
        if bpy_mesh.vertex_colors.active is not None:
            vert_col = [[] for _ in bpy_mesh.vertices]

        # build up data for each vertex
        for face in bpy_mesh.polygons:
            if face.loop_total != 3:
                self.operator.report({"ERROR"}, "Triangulate mesh before exporting.")
                return
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):

                if bpy_mesh.uv_layers.active is not None:
                    vert_tex[vert_idx].append(np.array(bpy_mesh.uv_layers.active.data[loop_idx].uv))

                if bpy_mesh.vertex_colors.active is not None:
                    vert_col[vert_idx].append(np.array(bpy_mesh.vertex_colors.active.data[loop_index].color))

        bbmin = np.min(vert_pos, axis=0)
        bbmax = np.max(vert_pos, axis=0)

        attributes = [vert_pos, vert_norm]
        if bpy_mesh.uv_layers.active is not None:
            vert_tex = [np.average(coords, axis=-2) for coords in vert_tex]
            attributes.append(vert_tex)
            texmin = np.min(vert_tex, axis=0)
            texmax = np.max(vert_tex, axis=0)

        if bpy_mesh.vertex_colors.active is not None:
            vert_col = [np.average(colors, axis=-2) for colors in vert_col]
            attributes.append(vert_col)

        vert_dtype = [("position", (np.float32, 3)), ("normal", (np.float32, 3))]
        if bpy_mesh.uv_layers.active is not None:
            vert_dtype.append(("texture0", (np.float32, 2)))
        if bpy_mesh.vertex_colors.active is not None:
            vert_dtype.append(("color", (np.uint8, 4)))

        vertex_data = [tuple(attr[i] for attr in attributes) for i in range(len(vert_pos))]
        vertex_data = np.array(vertex_data, dtype=vert_dtype)
        index_data = np.array([face.vertices for face in bpy_mesh.polygons], dtype=np.uint16)

        ##### Serialization ######

        serializer = ResourceSerializer()
        serializer.write_int32("indexType", 1)
        serializer.write_int32("topology", 0)
        serializer.begin("vertexlayout")

        serializer.write_uint32("vertexSize", vertex_data.itemsize)
        serializer.begin("attributes")

        index = 0
        offset = 0
        serializer.begin()
        serializer.write_string("semantic", "position")
        serializer.write_uint32("index", index)
        serializer.write_int32("type", Type.FLOAT32.value)
        serializer.write_uint32("componentCount", 3)
        serializer.write_bool("normalized", False)
        serializer.write_uint32("offset", offset)
        index += 1
        offset += 12
        serializer.end()

        serializer.begin()
        serializer.write_string("semantic", "normal")
        serializer.write_uint32("index", index)
        serializer.write_int32("type", Type.FLOAT32.value)
        serializer.write_uint32("componentCount", 3)
        serializer.write_bool("normalized", False)
        serializer.write_uint32("offset", offset)
        index += 1
        offset += 12
        serializer.end()

        '''
        serializer.begin()
        serializer.write_string("semantic", "tangent")
        serializer.write_uint32("index", index)
        serializer.write_int32("type", Type.FLOAT32.value)
        serializer.write_uint32("componentCount", 4)
        serializer.write_bool("normalized", False)
        serializer.write_uint32("offset", offset)
        index += 1
        offset += 16
        serializer.end()
        '''

        if bpy_mesh.uv_layers.active is not None:
            serializer.begin()
            serializer.write_string("semantic", "texture0")
            serializer.write_uint32("index", index)
            serializer.write_int32("type", Type.FLOAT32.value)
            serializer.write_uint32("componentCount", 2)
            serializer.write_bool("normalized", False)
            serializer.write_uint32("offset", offset)
            index += 1
            offset += 8
            serializer.end()

        if bpy_mesh.vertex_colors.active is not None:
            serializer.begin()
            serializer.write_string("semantic", "color")
            serializer.write_uint32("index", index)
            serializer.write_int32("type", Type.UINT8.value)
            serializer.write_uint32("componentCount", 4)
            serializer.write_bool("normalized", False)
            serializer.write_uint32("offset", offset)
            index += 1
            offset += 4
            serializer.end()

        serializer.end() # attributes
        serializer.end() # vertexLayout

        serializer.write_bool("saveWithPadding", False)

        serializer.write_array("vertices", vertex_data)
        serializer.write_array("indices", index_data)

        serializer.begin("blendshapes")
        serializer.end()

        serializer.write_uint32("vertexCacheVersion", 2)

        serializer.begin("vertexCache")
        serializer.end()

        serializer.begin("vertexCacheAabbKeyframes")
        serializer.end()

        serializer.write_vec3f("bbmin", bbmin)
        serializer.write_vec3f("bbmax", bbmax)
        if bpy_mesh.uv_layers.active is not None:
            serializer.write_vec2f("texmin", texmin)
            serializer.write_vec2f("texmax", texmax)

        serializer.begin("skinbones")
        serializer.end()

        serializer.begin("rgroups")
        serializer.end()

        serializer.begin("submeshes")
        serializer.end()

        serializer.finalize()
        serializer.to_file(self.filename)

        bpy.data.meshes.remove(bpy_mesh)

