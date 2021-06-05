# v1.1

import bpy


class ARMORED_OT_smart_loopcut(bpy.types.Operator):
    '''Same as Loopcut but with less clicks, also switches to edit mode automatically.

(www.armoredColony.com)'''

    bl_idname  = 'view3d.armored_smart_loopcut'
    bl_label   = 'ARMORED Smart Loopcut'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        if context.object.type != 'MESH':
            self.report({'WARNING'}, 'ARMORED Toolkit: Loopcut only works on MESH type objects.')
            return {'CANCELLED'}

        if context.mode  != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        bpy.ops.mesh.loopcut_slide('INVOKE_DEFAULT')
        return {'FINISHED'}


classes = (
    ARMORED_OT_smart_loopcut,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)    


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
