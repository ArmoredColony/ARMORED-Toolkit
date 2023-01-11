import bpy


class MESH_OT_armored_control_loops(bpy.types.Operator):
	'''Use the bevel tool to create control loops for subdivision surfaces.

armoredColony.com '''

	bl_idname = 'mesh.armored_control_loops'
	bl_label = 'ARMORED Control Loops'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		bpy.ops.mesh.armored_select_hard_edges()	# EXTERNAL SCRIPT.
		bpy.ops.mesh.bevel('INVOKE_DEFAULT', segments=2, profile=1, miter_outer='ARC')

		return {'FINISHED'}


classes = (
	MESH_OT_armored_control_loops,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)