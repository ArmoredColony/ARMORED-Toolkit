version = (1, 0, 1)

import bpy

# I DIDN'T KNOW HOW TO KEYMAP MACROS WITH CUSTOM PROPERTY VALUES AT THE TIME
# SO I MADE THIS OPERATOR INSTEAD.

class MESH_OT_armored_extrude(bpy.types.Operator):
	'''Extrude faces along their normals, with <even_offset> set to True by default.

	armoredColony.com '''
	
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
	MESH_OT_armored_extrude,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)