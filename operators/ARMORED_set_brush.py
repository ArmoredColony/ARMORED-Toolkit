import bpy


class SCULPT_OT_armored_set_brush(bpy.types.Operator):
	'''Make any brush active (even custom brushes) by name.

armoredColony.com '''

	bl_idname = 'sculpt.armored_set_brush'
	bl_label = 'ARMORED Set Brush'
	bl_options = {'REGISTER'}

	name: bpy.props.StringProperty(
		name='Name')

	@classmethod
	def poll(cls, context):
		return context.mode == 'SCULPT'

	def execute(self, context):
		try:
			context.tool_settings.sculpt.brush = bpy.data.brushes[self.name]
		except KeyError:
			self.report({'WARNING'}, f'\'{self.name}\' is not a valid brush preset name.')

		return {'FINISHED'}


classes = (
	SCULPT_OT_armored_set_brush,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)