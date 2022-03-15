import bpy


class OBJECT_OT_switch_and_focus(bpy.types.Operator):
	'''Operator Description.

	armoredColony.com '''

	bl_idname = 'object.armored_switch_and_focus'
	bl_label = 'ARMORED Transfer and Focus'
	bl_options = {'REGISTER', 'UNDO'}

	# @classmethod
	# def poll(cls, context):
	# 	return context.active_object is not None

	def execute(self, context):
		bpy.ops.object.transfer_mode('INVOKE_DEFAULT')
		bpy.ops.view3d.armored_focus('INVOKE_DEFAULT')
		return {'FINISHED'}


classes = (
	OBJECT_OT_switch_and_focus,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)