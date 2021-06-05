# v1.2

import bpy


class ARMORED_OT_duplicate(bpy.types.Operator):
    '''Duplicates the selected faces into a new object and activates the Move Tool.

(www.armoredColony.com)'''

    bl_idname = 'mesh.armored_duplicate'
    bl_label  = 'ARMORED Duplicate'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        original_ob = context.object

        try:
            bpy.ops.mesh.duplicate_move()
            bpy.ops.mesh.separate(type='SELECTED')
            
        except RuntimeError:
            self.report({'ERROR'}, 'ARMORED Duplicate\n You need to select something first.')
            return {'CANCELLED'}

        # Create a new variable that only contains the new object.
        sel = context.selected_objects
        if original_ob in sel: 
            sel.remove(original_ob)

        # Exit object mode for the old object and deselect it.
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # Set the new object to be active and selected.
        context.view_layer.objects.active = sel[0]
        sel[0].select_set(True)

        # Re-enter Edit mode and select the duplicated geo.
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        # bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT', use_even_offset=True)
        bpy.ops.wm.tool_set_by_id(name='builtin.move')

        return {'FINISHED'}


classes = (
    ARMORED_OT_duplicate,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

