# v1.3
# -Can now safely change the bevel properties after the operation without breaking anything.

# (For Blender 2.90 and above).


import bpy, bmesh
from bpy.props import BoolProperty

class ARMORED_OT_fast_bevel(bpy.types.Operator):
    '''Activates the bevel tool of whatever component mode you are using (face mode will bevel the perimeter of your selection).

(www.armoredColony.com)'''
 
    bl_idname = 'mesh.armored_fast_bevel'
    bl_label = 'ARMORED Fast Bevel'
    bl_options = {'REGISTER', 'UNDO'}

    face_border : BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
 
        # Are we in Vertex Mode?
        if sel_mode[0]:
            bpy.ops.mesh.bevel('INVOKE_DEFAULT', affect='VERTICES')
        
        # Are we in Edge Mode?
        elif sel_mode[1]:
            bpy.ops.mesh.bevel('INVOKE_DEFAULT', loop_slide=False)
            
        # Are we in Face Mode?
        elif sel_mode[2]:

            if self.face_border == True:
                me = context.edit_object.data
                bm = bmesh.from_edit_mesh(me)

                sel_border = set(e for e in bm.edges if e.select and (e.is_boundary or not all(f.select for f in e.link_faces)))
                
                bpy.ops.mesh.select_all(action='DESELECT')
                for e in sel_border: e.select = True

                bmesh.update_edit_mesh(me)
                bpy.ops.mesh.bevel('INVOKE_DEFAULT', loop_slide=False)

            else:
                bpy.ops.mesh.bevel('INVOKE_DEFAULT', loop_slide=False)
        
        return {'FINISHED'}


classes = (
    ARMORED_OT_fast_bevel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)