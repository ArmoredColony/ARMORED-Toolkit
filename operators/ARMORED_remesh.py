# v2.0

import bpy

class SCULPT_OT_armored_remesh(bpy.types.Operator):
	'''Voxel Remesh with vertex color preservation.

	armoredColony.com '''

	bl_idname = 'sculpt.armored_remesh'
	bl_label = 'ARMORED Remesh'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		self._set_remesh_settings(context)
		bpy.ops.object.voxel_remesh()
		return {'FINISHED'}
	
	def _set_remesh_settings(self, context):
		data = context.active_object.data
		data.use_remesh_preserve_vertex_colors = True
		# data.use_remesh_preserve_volume = True
		# data.use_remesh_preserve_sculpt_face_sets = True
		# data.use_remesh_preserve_paint_mask = True
		

classes = (
	SCULPT_OT_armored_remesh,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
