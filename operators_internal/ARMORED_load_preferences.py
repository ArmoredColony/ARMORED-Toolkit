version = (2, 1, 0)

import bpy

from .. utils import addon


USER_PREFERENCES = {

	'context.preferences.view.show_splash': False,
	'context.preferences.view.show_tooltips_python': True,
	'context.preferences.inputs.drag_threshold_mouse': 1,
	'context.preferences.inputs.invert_mouse_zoom': True,
	'context.preferences.edit.undo_steps': 150,

	'context.scene.unit_settings.scale_length': .01,
	'context.scene.unit_settings.length_unit': 'CENTIMETERS',

	'context.scene.world.color': [0.215861, 0.215861, 0.215861],

	'context.scene.render.engine': 'CYCLES',

	'context.scene.cycles.device': 'GPU',
	'context.scene.cycles.use_preview_denoising': True,
	'context.scene.cycles.denoiser': 'OPTIX',

	'context.scene.eevee.use_gtao': True,
	'context.scene.eevee.use_ssr': True,
	'context.scene.eevee.taa_samples': 64,
	'context.scene.eevee.gtao_distance': 50,	# Assuming scale_length of .01
	'context.scene.eevee.ssr_thickness': 50,
	'context.scene.eevee.use_ssr_halfres': False,
	'context.scene.eevee.ssr_quality': 1,
}

FACTORY_USER_PREFERENCES = {

	'context.preferences.view.show_splash': True,
	'context.preferences.view.show_tooltips_python': False,
	'context.preferences.inputs.drag_threshold_mouse': 3,
	'context.preferences.inputs.invert_mouse_zoom': False,
	'context.preferences.edit.undo_steps': 32,

	'context.scene.unit_settings.scale_length': 1,
	'context.scene.unit_settings.length_unit': 'METERS',

	'context.scene.world.color': [0.050876, 0.050876, 0.050876],

	'context.scene.render.engine': 'BLENDER_EEVEE',

	'context.scene.cycles.device': 'CPU',
	'context.scene.cycles.use_preview_denoising': False,
	'context.scene.cycles.denoiser': 'OPENIMAGEDENOISE',

	'context.scene.eevee.use_gtao': False,
	'context.scene.eevee.use_ssr': False,
	'context.scene.eevee.taa_samples': 32,
	'context.scene.eevee.gtao_distance': 20,	# Assuming scale_length of 1
	'context.scene.eevee.ssr_thickness': 20,
	'context.scene.eevee.use_ssr_halfres': True,
	'context.scene.eevee.ssr_quality': .25,
}

# Use str 'space_data' instead of 'context.space_data'
# because we want to affect all spaces and not just the active one.
SPACE_SETTINGS = {
	'space_data.overlay.grid_scale': USER_PREFERENCES.get('context.scene.unit_settings.scale_length', 1.0),
	'space_data.overlay.show_stats': True,
	'space_data.shading.use_scene_world_render': False,
	# 'space_data.clip_end': 10000,

}

FACTORY_SPACE_SETTINGS = {
	'space_data.overlay.grid_scale': 1.0,
	'space_data.overlay.show_stats': False,
	'space_data.shading.use_scene_world_render': True,
	# 'space_data.clip_end': 1000,
}


def set_user_preferences(context, user_preferences):
	for key, val in user_preferences.items():
		data_path, attr_name = key.rsplit('.', 1)

		try:
			setattr(eval(data_path), attr_name, val)
		except Exception as error:
			print(error)

		if addon.debug(): 
			print(f'ARMORED-Toolkit: Set \'{key}\' = {val}')


def set_space_settings(space_settings):
	for screen in bpy.data.screens:
		for area in screen.areas:
			for space_data in area.spaces:
				if space_data.type != 'VIEW_3D':
					continue
				
				for key, val in space_settings.items():
					data_path, attr_name = key.rsplit('.', 1)

					try:
						setattr(eval(data_path), attr_name, val)
					except Exception as error:
						print(error)

					if addon.debug(): 
						print(f'ARMORED-Toolkit: Set \'{key}\' = {val}')


class ARMORED_OT_load_preferences(bpy.types.Operator):

	bl_idname = 'armored.load_preferences'
	bl_label = 'ARMORED Load Preferences'
	bl_options = {'REGISTER', }

	@classmethod
	def description(cls, context, event):

		SETTINGS = {**USER_PREFERENCES, **SPACE_SETTINGS}

		list_description = []
		for key, val in SETTINGS.items():
			_, attr_name = key.rsplit('.', 1)
			attr_name = attr_name.replace('_', ' ')
			list_description.append(f"{attr_name}: {val}")

		return 'Loads my custom system preferences\n NOTE: these settings persist when the addon is disabled; use the Unload button to return Blender to factory defaults:\n' + '\u2022 ' + ('\n\u2022 '.join(list_description))
	
	def execute(self, context):
		self._load_custom_preferences(context)

		return {'FINISHED'}
	

	def _load_custom_preferences(self, context) -> None:
		set_user_preferences(context, USER_PREFERENCES)
		set_space_settings(SPACE_SETTINGS)

		# bpy.ops.wm.save_homefile()
		bpy.ops.wm.save_userpref()
		
		self.report({'INFO'}, 'ARMORED-Toolkit: LOADED Armored Preferences')

	
class ARMORED_OT_unload_preferences(bpy.types.Operator):
	
	bl_idname = 'armored.unload_preferences'
	bl_label = 'ARMORED Unload Preferences'
	bl_options = {'REGISTER', 'INTERNAL'}

	@classmethod
	def description(cls, context, event):

		SETTINGS = {**FACTORY_USER_PREFERENCES, **FACTORY_SPACE_SETTINGS}

		list_description = []
		for key, val in SETTINGS.items():
			_, attr_name = key.rsplit('.', 1)
			attr_name = attr_name.replace('_', ' ')
			list_description.append(f"{attr_name}: {val}")

		return 'Restore the following preferences to factory defaults:\n' + '\u2022 ' + ('\n\u2022 '.join(list_description))

	def execute(self, context):
		self._unload_custom_preferences(context)

		return {'FINISHED'}
	

	def _unload_custom_preferences(self, context):
		set_user_preferences(context, FACTORY_USER_PREFERENCES)
		set_space_settings(FACTORY_SPACE_SETTINGS)

		# bpy.ops.wm.save_homefile()
		bpy.ops.wm.save_userpref()

		self.report({'INFO'}, 'ARMORED-Toolkit: RESET Preferences to Factory Defaults')


classes = (
	ARMORED_OT_load_preferences,
	ARMORED_OT_unload_preferences,

)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)