# v2.0

import bpy


class MESH_OT_armored_focus(bpy.types.Operator):
    '''Provides additional functionality to the view_selected operator, such as re-centering the object even if you don't have any components selected, or viewing all the objects in your scene if no object is selected.

(www.armoredColony.com)'''
    
    bl_idname = 'mesh.armored_focus'
    bl_label = 'ARMORED Focus'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        if context.mode == 'OBJECT':
            selection = context.selected_objects

            bpy.ops.view3d.view_selected('INVOKE_DEFAULT') if selection else bpy.ops.view3d.view_all('INVOKE_DEFAULT')
            return {'FINISHED'}

        elif context.mode == 'EDIT_MESH': 
            obj = context.edit_object
            selection = obj.data.total_vert_sel
            
            if not selection:
                bpy.ops.mesh.select_all(action='SELECT')

            bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
            
            if not selection:
                bpy.ops.mesh.select_all(action='DESELECT')

        return {'FINISHED'}

    
classes = (
    MESH_OT_armored_focus,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)