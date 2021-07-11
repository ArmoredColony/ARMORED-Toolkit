import bpy
from .. utils import addon


def draw(self, context):
    layout = self.layout
    layout.prop(addon.preferences(), 'allow_gizmo_click')


def register():
    bpy.types.VIEW3D_PT_gizmo_display.prepend(draw)


def unregister():
    bpy.types.VIEW3D_PT_gizmo_display.remove(draw)