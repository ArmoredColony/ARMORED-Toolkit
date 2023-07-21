import bpy

import sys
import pathlib
# import os

from .. utils import (
    addon,
    config,
    descriptions,
    icons,
    paths,
)

from .. customize import (
    keymaps,
    resources,  # DO NOT DELETE (USED BY EVAL)
)


preview_collections = {}
default_path = str(pathlib.Path.home() / 'Desktop')

# This only seems to work out here so... whatever.
def update(self, context, prop='', category=''):
	state = getattr(addon.prefs(), prop)

	if category == 'keymaps':
		keymap_group = keymaps.keymap_groups[prop]
		if state:   keymap_group.register()
		else:       keymap_group.unregister()

	elif category in {'matcaps', 'hdris', 'studio_lights', 'themes'}:
		if state:   eval(f'resources.{category.upper()}.load()')
		else:       eval(f'resources.{category.upper()}.unload()')

	elif category == 'operator':
		from .. operators import ARMORED_mode_toggle
		ARMORED_mode_toggle.register()
		ARMORED_mode_toggle.unregister()

	# config.set_config(prop, category, state)


class ARMORED_PT_Toolkit_Preferences(bpy.types.AddonPreferences):
	bl_idname = addon.name()

	def closure(prop, category):
		return lambda a, b: update(a, b, prop, category)   # a, b = self, context
	
	# KEYMAP GROUPS >>

	maya_navigation: bpy.props.BoolProperty(name='Maya Navigation', default=False,
		description='Maya style navigation (ALT + Mouse Buttons)', 
		update=closure(prop='maya_navigation', category='keymaps'))

	loop_selection: bpy.props.BoolProperty(name='Double Click to Select Loops', default=False,
		description='Double Click to select component loops', 
		update=closure(prop='loop_selection', category='keymaps'),)
		
	focus_selected_with_f: bpy.props.BoolProperty(name='Focus Selected with F', default=False,
		description='Frame your selection with the F key (NUMPAD_PERIOD can still be used). This option does NOT affect Sculpt or similar modes where F is used to resize the brush. See the dedicated ZBrush Sculpting override for this functionality', 
		update=closure(prop='focus_selected_with_f', category='keymaps'),)

	fast_subdivision: bpy.props.BoolProperty(name='Fast Subdivision', default=False,
		description='Lowers the \'quality\' of the \'use_limit_surface\' property in Subsurf Modifiers applied with Ctrl + 1...9', 
		update=closure(prop='fast_subdivision', category='keymaps'),)

	deselect_with_ctrl: bpy.props.BoolProperty(name='Deselect with CTRL', default=False,
		description='CTRL Click now deselects stuff (both in Edit and Object mode)', 
		update=closure(prop='deselect_with_ctrl', category='keymaps'),)

	transform_with_gizmos: bpy.props.BoolProperty(name='Transform with Gizmos', default=False,
		description='Use the Gizmo version of the Move, Scale and Rotate Tools', 
		update=closure(prop='transform_with_gizmos', category='keymaps'),)

	allow_gizmo_click: bpy.props.BoolProperty(name='Allow Gizmo Click', default=False,
		description='Activate Gizmos on Click instead of waiting for a Drag event', 
		update=closure(prop='allow_gizmo_click', category='keymaps'),)

	zbrush_sculpting: bpy.props.BoolProperty(name='ZBrush Sculpting', default=False,
		description='Makes Sculpt AND Vertex Paint modes a bit more familiar to ZBrush users (does NOT include ZBrush navigation).\n\n' + 'See PDF above for the full list of keymaps', 
		update=closure(prop='zbrush_sculpting', category='keymaps'),)

	operator_shortcuts: bpy.props.BoolProperty(name='Operator Keymaps', default=False, 
		description='Enables predefined keymaps for some operators/scripts in the Armored Toolkit.\n\n' + 'See PDF above for the full list of keymaps', 
		update=closure(prop='operator_shortcuts', category='keymaps'),)

	tab_history: bpy.props.BoolProperty(name='TAB History', default=False,
		description='Use custom TAB functionality.\n\n' + descriptions.smart_tab_functions, 
		update=closure(prop='tab_history', category='keymaps'),)

	tab_undo_mode: bpy.props.EnumProperty(name='Undo behaviour for each TAB press', default='GROUPED',
		description='TAB Undo Behaviour ', 
		update=closure(prop='tab_undo_mode', category='operator'),
		items=[ ('NORMAL',  'Blender Default',            'Create one undo step for each TAB press'), 
			('GROUPED', 'Grouped Undo (recommended)', 'Combine repeated TAB presses into a single Undo step'),
			('SKIP',    'Skip Undo',                  'Pressing TAB does NOT generate undo history'), ])

	delete_without_menus: bpy.props.BoolProperty(name='Delete without Menus', default=False,
		description='Delete components based on your selection mode (vertex, edge, face) without aditional menus.\nOriginal Menu moved to ALT+X', 
		update=closure(prop='delete_without_menus', category='keymaps'),)

	wireframe_selected: bpy.props.BoolProperty(name='Wireframe Selected', default=False,
		description='Display the wireframe of any objects you select and viceversa', 
		update=closure(prop='wireframe_selected', category='keymaps'),)


	# STUDIO LIGHTS >>

	matcaps: bpy.props.BoolProperty(name='MATCAPS', default=False,
		description='Some of my favorite matcaps.\n' + descriptions.matcap_files, 
		update=closure(prop='matcaps', category='matcaps'),)

	hdris: bpy.props.BoolProperty(name='HDRIS', default=False,
		description='Just some barely useful HDRIS.\n' + descriptions.hdri_files,
		update=closure(prop='hdris', category='hdris'),)

	studio_lights: bpy.props.BoolProperty(name='Studio Lights', default=False,
		description='Just some barely useful Studio Lights.\n' + descriptions.studio_light_files,
		update=closure(prop='studio_lights', category='studio_lights'),)


	# THEMES >>

	themes: bpy.props.BoolProperty(name='Themes', default=False,
		description='Mostly personal themes of mine.\n' + descriptions.theme_files, 
		update=closure(prop='themes', category='themes'),)
	

	# EXPORT PATHS >>

	export_path : bpy.props.StringProperty(
		name='Export Path', default=default_path, subtype='DIR_PATH')
	
	render_path : bpy.props.StringProperty(
		name='Render Path', default=default_path, subtype='DIR_PATH')


	# DEBUGGING >>

	debug: bpy.props.BoolProperty(name='Debug', default=False,
		description='Prints developer oriented information in the console window. Not really meant for end users.')


	def draw(self, context):
		layout = self.layout
		layout.use_property_split = False

		web_icons = preview_collections['web_icons']

		col = layout.column(align=True)
		row = col.row()
		row.operator('wm.url_open', text='GitHub', icon_value=web_icons['github32'].icon_id).url = 'https://github.com/ArmoredColony/ARMORED-Toolkit'
		row.operator('wm.url_open', text='Youtube', icon_value=web_icons['youtube32'].icon_id).url = 'https://www.youtube.com/armoredColony'
		row.operator('wm.url_open', text='Blender Market', icon_value=web_icons['blender_market32'].icon_id).url = 'https://blendermarket.com/creators/armoredcolony'
		row.operator('wm.url_open', text='Artstation', icon_value=web_icons['artstation32'].icon_id).url = 'https://armoredColony.com'
		layout.separator()

		def prop_line(prop, icon, url='www.youtube.com/armoredcolony', text=''):
			row = box.column(align=True).row()

			row.label(text=text or prop.replace('_', ' ').title())
			row.separator()
			row.prop(self, prop, text='On' if getattr(self, prop) else 'Off', toggle=True);
			#     row.operator('wm.url_open', icon=icon, text='').url = url

		# box = layout.box()
		# col = box.column(align=True)
		# col.label(text='This addon automatically enables developer extras', icon='ERROR')

		split = layout.split(factor=0.6)
		col1 = split.column(align=True)
		col2 = split.column(align=True)

		box = col1.box()
		box.label(text='Keymap Overrides:')
		box.operator('armored.open_folder', text='PDF Keymap List', icon='TEXT').path = paths.AddonPaths.docs_keymaps
		prop_line(prop='maya_navigation',       icon='FILE_MOVIE', url='www.youtube.com')
		prop_line(prop='loop_selection',        icon='FILE_MOVIE', url='www.youtube.com')
		prop_line(prop='focus_selected_with_f', icon='FILE_MOVIE', url='www.youtube.com')
		prop_line(prop='fast_subdivision',      icon='FILE_MOVIE', url='www.youtube.com')
		prop_line(prop='delete_without_menus',  icon='FILE_MOVIE', url='www.youtube.com')
		prop_line(prop='deselect_with_ctrl',    icon='FILE_MOVIE', url='www.youtube.com')
		prop_line(prop='transform_with_gizmos', icon='FILE_MOVIE', url='www.youtube.com')
		prop_line(prop='allow_gizmo_click',     icon='FILE_MOVIE', url='www.youtube.com')
		prop_line(prop='zbrush_sculpting',      icon='FILE_MOVIE', url='www.youtube.com')
		prop_line(prop='operator_shortcuts',    icon='FILE_MOVIE', url='www.youtube.com')

		col1.separator()

		box = col1.box()
		box.label(text='Extra Resources:')
		prop_line(prop='matcaps',       icon='MATERIAL', url='www.youtube.com')
		prop_line(prop='hdris',         icon='MATERIAL', url='www.youtube.com', text='HDRIS')
		prop_line(prop='studio_lights', icon='MATERIAL', url='www.youtube.com')
		prop_line(prop='themes',        icon='MATERIAL', url='www.youtube.com')

		col1.separator()

		box = col1.box()
		box.label(text='TAB Override:')
		prop_line(prop='tab_history', icon='FILE_MOVIE', url='www.youtube.com')
		if self.tab_history:
			box.prop(self, 'tab_undo_mode', text='', expand=False)
		col1.separator()

		box = col1.box()
		box.label(text='EXPERIMENTAL', icon='ERROR')
		prop_line(prop='wireframe_selected', icon='MATERIAL', url='www.youtube.com')
		col1.separator()

		box = col2.box()
		box.label(text='Custom Preferences:')
		layout.use_property_split = True
		box.operator('armored.load_preferences', text='Load Preferences')
		box.operator('armored.unload_preferences', text='Unload Preferences')
		# prop_line(prop='system_preferences', icon='TOPBAR', url='www.youtube.com')
		layout.use_property_split = False
		col2.separator()

		box = col2.box()
		box.label(text='Custom Theme:')
		box.operator('armored.theme_install', text='Load Theme')
		box.operator('armored.theme_uninstall', text='Unload Theme')

		# box.operator('preferences.reset_default_theme', text='Reset to Default Theme')
		col2.separator()

		col2.separator()
		box = col2.box()
		box.label(text='Useful Directories:')
		box.operator('armored.open_folder', text='Scripts Folder', icon='ERROR')      .path = paths.AddonPaths.operators
		box.operator('armored.open_folder', text='Keymaps File',   icon='FILE_SCRIPT').path = paths.AddonPaths.keymaps
		box.operator('armored.open_folder', text='Startup Folder', icon='FILE_FOLDER').path = paths.BlenderPaths.startup
		box.operator('armored.open_folder', text='Matcaps Folder', icon='MATERIAL')   .path = paths.BlenderPaths.matcaps
		box.operator('armored.open_folder', text='Themes Folder',  icon='TOPBAR')     .path = paths.BlenderPaths.themes


		# FILE PATHS >>

		col2.separator()
		box = col2.box()
		box.label(text='File Paths:')
		box.prop(self, 'export_path', text='Export Path')
		box.prop(self, 'render_path', text='Render Path')


		# DEVELOPER TOOLS >>

		col2.separator()
		box = col2.box()
		box.label(text='Developer Tools:')
		box.prop(self, 'debug', toggle=True)

		layout.label(text=f'Python {sys.version}')


class FilePathsPanel:

	bl_space_type = 'PREFERENCES'
	bl_region_type = 'WINDOW'
	bl_context = 'file_paths'


class ARMORED_PT_file_paths(FilePathsPanel, bpy.types.Panel):
    
	bl_label = 'Armored Toolkit'

	def draw(self, context):
		wm = context.window_manager.armored_export

		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		col = self.layout.column()
		col.label(text='Must be set per File!')
		col.prop(wm, 'export_path', text='Fast Export')


classes = (
	ARMORED_PT_Toolkit_Preferences,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	icons.load_icons(preview_collections)
	# config.load_config()


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	icons.unload_icons(preview_collections)
