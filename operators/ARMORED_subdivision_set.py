import bpy


class OBJECT_OT_armored_subdivision_set(bpy.types.Operator):
	'''Same as the default operator for setting your subdivision level (CTRL+1, etc) but without any Undo History.

armoredColony.com '''

	bl_idname = 'object.armored_subdivision_set'
	bl_label = 'ARMORED Set Subdivision'
	bl_options = {'REGISTER'}

	level: bpy.props.IntProperty(name='Level', default=1, min=0, soft_min=0, max=100, soft_max=6)

	@classmethod
	def poll(cls, context):
		return context.selected_objects
	
	def invoke(self, context, event):
		bpy.ops.object.subdivision_set(level=self.level)
		return {'FINISHED'}

	# def execute(self, context):
		# return {'FINISHED'}


classes = (
	OBJECT_OT_armored_subdivision_set,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)