# v1.0

import bpy


class ARMORED_OT_open_url(bpy.types.Operator):
    '''Go to training URL'''

    bl_idname  = 'armored.open_url'
    bl_label   = 'ARMORED Open URL'
    bl_options = {'REGISTER', 'INTERNAL'}

    url : bpy.props.StringProperty(default='www.armoredColony.com')

    def execute(self, context):
        bpy.ops.wm.url_open(url=self.url)
        return {'FINISHED'}

classes = (
    ARMORED_OT_open_url,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)    


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
