import bpy
from bpy.props import StringProperty
import os

from .. utils import addon



class ARMORED_OT_load_materials(bpy.types.Operator):
    '''Load Armored Colony Materials.

(www.armoredColony.com)'''
 
    bl_idname = 'view3d.armored_load_materials'
    bl_label = 'ARMORED Load Materials'
    bl_options = {'REGISTER', 'UNDO'}

    # directory = StringProperty(subtype='DIR_PATH')
    # filename = StringProperty(subtype='FILE_NAME')

    def execute(self, context):
        # directory = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 
        filename = 'Armored Materials.blend'
        filepath = os.path.join(addon.get_path(), 'resources', 'materials', filename)

        local_materials = {mat.name for mat in bpy.data.materials}
        
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            external_materials = [mat for mat in data_from.materials if mat.startswith('ARM')]
            # data_to.materials = ['ARM-Base']
            # data_to.materials = data_from.materials #  append all materials from blend

            for mat in external_materials:
                if mat in local_materials:
                    continue
                
                data_to.materials.append(mat)

        return {'FINISHED'}


classes = (
    ARMORED_OT_load_materials,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)