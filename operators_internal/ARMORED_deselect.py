# v1.0

import bpy
from bpy.props import EnumProperty


class ARMORED_OT_deselect(bpy.types.Operator):
    '''Wrapper for deselect operator (allows custom hotkey to take priority because it registers late?)'''

    bl_idname  = 'armored.deselect'
    bl_label   = 'ARMORED Deselect'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        bpy.ops.view3d.select('INVOKE_DEFAULT', deselect=True, center=False, object=False)
        return {'FINISHED'}

classes = (
    ARMORED_OT_deselect,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)    


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
