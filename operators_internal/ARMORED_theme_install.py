version = (2, 0, 1)

import bpy
import os
import dataclasses

from .. utils import (
	addon,
	paths,
	)


@dataclasses.dataclass(frozen=True)
class Shading:
	type:         str = None
	light:        str = None
	studio_light: str = None


SHADING_PREFERENCES = {

	'Layout':         Shading('SOLID', 'MATCAP', 'ARC Lambert NVil.png'),
	'Modeling':       Shading('SOLID', 'MATCAP', 'ARC Lambert NVil.png'),
	'Sculpting':      Shading('SOLID', 'MATCAP', 'ARC Default.png'),
	'UV Editing':     Shading('SOLID', 'MATCAP', 'ARC Lambert NVil.png'),
	'Animation':      Shading('SOLID', 'MATCAP', 'ARC Lambert NVil.png'),
	'Geometry Nodes': Shading('SOLID', 'MATCAP', 'ARC Lambert NVil.png'),
	'Scripting':      Shading('SOLID', 'MATCAP', 'ARC Lambert NVil.png'),
}

FACTORY_SHADING_PREFERENCES = {

	'Layout':         Shading('SOLID', 'STUDIO', None),
	'Modeling':       Shading('SOLID', 'STUDIO', None),
	'Sculpting':      Shading('SOLID', 'MATCAP', 'basic_1.exr'),
	'UV Editing':     Shading('SOLID', 'STUDIO', None),
	'Animation':      Shading('SOLID', 'STUDIO', None),
	'Geometry Nodes': Shading('SOLID', 'STUDIO', None),
	'Scripting':      Shading('SOLID', 'STUDIO', None),
}

def enable_required_resources(required_resources: list[str]):
	'''
	Enable the resources required by other preference loading functions.
	'''

	for resource in required_resources:
		if getattr(addon.prefs(), resource) is None:
			if addon.debug():
				print(f'ARMORED-Toolkit: Resource {resource} not found. Skipping.')
			continue

		if getattr(addon.prefs(), resource) is True:
			if addon.debug():
				print(f'ARMORED-Toolkit: Resource {resource} is already ENABLED. Skipping.')
			continue

		setattr(addon.prefs(), resource, True)
		if addon.debug():
			print(f'ARMORED-Toolkit: \'Load Preferences\' ENABLED Resource {resource}.')


def set_favorite_hdri(hdri_name: str):
	'''
	Iterates through all screens and set the MATERIAL `shading_type` to use the specified `hdri_name`.
	'''

	for screen in bpy.data.screens:
		for area in screen.areas:
			for space in area.spaces:
				if space.type != 'VIEW_3D':
					continue
				
				# Apparently we can only change the `studio_light` of the current `shading_type`.
				prev_type = space.shading.type

				space.shading.type = 'MATERIAL'
				space.shading.studio_light = hdri_name

				space.shading.type = prev_type


def set_viewport_shading(shading_preferences: dict[str, Shading]):
	'''
	Iterates though `shading_preferences` and sets the `shading_type` and `studio_light` for any `3D_VIEW` spaces it finds.
	'''

	for key, val in shading_preferences.items():
		screen = bpy.data.screens.get(key)

		if screen is None:
			if addon.debug():
				print(f'ARMORED-Toolkit: Screen \'{key}\' not found. Skipping.')
			continue

		for area in screen.areas:
			for space in area.spaces:
				if space.type != 'VIEW_3D':
					continue
				
				space.shading.type = val.type

				if val.light is not None:
					space.shading.light = val.light

				if val.studio_light is not None:
					space.shading.studio_light = val.studio_light	


class ARMORED_OT_theme_install(bpy.types.Operator):
	'''Install my personal Blender Theme with it's matching Matcap and HDRI.

	armoredColony.com '''

	bl_idname = 'armored.theme_install'
	bl_label = 'ARMORED Theme Install'
	bl_options = {'REGISTER', 'INTERNAL'}

	theme_filename: bpy.props.StringProperty(name='Theme File Name', default='Armored_Colony.xml')
	
	def execute(self, context):
		# We used to install the theme from the addon 'resources' folder, which did not require enabling the 'themes' resource.
		# This meant the addon would remove the theme preset after restarting if the user never enabled the 'themes' resource manually.
		# The theme remained applied visually, but the preset would be gone from the themes preset list in the Blender preferences.
		# file_path = os.path.join(paths.AddonPaths.themes, self.theme_filename)    # The source, not the target.
		# bpy.ops.preferences.theme_install(filepath=file_path, overwrite=True)

		enable_required_resources(['matcaps', 'hdris', 'studio_lights', 'themes'])

		bpy.ops.script.execute_preset(
			filepath=os.path.join(paths.BlenderPaths.themes, self.theme_filename),	# Should now exist after enabling the resource.
			menu_idname='USERPREF_MT_interface_theme_presets'
		)

		set_favorite_hdri('ARC 2 Panels Tilted 4K.hdr')
		set_viewport_shading(SHADING_PREFERENCES)
		
		self.report({'INFO'}, f'ARMORED-Toolkit: LOADED Theme `{self.theme_filename}` with Matcap `ARC Lambert NVil.png` and HDRI `ARC 2 Panels Tilted 4K.hdr`.')
		
		return {'FINISHED'}


class ARMORED_OT_theme_uninstall(bpy.types.Operator):
	'''Restore Blender's default theme, matcap and HDRI.

	armoredColony.com '''

	bl_idname = 'armored.theme_uninstall'
	bl_label = 'ARMORED Theme Uninstall'
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		bpy.ops.preferences.reset_default_theme()
		set_viewport_shading(FACTORY_SHADING_PREFERENCES)
		set_favorite_hdri('forest.exr')

		self.report({'INFO'}, 'ARMORED-Toolkit: RESTORED default theme, matcap and HDRI.')

		return {'FINISHED'}
	


classes = (
	ARMORED_OT_theme_install,
	ARMORED_OT_theme_uninstall
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)