version = (1, 2, 0)

import bpy


class VIEW3D_OT_armored_transfer_data(bpy.types.Operator):
	'''Duplicate the `object.data` of the active object to all selected objects and optionally turn them into linked duplicates.

	armoredColony.com '''

	bl_idname = 'view3d.armored_transfer_data'
	bl_label = 'ARMORED Transfer Data'
	bl_options = {'REGISTER', 'UNDO'}

	linked: bpy.props.BoolProperty(name='Linked', default=False)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		active = context.active_object
		selected = [obj for obj in context.selected_objects if obj is not active]

		for obj in selected:
			if self.linked:
				obj.data = active.data
			else:
				obj.data.name += '_old'
				obj.data = active.data.copy()
				obj.data.name = obj.name

		return {'FINISHED'}


classes = (
	VIEW3D_OT_armored_transfer_data,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)