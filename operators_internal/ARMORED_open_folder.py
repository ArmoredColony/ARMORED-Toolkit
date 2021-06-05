import bpy
import os


class ARMORED_OT_open_folder(bpy.types.Operator):
    '''Open Folder'''
    
    bl_idname = 'armored.open_folder'
    bl_label = 'ARMORED Open Folder'
    bl_options = {'REGISTER', 'INTERNAL'}
    
    path : bpy.props.StringProperty()

    def execute(self, context):
        # path = os.path.join(dirname(dirname(__file__)), self.sub_folder)
        os.startfile(self.path)
        return {'FINISHED'}


classes = (
    ARMORED_OT_open_folder,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)