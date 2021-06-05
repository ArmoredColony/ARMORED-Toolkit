# v1.1

import bpy, bmesh


class ARMORED_OT_select_edge_ring(bpy.types.Operator):
    '''Switches to edge mode before running the edge ring operator.

(www.armoredColony.com)'''
    
    bl_idname = 'mesh.armored_select_edge_ring'
    bl_label = 'ARMORED Select Edge Ring'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.loop_multi_select(ring=True)
        return {'FINISHED'}


classes = (
    ARMORED_OT_select_edge_ring,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)