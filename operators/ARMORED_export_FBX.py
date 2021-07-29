import bpy
from bpy.props import StringProperty
import os


# folder = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 
# filename = 'temp.fbx'
# desktop_path = os.environ['HOMEPATH'], 'Desktop'


class ARMORED_OT_export_FBX(bpy.types.Operator):
    '''Export selected as FBX.

(www.armoredColony.com)'''
 
    bl_idname = 'object.armored_export_fbx'
    bl_label = 'ARMORED Export FBX'
    bl_options = {'REGISTER', 'UNDO'}

    directory = StringProperty(subtype='DIR_PATH')
    filename = StringProperty(subtype='FILE_NAME')

    # @classmethod
    # def poll(cls, context):
    #     return context.mode == 'EDIT_MESH'

    def execute(self, context):
        sel = context.selected_objects
        if not sel:
            self.report({'WARNING'}, 'Select the objects you want to export')
            return {'CANCELLED'}

        self.directory = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 
        # self.directory = os.path.join(os.environ['HOMEPATH'], 'Desktop')
        self.filename = 'temp.fbx'

        path = os.path.join(self.directory, self.filename)
        bpy.ops.export_scene.fbx(
            filepath=path, 
            use_selection=True, 
            bake_space_transform=True,
            mesh_smooth_type='FACE',
            bake_anim=True,
            )

        self.report({'INFO'}, f'Exported {self.filename} to {self.directory}')
        return {'FINISHED'}


classes = (
    ARMORED_OT_export_FBX,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)