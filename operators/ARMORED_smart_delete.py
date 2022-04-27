import bpy


class MESH_OT_armored_smart_delete(bpy.types.Operator):
	'''Deletes components based on your selection mode (vertex, edge, face) without aditional menus.

armoredColony.com '''

	bl_idname = 'mesh.armored_smart_delete'
	bl_label = 'ARMORED Smart Delete'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'

	def invoke(self, context, event):
		mode = context.tool_settings.mesh_select_mode[:]

		if mode[0]:
			bpy.ops.mesh.delete(type='VERT')

		elif mode[1]:
			bpy.ops.mesh.delete(type='EDGE')
			# bpy.ops.mesh.dissolve_mode(use_verts=True)
		
		elif mode[2]:
			bpy.ops.mesh.delete(type='FACE')

		return {'FINISHED'}
		

classes = (
	MESH_OT_armored_smart_delete,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)