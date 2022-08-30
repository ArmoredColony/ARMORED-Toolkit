# v1.0

import bpy
from bpy.props import StringProperty, BoolProperty


class VIEW3D_OT_armored_silhouette(bpy.types.Operator):
	'''Toggle back and forth between flat shading and the previous lighting mode.
	
	armoredColony.com '''
	
	bl_idname = 'view3d.armored_silhouette'
	bl_label = 'ARMORED Silhouette'
	bl_options = {'REGISTER'}
	
	last_mode   : StringProperty(name='Previous Mode',   default='MATCAP')
	last_color  : StringProperty(name='Previous Color',  default='MATERIAL')
	last_cavity : StringProperty(name='Previous Cavity', default='BOTH')

	last_fade_inactive : BoolProperty(name='Previous Fade Inactive', default=False)

	def set_flat_mode(self, context):
		space_data = context.space_data
		space_data.shading.light = 'FLAT'
		space_data.shading.color_type = 'SINGLE'
		space_data.shading.cavity_type = 'WORLD'
		space_data.overlay.show_fade_inactive = False
	
	def store_last_mode(self, context):
		space_data = context.space_data
		self.last_mode = space_data.shading.light
		self.last_color = space_data.shading.color_type
		self.last_cavity = space_data.shading.cavity_type
		self.last_fade_inactive = space_data.overlay.show_fade_inactive

	def set_from_last_mode(self, context):
		space_data = context.space_data
		space_data.shading.light = self.last_mode
		space_data.shading.color_type = self.last_color
		space_data.shading.cavity_type = self.last_cavity
		space_data.overlay.show_fade_inactive = self.last_fade_inactive

	def invoke(self, context, event):
		if context.space_data.shading.light == 'FLAT':
			self.set_from_last_mode(context)
		else:
			self.store_last_mode(context)
			self.set_flat_mode(context)

		return {'FINISHED'}

	
classes = (
	VIEW3D_OT_armored_silhouette,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)