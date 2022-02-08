# v1.0

import bpy


class SCULPT_OT_armored_remesh(bpy.types.Operator):
	'''Voxel Remesh with volume, detail and vertex color preservation.

	armoredColony.com '''

	bl_idname = 'sculpt.armored_remesh'
	bl_label = 'ARMORED Remesh'
	bl_options = {'REGISTER', 'UNDO'}

	def transfer_vertex_color(self, context):
		context.view_layer.objects.active = self.temp_copy
		bpy.ops.object.data_transfer(data_type='VCOL')
		context.view_layer.objects.active = self.active

	def create_temp_copy(self):
		self.temp_copy = self.active.copy()
		self.temp_copy.data = self.active.data.copy()
		bpy.context.collection.objects.link(self.temp_copy)

	def destroy_temp_copy(self):
		bpy.data.meshes.remove(self.temp_copy.data)

	def set_remesh_settings(self):
		data = self.active.data
		data.use_remesh_preserve_volume = True
		# data.use_remesh_preserve_sculpt_face_sets = True
		# data.use_remesh_preserve_paint_mask = True
		
	def execute(self, context):
		self.active = context.active_object
		self.create_temp_copy()

		# self.set_remesh_settings()
		bpy.ops.object.voxel_remesh()

		self.transfer_vertex_color(context)
		self.destroy_temp_copy()
		# bpy.ops.ed.undo_push()
		return {'FINISHED'}


classes = (
	SCULPT_OT_armored_remesh,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
