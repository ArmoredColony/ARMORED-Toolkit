version = (2, 5, 1)

import bpy
import mathutils

import os
import json


filepath = os.path.join(os.path.dirname(__file__), 'view_settings.json')

class VIEW3D_OT_armored_silhouette(bpy.types.Operator):
	'''Toggle back and forth between flat shading and the previous lighting mode.
	
	armoredColony.com '''
	
	bl_idname = 'view3d.armored_silhouette'
	bl_label = 'ARMORED Silhouette'
	bl_options = {'REGISTER'}

	SILHOUETTE_SETTINGS = {
		'context.space_data.shading.light': 'FLAT',
		'context.space_data.shading.color_type': 'SINGLE',
		'context.space_data.shading.single_color': (.8, .8, .8),		# WHITE SILHOUETTE
		# 'context.space_data.shading.single_color': (.015, .015, .015),	# BLACK SILHOUETTE
		# 'context.space_data.shading.background_type': 'VIEWPORT',		# UNCOMMENT TO CHANGE BACKGROUND COLOR
		# 'context.space_data.shading.background_color': (0, 0, 0),		# BLACK BACKGROUND
		# 'context.space_data.shading.background_color': (1, 1, 1),		# WHITE BACKGROUND
		# 'context.space_data.shading.show_cavity': False,
		'context.space_data.shading.cavity_type': 'WORLD',
		'context.space_data.shading.cavity_ridge_factor': 0.0,
		'context.space_data.shading.cavity_valley_factor': 0.25,
		'context.space_data.shading.show_object_outline': False,
		'context.space_data.shading.show_xray': False,
		'context.space_data.shading.show_shadows': False,

		'context.space_data.overlay.show_fade_inactive': False,

		'context.scene.display.matcap_ssao_samples': 124,
		'context.scene.display.matcap_ssao_distance': 0.1,
		'context.scene.display.matcap_ssao_attenuation': 1.0,

		'context.scene.tool_settings.sculpt.show_face_sets': False,
	}

	def execute(self, context):

		if context.space_data.shading.light == 'FLAT':
			if os.path.exists(filepath):
				self._restore_view_settings(context)
			else:
				self._save_view_settings(context)
				self._set_flat_mode(context)
		else:
			self._save_view_settings(context)
			self._set_flat_mode(context)

		return {'FINISHED'}


	# PRIMARY METHODS

	def _set_flat_mode(self, context):
		'''
		Set the necessary viewport settings to mimic a silhouette mode (referencing the SILHOUETTE_SETTINGS: dict).
		'''

		for key, val in self.SILHOUETTE_SETTINGS.items():
			data_path, attr_name = key.rsplit('.', 1)
			setattr(eval(data_path), attr_name, val)
		
	def _save_view_settings(self, context):
		'''
		Save the current viewport settings to JSON before changing anything.
		'''

		view_settings = self._get_current_view_settings(context)

		with open(filepath, 'w') as write:
			json.dump(view_settings, write, indent=8)


	def _restore_view_settings(self, context):
		'''
		Restore the viewport settings from the saved .json.
		'''

		with open(filepath, 'r') as read:  
			old_preferences = json.load(read)

		for key, val in old_preferences.items():
			data_path, attr_name = key.rsplit('.', 1)
			setattr(eval(data_path), attr_name, val)
		

	# HELPER METHODS

	def _get_current_view_settings(self, context) -> dict:
		'''
		Return a dictionary of Blender's viewport settings (only the ones we intend to change).
		'''

		current_settings = {}
		for key in self.SILHOUETTE_SETTINGS.keys():
			data_path, attr_name = key.rsplit('.', 1)
			blender_value = getattr(eval(data_path), attr_name)
			current_settings[key] = self._convert_to_valid_type(blender_value)
		
		return current_settings

	def _convert_to_valid_type(self, val):
		if isinstance(val, (mathutils.Vector, mathutils.Color)):
			return tuple(val)
		
		return val


	
classes = (
	VIEW3D_OT_armored_silhouette,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)