import bpy
import os
from bpy.props import StringProperty
from .. utils.addon import get_path

# v1.0

class ARMORED_OT_theme_install(bpy.types.Operator):
    '''Install a theme from the Armored Toolkit.

www.armoredColony.com'''
    
    bl_idname = 'armored.theme_install'
    bl_label = 'ARMORED Theme Install'
    bl_options = {'REGISTER', 'INTERNAL'}

    filename: StringProperty(name='Theme File Name', default='armored_colony.xml')
    
    def execute(self, context):
        path = os.path.join(get_path(), 'resources', 'themes', self.filename)
        bpy.ops.preferences.theme_install(filepath=path, overwrite=True)
        
        self.report({'INFO'}, 'LOADED Armored Theme')
        # print('LOADED Armored Theme.')
        return {'FINISHED'}


classes = (
    ARMORED_OT_theme_install,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)