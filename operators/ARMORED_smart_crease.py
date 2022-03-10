import bpy


class MESH_OT_armored_smart_crease(bpy.types.Operator):
	'''Run the appropriate crease tool for the current component mode.

	armoredColony.com '''

	bl_idname = 'mesh.armored_smart_crease'
	bl_label = 'ARMORED Crease'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None
	
	def execute(self, context):
		mode = self._get_mode(context)
		if mode [0]:	## Vertex Mode
			bpy.ops.transform.vert_crease('INVOKE_DEFAULT')
		else:
			bpy.ops.transform.edge_crease('INVOKE_DEFAULT')

		return {'FINISHED'}


	def _get_mode(self, context) -> tuple[bool, bool, bool]:
		'''Returns the Vertex, Edge and Face mode states'''
		
		return context.tool_settings.mesh_select_mode


classes = (
	MESH_OT_armored_smart_crease,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)