import bpy


class VIEW3D_OT_armored_toggle_overlays(bpy.types.Operator):
	'''Toggles the visibility of Overlays AND Gizmos.

armoredColony.com '''

	bl_idname = 'view3d.armored_toggle_overlays'
	bl_label = 'ARMORED Toggle Overlays'
	bl_options = {'REGISTER'}

	# @classmethod
	# def poll(cls, context):
	# 	return context.active_object is not None

	def execute(self, context):
		space_data = context.space_data
		state = space_data.overlay.show_overlays
		# n_panel = space_data.show_region_ui

		space_data.overlay.show_overlays = not state
		space_data.show_gizmo = not state
		
		return {'FINISHED'}


classes = (
	VIEW3D_OT_armored_toggle_overlays,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)