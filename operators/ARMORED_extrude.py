import bpy

# v1.0

class ARMORED_OT_extrude(bpy.types.Operator):
    '''Extrude faces along their individual normals (like Maya).

(www.armoredColony.com)
'''
    
    bl_idname = 'mesh.armored_extrude'
    bl_label = 'ARMORED Extrude'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        bpy.ops.mesh.extrude_region()
        bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT', use_even_offset=True)

        return {'FINISHED'}


classes = (
    ARMORED_OT_extrude,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)