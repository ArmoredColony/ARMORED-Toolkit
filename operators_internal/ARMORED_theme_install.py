# v1.2

import bpy
from bpy.props import StringProperty
import os
from .. utils import(
    paths,
)


class ARMORED_OT_theme_install(bpy.types.Operator):
    '''Install my personal Blender Theme.

armoredColony.com '''
    
    bl_idname = 'armored.theme_install'
    bl_label = 'ARMORED Theme Install'
    bl_options = {'REGISTER', 'INTERNAL'}

    filename: StringProperty(name='Theme File Name', default='Armored_Colony.xml')
    
    def execute(self, context):
        file_path = os.path.join(paths.AddonPaths.themes, self.filename)    # The source, not the target.
        bpy.ops.preferences.theme_install(filepath=file_path, overwrite=True)
        
        self.report({'INFO'}, f'LOADED Theme: {self.filename}')
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