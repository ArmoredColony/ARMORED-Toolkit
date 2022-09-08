# v2.0

import bpy
import mathutils

import os
import json
import copy
import collections
import functools
import operator

from pprint import pprint


def flatten(d, parent_key='', sep='.') -> dict:
	items = []
	for key, val in d.items():
		new_key = parent_key + sep + key if parent_key else key

		if isinstance(val, collections.abc.MutableMapping):
			items.extend(flatten(val, parent_key=new_key, sep=sep).items())
		else:
			items.append((new_key, val))

	return dict(items)


# def nested_set(d: dict, keys, val):
# 	d = {}
# 	for key in keys[:-1]:
# 		d = d.setdefault(key, {})
# 	d[keys[-1]] = val


def set_nested_item(d: dict, map_list: list[str], val) -> dict:
	'''Set Item in nested dictionary'''

	functools.reduce(operator.getitem, map_list[:-1], d)[map_list[-1]] = val
	return d


class VIEW3D_OT_armored_silhouette(bpy.types.Operator):
	'''Toggle back and forth between flat shading and the previous lighting mode.
	
	armoredColony.com '''
	
	bl_idname = 'view3d.armored_silhouette'
	bl_label = 'ARMORED Silhouette'
	bl_options = {'REGISTER'}
	
	SILHOUETTE_SETTINGS = {
		'context': {
			'space_data': {
				'shading': {
					'light': 'FLAT',
					'color_type': 'SINGLE',
					'single_color': (.8, .8, .8),		# WHITE SILHOUETTE
					# 'single_color': (.015, .015, .015),	# BLACK SILHOUETTE
					# 'background_type': 'VIEWPORT',	# UNCOMMENT TO CHANGE BACKGROUND COLOR
					# 'background_color': (0, 0, 0),	# BLACK BACKGROUND
					# 'background_color': (1, 1, 1),	# WHITE BACKGROUND
					# 'show_cavity': False,
					'cavity_type': 'WORLD',
					'cavity_ridge_factor': 0.0,
					'cavity_valley_factor': 0.25,
					'show_object_outline': False,
					'show_xray': False,
					'show_shadows': False,
				},
				'overlay': {
					'show_fade_inactive': False,
					},
			},
			'scene': {
				'display': {
					'matcap_ssao_samples': 124,
					'matcap_ssao_distance': 0.1,
					'matcap_ssao_attenuation': 1.0,
				},
				'tool_settings': {
					'sculpt': {
						'show_face_sets': False,
					}
				}
			}
		}
	}

	def invoke(self, context, event):
		self.filepath = os.path.join(os.path.dirname(__file__), 'view_settings.json')

		if context.space_data.shading.light == 'FLAT':
			if os.path.exists(self.filepath):
				print('Exit Silhouette Mode')
				self.restore_view_settings(context)
			else:
				print('Enter Silhouette Mode')
				self.save_view_settings(context)
				self.set_flat_mode(context)
		else:
			print('Enter Silhouette Mode')
			self.save_view_settings(context)
			self.set_flat_mode(context)

		return {'FINISHED'}


	def set_flat_mode(self, context):
		'''
		Set the necessary viewport settings to mimic a silhouette mode (referencing the SILHOUETTE_SETTINGS: dict).
		'''

		flat_view_settings = flatten(self.SILHOUETTE_SETTINGS)

		for flat_key, val in flat_view_settings.items():
			data_path, attr_name = flat_key.rsplit('.', 1)
			setattr(eval(data_path), attr_name, val)

	
	def save_view_settings(self, context):
		'''
		Save the current viewport settings to .json before changing anything.
		'''

		saved_settings = copy.deepcopy(self.SILHOUETTE_SETTINGS)
		flat_view_settings = flatten(saved_settings)

		for flat_key, _ in flat_view_settings.items():
			keys = flat_key.split('.')
			data_path, attr_name = flat_key.rsplit('.', 1)

			new_val = getattr(eval(data_path), attr_name)
			new_val = self._convert_to_valid_type(new_val)

			saved_settings = set_nested_item(saved_settings, keys, new_val)
		
		with open(self.filepath, 'w') as write:
			json.dump(saved_settings, write, indent=8)

	def restore_view_settings(self, context):
		'''
		Restore the viewport settings from the saved .json.
		'''

		with open(self.filepath, 'r') as read:  
			saved_settings = json.load(read)
		
		flat_view_settings = flatten(saved_settings)
		
		for flat_key, val in flat_view_settings.items():
			data_path, attr_name = flat_key.rsplit('.', 1)
			setattr(eval(data_path), attr_name, val)
	
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