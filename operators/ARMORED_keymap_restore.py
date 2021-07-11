import bpy

# v1.0

class ARMORED_OT_keymap_restore(bpy.types.Operator):
    '''Restore keymaps to defaults (addon keymaps seem unnafected).

(www.armoredColony.com)'''
    
    bl_idname = 'armored.keymap_restore'
    bl_label = 'ARMORED Keymap Restore'
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.preferences.keymap_restore(all=True)
        self.report({'WARNING'}, 'Keymap Editor was Restored')
        return {'FINISHED'}


classes = (
    ARMORED_OT_keymap_restore,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)