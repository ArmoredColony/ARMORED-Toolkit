# v1.2

import bpy
import mathutils

import os
import json

from .. utils import addon


filepath = os.path.join(os.path.dirname(__file__), 'blender_preferences.json')


ARMORED_COLONY_PREFERENCES = {

	'context.preferences.view.show_splash': False,
	'context.preferences.view.show_tooltips_python': True,
	'context.preferences.inputs.drag_threshold_mouse': 1,
	'context.preferences.inputs.invert_mouse_zoom': True,
	'context.preferences.edit.undo_steps': 150,
	
	'context.scene.unit_settings.scale_length': .01,
	'context.scene.unit_settings.length_unit': 'CENTIMETERS',
	'context.scene.eevee.use_gtao': True,
	'context.scene.eevee.use_ssr': True,

	'context.scene.world.color': [0.215861, 0.215861, 0.215861],	
}


class ARMORED_OT_load_custom_preferences(bpy.types.Operator):
	bl_idname = 'armored.load_custom_preferences'
	bl_label = 'ARMORED Load Custom Preferences'
	bl_options = {'REGISTER', 'INTERNAL'}

	@classmethod
	def description(cls, context, event):
		list_description = []
		for key, val in ARMORED_COLONY_PREFERENCES.items():
			_, attr_name = key.rsplit('.', 1)
			attr_name = attr_name.replace('_', ' ')
			list_description.append(f"{attr_name}: {val}")

		return 'Loads my custom system preferences\n NOTE: these settings persist even if the addon is disabled so use the Unload button to return them to their previous state:\n' + '\u2022 ' + ('\n\u2022 '.join(list_description))

	def execute(self, context):
		self._load_custom_preferences(context)

		return {'FINISHED'}
	

	def _load_custom_preferences(self, context) -> None:

		current_preferences = self._get_current_preferences(context)

		with open(filepath, 'w') as write:
			json.dump(current_preferences, write, indent=8)

		for key, val in ARMORED_COLONY_PREFERENCES.items():
			data_path, attr_name = key.rsplit('.', 1)
			setattr(eval(data_path), attr_name, val)

			if addon.debug(): 
				print(f'ARMORED-Toolkit: Set \'{key}\' = {val}')

		if addon.debug(): 
			print('LOADED Armored Preferences')
	
	def _save_preferences(self, context) -> None:
		'''
		Save the current preferences to JSON before changing anything.
		'''

		preferences = self._get_current_preferences(context)

		with open(filepath, 'w') as write:
			json.dump(preferences, write, indent=8)


	def _get_current_preferences(self, context) -> dict:
		'''
		Return a dictionary of Blender's preferences (only the ones we intend to change).
		'''

		current_preferences = {}
		for key in ARMORED_COLONY_PREFERENCES.keys():
			data_path, attr_name = key.rsplit('.', 1)
			blender_value = getattr(eval(data_path), attr_name)
			current_preferences[key] = self._convert_to_valid_type(blender_value)
		
		return current_preferences
	
	def _convert_to_valid_type(self, val):
		if isinstance(val, (mathutils.Vector, mathutils.Color)):
			return tuple(val)
		
		return val

	
class ARMORED_OT_unload_custom_preferences(bpy.types.Operator):
	bl_idname = 'armored.unload_custom_preferences'
	bl_label = 'ARMORED Unload Custom Preferences'
	bl_options = {'REGISTER', 'INTERNAL'}

	@classmethod
	def description(cls, context, event):
		list_description = []
		for key in ARMORED_COLONY_PREFERENCES.keys():
			_, attr_name = key.rsplit('.', 1)
			attr_name = attr_name.replace('_', ' ')
			list_description.append(f"{attr_name}")

		return 'Reverts the following preferences to whatever they were before (not necessarily the Blender Defaults):\n' + '\u2022 ' + ('\n\u2022 '.join(list_description))

	def execute(self, context):
		self._unload_custom_preferences(context)
		return {'FINISHED'}
	

	def _unload_custom_preferences(self, context):
		if not os.path.exists(filepath):
			print('ARMORED-Toolkig: FAILED to revert preferences. No preferences file found.')
			return

		with open(filepath, 'r') as read:  
			old_preferences = json.load(read)
		
		for key, val in old_preferences.items():
			data_path, attr_name = key.rsplit('.', 1)
			setattr(eval(data_path), attr_name, val)
			
			if addon.debug(): 
				print(f'ARMORED-Toolkit: Set \'{key}\' = {val}')

		if addon.debug(): 
			print('UNLOADED Armored Preferences')



classes = (
	ARMORED_OT_load_custom_preferences,
	ARMORED_OT_unload_custom_preferences,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)