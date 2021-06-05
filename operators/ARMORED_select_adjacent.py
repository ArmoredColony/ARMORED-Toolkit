# v1.1

import bpy, bmesh
from bpy.props import BoolProperty

   
class ARMORED_OT_select_adjacent(bpy.types.Operator):
    '''Selects the adjacent components (different component modes offers different results).

(www.armoredColony.com)'''
    
    bl_idname = 'mesh.armored_select_adjacent'
    bl_label = 'ARMORED Select Adjacent'
    bl_options = {'REGISTER', 'UNDO'}

    face_step: BoolProperty(name='Face Step', default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.edit_object.data)
        mode = context.tool_settings.mesh_select_mode[:]

        if mode[0]:   sel = set(e for e in bm.verts if e.select)
        elif mode[1]: sel = set(e for e in bm.edges if e.select)
        elif mode[2]: sel = set(e for e in bm.faces if e.select)

        bpy.ops.mesh.select_more(use_face_step=self.face_step)
            
        for e in sel:
            e.select = False
        
        bm.select_flush_mode()   
        return {'FINISHED'}


classes = (
    ARMORED_OT_select_adjacent,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)