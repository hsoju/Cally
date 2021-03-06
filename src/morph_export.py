from bpy.props import StringProperty
from bpy.types import Context, Operator
from bpy_extras.io_utils import ExportHelper
from typing import Set
from .xfile.xpf import export_xpf


class CalMorphExporter(Operator, ExportHelper):
    """Exports as a Cal3D XPF file"""
    bl_idname = "export_scene.export_xpf"
    bl_label = "Export XPF"
    bl_options = {'REGISTER', 'PRESET'}

    filename_ext = ".xpf"

    filter_glob: StringProperty(
        default="*.xpf",
        options={'HIDDEN'},
        maxlen=255,
    )

    @classmethod
    def poll(cls, context: Context) -> bool:
        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.data.shape_keys and obj.data.shape_keys.animation_data \
                    and obj.data.shape_keys.animation_data.action:
                return True
        return False

    def execute(self, context: Context) -> Set[str]:
        export_xpf(context, self.filepath, context.scene.render.fps, context.scene.frame_end)
        return {'FINISHED'}
