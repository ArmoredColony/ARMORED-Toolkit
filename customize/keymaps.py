import bpy
import math
import pathlib
import sys

from .. utils import(
	addon, 
	debug,
	keymap_utils,
	mod_utils,
)


wm = bpy.context.window_manager
kc = wm.keyconfigs.addon


keymap_groups = {}
special_keymaps = []


ABSTRACT_ARMORED_FOCUS_CATEGORY = '3D View'	# Must be an existing category for persistence in the USER keyconfig.
ABSTRACT_ARMORED_FOCUS_IDNAME   = 'armored.abstract_focus'


def create_abstract_armored_focus_kmi() -> None:
	'''
	Sets the abstract keymap item that appears in the addon preferences.
	It is a dummy kmi used to capture a user input (bpy.props has no kmi type).

	Note:
		This kmi is only referenced by the same properties it is created with.
	'''

	prefs = addon.prefs()
	category = ABSTRACT_ARMORED_FOCUS_CATEGORY
	km = kc.keymaps.get(category) or kc.keymaps.new(name=category)

	kmi = keymap_utils.create_kmi(
		km     = km, 
		idname = ABSTRACT_ARMORED_FOCUS_IDNAME, 
		type   = prefs.focus_kmi_type, 
		value  = prefs.focus_kmi_value, 
		ctrl   = prefs.focus_kmi_ctrl, 
		alt    = prefs.focus_kmi_alt, 
		shift  = prefs.focus_kmi_shift,
	)

	special_keymaps.append((km, kmi))


@bpy.app.handlers.persistent
def update_armored_focus_keymaps(*args):
	'''
	Updates all `armored_focus` operator keymaps to match 
	the related kmi properties in the addon preferences.
	'''
	
	if not addon.prefs().focus_selected:
		return
	
	debug.msg('ARMORED-Toolkit: Updating Armored Focus Keymaps.')

	prefs = addon.prefs()
	for _km, kmi in keymap_groups['focus_selected'].keymap_list:
		kmi.type  = prefs.focus_kmi_type
		kmi.value = prefs.focus_kmi_value
		kmi.ctrl  = prefs.focus_kmi_ctrl
		kmi.alt   = prefs.focus_kmi_alt
		kmi.shift = prefs.focus_kmi_shift


# @bpy.app.handlers.persistent
# def disable_conflicting_keymaps(*args):
# 	'''
# 	Disable keymaps that may conflict with addon keymaps.
# 	'''
	
# 	disable_select_through_conflicts()


# def disable_select_through_conflicts():
# 	'''
# 	Disables any keymaps that may conflict with the default keymap
# 	for the `armored_select_through` operator.
# 	'''
	
# 	kc = bpy.context.window_manager.keyconfigs.user
# 	km = kc.keymaps.get('Mesh')

# 	if km is None:
# 		debug.msg('ARMORED-Toolkit: keymap category [Mesh] not found.')
# 		return

# 	result = keymap_utils.disable_kmi(
# 		km=km,
# 		idname='wm.call_menu',
# 		type='RIGHTMOUSE',
# 		value='PRESS'
# 	)

# 	if result:
# 		print('Disabled Select Through Keymap Conflict')
# 	else:
# 		print('No Select Through Keymap Conflict Found')


def get_export_path_from_addon():
	'''
	Gets the custom `export_path` property, defined in the addon preferences.
	'''
	
	armored_toolkit = bpy.context.preferences.addons['ARMORED-Toolkit']
	props = armored_toolkit.preferences

	return getattr(props, 'export_path')


# Use underscores in the class names. Capitalization is irrelevant as long as the letters
# match the property names in the addon preferences

class MAYA_NAVIGATION(keymap_utils.KeymapGroup):
	def register(self):
		self.km = kc.keymaps.new('3D View', space_type='VIEW_3D')

		self.add('view3d.rotate', 'LEFTMOUSE',   'CLICK_DRAG',	alt=True)
		self.add('view3d.move',   'MIDDLEMOUSE', 'PRESS',	alt=True)
		self.add('view3d.zoom',   'RIGHTMOUSE',  'PRESS',	alt=True)

		self.status_message('ENABLED')


class LOOP_SELECTION(keymap_utils.KeymapGroup):
	def register(self):
		self.km = kc.keymaps.new(name='Mesh')

		# Loop Select
		self.add('mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK')
		self.prop('extend', False)
		self.prop('deselect', False)
		self.prop('toggle', False)

		# Loop Select ADD
		self.add('mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK', shift=True)
		self.prop('extend', True)
		self.prop('deselect', False)
		self.prop('toggle', True)

		# Loop Select REMOVE
		self.add('mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK', ctrl=True)
		self.prop('extend', False)
		self.prop('deselect', True)
		self.prop('toggle', False)

		self.status_message('ENABLED')


class focus_selected(keymap_utils.KeymapGroup):
	def register(self):
		'''
		Some keymaps work with the global self.km = kc.keymaps.new('Window') (space_type defaults to EMPTY)
		...but others get overriden by more specific category names. Not sure how space_type affects priority.
		'''

		prefs = addon.prefs()
		key   = prefs.focus_kmi_type
		ctrl  = prefs.focus_kmi_ctrl
		shift = prefs.focus_kmi_shift
		alt   = prefs.focus_kmi_alt

		# key   = 'F'
		# ctrl  = False
		# alt   = False
		# shift = False

		self.km = kc.keymaps.new('Outliner', space_type='OUTLINER')
		self.add('outliner.show_active', key, 'PRESS', ctrl, alt, shift)

		# self.km = kc.keymaps.new('3D View', space_type='VIEW_3D')
		# self.add('view3d.armored_focus', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('Object Mode')  # DEFAULT space_type is 'EMPTY'
		self.add('object.armored_focus', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('Mesh')
		self.add('mesh.armored_focus', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('Lattice')
		self.add('lattice.armored_focus', key, 'PRESS', ctrl, alt, shift)
		
		self.km = kc.keymaps.new('Curve')
		self.add('curve.armored_focus', key, 'PRESS', ctrl, alt, shift)

		# self.km = kc.keymaps.new('Sculpt')
		# self.add('view3d.view_selected', key, 'PRESS', ctrl, alt, shift)
		# self.add('view3d.armored_focus', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR')
		self.add('graph.view_selected', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('Image', space_type='IMAGE_EDITOR')
		self.add('image.armored_focus', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('Node Editor', space_type='NODE_EDITOR')
		self.add('node.armored_focus', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('File Browser Main', space_type='FILE_BROWSER')
		self.add('file.view_selected', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR')
		self.add('action.view_selected', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('NLA Editor', space_type='OUTLINER')
		self.add('nla.view_selected', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR')
		self.add('sequencer.view_selected', key, 'PRESS', ctrl, alt, shift)

		self.km = kc.keymaps.new('Outliner', space_type='OUTLINER')
		self.add('clip.view_selected', key, 'PRESS', ctrl, alt, shift)

		self.status_message('ENABLED')

	
class FAST_SUBDIVISION(keymap_utils.KeymapGroup):
	def register(self):

		self.km = kc.keymaps.new(name='Object Mode')
		self.add('object.armored_fast_subdivision', 'ZERO',  'PRESS', ctrl=True); self.prop('level', 0)
		self.add('object.armored_fast_subdivision', 'ONE',   'PRESS', ctrl=True); self.prop('level', 1)
		self.add('object.armored_fast_subdivision', 'TWO',   'PRESS', ctrl=True); self.prop('level', 2)
		self.add('object.armored_fast_subdivision', 'THREE', 'PRESS', ctrl=True); self.prop('level', 3)
		self.add('object.armored_fast_subdivision', 'FOUR',  'PRESS', ctrl=True); self.prop('level', 4)
		self.add('object.armored_fast_subdivision', 'FIVE',  'PRESS', ctrl=True); self.prop('level', 5)
		self.add('object.armored_fast_subdivision', 'SIX',   'PRESS', ctrl=True); self.prop('level', 6)
		self.add('object.armored_fast_subdivision', 'SEVEN', 'PRESS', ctrl=True); self.prop('level', 7)
		self.add('object.armored_fast_subdivision', 'EIGHT', 'PRESS', ctrl=True); self.prop('level', 8)
		self.add('object.armored_fast_subdivision', 'NINE',  'PRESS', ctrl=True); self.prop('level', 9)

		self.km = kc.keymaps.new(name='Mesh')
		self.add('mesh.armored_fast_subdivision',   'ZERO',  'PRESS', ctrl=True); self.prop('level', 0)
		self.add('mesh.armored_fast_subdivision',   'ONE',   'PRESS', ctrl=True); self.prop('level', 1)
		self.add('mesh.armored_fast_subdivision',   'TWO',   'PRESS', ctrl=True); self.prop('level', 2)
		self.add('mesh.armored_fast_subdivision',   'THREE', 'PRESS', ctrl=True); self.prop('level', 3)
		self.add('mesh.armored_fast_subdivision',   'FOUR',  'PRESS', ctrl=True); self.prop('level', 4)
		self.add('mesh.armored_fast_subdivision',   'FIVE',  'PRESS', ctrl=True); self.prop('level', 5)
		self.add('mesh.armored_fast_subdivision',   'SIX',   'PRESS', ctrl=True); self.prop('level', 6)
		self.add('mesh.armored_fast_subdivision',   'SEVEN', 'PRESS', ctrl=True); self.prop('level', 7)
		self.add('mesh.armored_fast_subdivision',   'EIGHT', 'PRESS', ctrl=True); self.prop('level', 8)
		self.add('mesh.armored_fast_subdivision',   'NINE',  'PRESS', ctrl=True); self.prop('level', 9)

		self.status_message('ENABLED')


class DESELECT_WITH_CTRL(keymap_utils.KeymapGroup):
	def register(self):
		self.km = kc.keymaps.new(name='Object Mode')
		self.add('armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

		self.km = kc.keymaps.new(name='Mesh')
		self.add('armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

		self.km = kc.keymaps.new('Lattice')
		self.add('armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

		self.km = kc.keymaps.new('Curve', space_type='EMPTY')
		self.add('armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

		self.status_message('ENABLED')


class TRANSFORM_WITH_GIZMOS(keymap_utils.KeymapGroup):
	def register(self):
		# self.km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
		self.km = kc.keymaps.new('3D View', space_type='VIEW_3D')
		self.add('view3d.armored_toggle_tool', 'G', 'PRESS'); self.prop('name', 'builtin.move')
		self.add('view3d.armored_toggle_tool', 'R', 'PRESS'); self.prop('name', 'builtin.rotate')
		self.add('view3d.armored_toggle_tool', 'S', 'PRESS'); self.prop('name', 'builtin.scale')

		self.km = kc.keymaps.new(name='Mesh')
		self.add('view3d.armored_toggle_tool', 'G', 'PRESS'); self.prop('name', 'builtin.move')
		self.add('view3d.armored_toggle_tool', 'R', 'PRESS'); self.prop('name', 'builtin.rotate')
		self.add('view3d.armored_toggle_tool', 'S', 'PRESS'); self.prop('name', 'builtin.scale')

		self.status_message('ENABLED')


class DELETE_WITHOUT_MENUS(keymap_utils.KeymapGroup):
	def register(self):
		self.km = kc.keymaps.new(name='Mesh')
		self.add('mesh.armored_smart_delete', 'X', 'PRESS')
		self.add('wm.call_menu', 'X', 'PRESS', alt=True); self.prop('name', 'VIEW3D_MT_edit_mesh_delete')

		self.status_message('ENABLED')


class ALLOW_GIZMO_CLICK(keymap_utils.KeymapGroup):
	def register(self):
		self.km = kc.keymaps.new('Generic Gizmo Maybe Drag', space_type='EMPTY')     # Makes Gizmos activate on click instead of drag.
		self.add('gizmogroup.gizmo_tweak', 'LEFTMOUSE', 'PRESS')

		self.status_message('ENABLED')


class TAB_HISTORY(keymap_utils.KeymapGroup):
	def register(self):
		self.km = kc.keymaps.new('Object Non-modal')
		self.add('armored.mode_toggle', 'TAB', 'PRESS')

		self.status_message('ENABLED')


class ZBRUSH_SCULPTING(keymap_utils.KeymapGroup):
	def register(self):
		self.km = kc.keymaps.new(name='Sculpt')

		self.add('sculpt.sample_color', 'C', 'PRESS')
		# self.add('paint.brush_colors_flip', 'X', 'PRESS')

		# self.add('view3d.localview', 'TAB', 'PRESS'); self.prop('frame_selected', False)

		# self.add('mesh.paint_mask_slice', 'E', 'PRESS', ctrl=True, shift=True); self.prop('fill_holes', False)

		# self.add('object.transfer_mode', 'Q', 'PRESS')
		# self.add('object.armored_switch_and_focus', 'Q', 'DOUBLE_CLICK')

		# self.add('sculpt.armored_focus', 'F', 'PRESS', alt=True)
		# self.add('view3d.view_selected', 'F', 'PRESS', alt=False)
		# self.add('wm.context_toggle',    'F', 'PRESS', shift=True); self.prop('data_path', 'space_data.overlay.show_wireframes')

		# self.add('transform.resize', 'S', 'PRESS', alt=True)

		# self.add('view3d.armored_silhouette', 'V', 'PRESS', alt=True)
		# self.add('view3d.armored_subdivide', 'D', 'PRESS', ctrl=True)
		# # self.add('sculpt.armored_remesh', 'R', 'PRESS', ctrl=True)

		# # self.add('sculpt.armored_scale_unmasked', 'S', 'PRESS', alt=True)
		# self.add('transform.translate', 'G', 'PRESS')

		# # Invert brush stroke (set to ALT instead of CTRL)
		# self.add('sculpt.brush_stroke', 'LEFTMOUSE', 'PRESS', alt=True); self.prop('mode', 'INVERT')

		# # BRUSHES

		# CLAY STRIPS
		self.add('brush.asset_activate', 'ONE', 'PRESS')
		self.prop('asset_library_type', 'ESSENTIALS')
		self.prop('relative_asset_identifier', 'brushes\\essentials_brushes-mesh_sculpt.blend\\Brush\\Clay Strips')

		# CLAY
		self.add('brush.asset_activate', 'ONE', 'PRESS', alt=True)
		self.prop('asset_library_type', 'ESSENTIALS')
		self.prop('relative_asset_identifier', 'brushes\\essentials_brushes-mesh_sculpt.blend\\Brush\\Clay')

		# DRAW SHARP
		self.add('brush.asset_activate', 'TWO', 'PRESS')
		self.prop('asset_library_type', 'ESSENTIALS')
		self.prop('relative_asset_identifier', 'brushes\\essentials_brushes-mesh_sculpt.blend\\Brush\\Draw Sharp')

		# DRAW
		self.add('brush.asset_activate', 'TWO', 'PRESS', alt=True)
		self.prop('asset_library_type', 'ESSENTIALS')
		self.prop('relative_asset_identifier', 'brushes\\essentials_brushes-mesh_sculpt.blend\\Brush\\Draw')

		# SCRAPE/FILL
		self.add('brush.asset_activate', 'THREE', 'PRESS')
		self.prop('asset_library_type', 'ESSENTIALS')
		self.prop('relative_asset_identifier', 'brushes\\essentials_brushes-mesh_sculpt.blend\\Brush\\Scrape/Fill')

		# HPOLISH
		self.add('brush.asset_activate', 'THREE', 'PRESS', alt=True)
		self.prop('asset_library_type', 'CUSTOM')
		self.prop('asset_library_identifier', 'User Library')
		self.prop('relative_asset_identifier', 'Saved\\Brushes\\hPolish.asset.blend\\Brush\\hPolish')

		# GRAB
		self.add('brush.asset_activate', 'FOUR', 'PRESS')
		self.prop('asset_library_type', 'ESSENTIALS')
		self.prop('relative_asset_identifier', 'brushes\\essentials_brushes-mesh_sculpt.blend\\Brush\\Grab')

		# SNAKE HOOK
		self.add('brush.asset_activate', 'FOUR', 'PRESS', alt=True)
		self.prop('asset_library_type', 'ESSENTIALS')
		self.prop('relative_asset_identifier', 'brushes\\essentials_brushes-mesh_sculpt.blend\\Brush\\Snake Hook')

		# # BRUSH SIZE
		self.add('wm.radial_control',  'S', 'PRESS')
		self.prop('data_path_primary',   'tool_settings.sculpt.brush.size.size')
		self.prop('data_path_secondary', 'tool_settings.unified_paint_settings.size')
		self.prop('use_secondary',       'tool_settings.unified_paint_settings.use_unified_size')
		self.prop('rotation_path',       'tool_settings.sculpt.brush.texture_slot.angle')
		self.prop('color_path',          'tool_settings.sculpt.brush.cursor_color_add')
		self.prop('fill_color_path', '')
		self.prop('fill_color_override_path', '')
		self.prop('fill_color_override_test_path', '')
		self.prop('zoom_path', '')
		self.prop('image_id', 'tool_settings.sculpt.brush')
		self.prop('secondary_tex', False)
		self.prop('release_confirm', True)  # Only property that was changed.

		# BRUSH STRENGTH
		self.add('wm.radial_control',  'S', 'PRESS', shift=True)
		self.prop('data_path_primary',   'tool_settings.sculpt.brush.size.strength')
		self.prop('data_path_secondary', 'tool_settings.unified_paint_settings.strength')
		self.prop('use_secondary',       'tool_settings.unified_paint_settings.use_unified_strength')
		self.prop('rotation_path',       'tool_settings.sculpt.brush.texture_slot.angle')
		self.prop('color_path',          'tool_settings.sculpt.brush.cursor_color_add')
		self.prop('fill_color_path', '')
		self.prop('fill_color_override_path', '')
		self.prop('fill_color_override_test_path', '')
		self.prop('zoom_path', '')
		self.prop('image_id', 'tool_settings.sculpt.brush')
		self.prop('secondary_tex', False)
		self.prop('release_confirm', True)  # Only property that was changed.

		self.status_message('ENABLED')


class OPERATOR_SHORTCUTS(keymap_utils.KeymapGroup):
	def register(self):
		# ========================================================================================================
		# WINDOW

		self.km = kc.keymaps.new('Window', space_type='EMPTY')

		self.add('screen.userpref_show',		'COMMA',	'PRESS', ctrl=True)
		self.add('wm.armored_open_most_recent',		'R',		'PRESS', alt=True, shift=True)
		self.add('script.reload',			'F5',		'PRESS')  # best to create this keymap manually in blender's keymap editor, otherwise you wont be able to use it if something crashes.

		# Generic (doesn't work unless separate from 3D View)
		self.km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
		self.add('screen.redo_last',            'T',     'PRESS')


		# ========================================================================================================
		# VIEW 3D

		self.km = kc.keymaps.new('3D View', space_type='VIEW_3D')

		self.add('view3d.view_all',				'HOME',			'PRESS', shift=True)
		self.add('view3d.zoom_border',				'BUTTON4MOUSE',		'PRESS')
		self.add('view3d.armored_paint_select',			'Q',			'PRESS') # Tapping this will activate select_box instead.
		self.add('wm.toolbar_fallback_pie',			'Q',			'DOUBLE_CLICK')
		self.add('wm.context_toggle',				'W',			'PRESS', shift=True)
		self.prop('data_path', 'space_data.overlay.show_wireframes')

		self.add('view3d.armored_toggle_overlays',		'W',			'PRESS', alt=True)
		self.prop('toggle_gizmos', False)
		
		self.add('view3d.armored_toggle_tool',			'W',			'PRESS')
		self.prop('name', 'builtin.move')

		self.add('view3d.armored_autosmooth',			'A',			'PRESS', ctrl=True, shift=True)
		self.add('view3d.armored_toggle_cavity',		'C',			'PRESS', alt=True)
		self.add('view3d.armored_cycle_cavity_type',		'C',			'PRESS', alt=True, shift=True)
		self.add('view3d.armored_subdivide',			'D',			'PRESS', ctrl=True)
		self.add('view3d.armored_increase_subd_mod_level',	'PAGE_UP',		'PRESS')
		self.add('view3d.armored_decrease_subd_mod_level',	'PAGE_DOWN',		'PRESS')
		self.add('view3d.localview',				'SLASH',		'PRESS')
		self.prop('frame_selected', False)

		self.add('view3d.localview',				'NUMPAD_SLASH',  	'PRESS')
		self.prop('frame_selected', False)


		# ========================================================================================================
		# NODE EDITOR

		self.km = kc.keymaps.new('Node Editor', space_type='NODE_EDITOR')

		self.add('view2d.zoom_border',				'BUTTON4MOUSE', 'PRESS')

		

		# ========================================================================================================
		# POSE

		self.km = kc.keymaps.new(name='Pose')

		self.add('view3d.armored_toggle_overlays',	'W', 'PRESS', alt=True); self.prop('toggle_gizmos', False)



		# ========================================================================================================
		# OBJECT

		self.km = kc.keymaps.new(name='Object Mode')

		self.add('object.armored_clear_location',	'G', 'PRESS', alt=True)
		self.add('object.armored_hide',             	'H', 'PRESS')
		self.add('object.delete',                   	'X', 'PRESS')
		self.prop('confirm', False)

		self.add('mesh.armored_classic_mirror',     	'X', 'PRESS', ctrl=True, alt=True)
		self.add('wm.obj_export',                   	'E', 'PRESS', ctrl=True)
		self.prop('filepath', get_export_path_from_addon())
		self.prop('export_selected_objects',    True)
		self.prop('export_materials',           False)
		self.prop('export_triangulated_mesh',   True)

		self.add('object.move_to_collection',       	'N', 'PRESS', shift=True)
		self.prop('collection_index', 0)
		self.prop('is_new', True)


		# ========================================================================================================
		# MESH

		self.km = kc.keymaps.new(name='Mesh')

		self.add('mesh.armored_select_through',		'RIGHTMOUSE',		'CLICK_DRAG', ctrl=True)
		self.prop('select_mode', 'ADD')
		
		self.add('mesh.armored_custom_orientation',	'D',			'PRESS')
		self.add('wm.context_toggle',			'W',			'PRESS', shift=True)
		self.prop('data_path', 'space_data.overlay.show_wireframes')

		self.add('mesh.armored_classic_mirror',		'X',			'PRESS', ctrl=True, alt=True)
		self.add('mesh.loop_multi_select',		'L',			'PRESS', alt=True)
		self.prop('ring', False)

		self.add('mesh.armored_vitaly_poke',		'V',			'PRESS', alt=True)
		self.add('mesh.loopcut_slide',			'C',			'PRESS')
		self.prop('TRANSFORM_OT_edge_slide.release_confirm', True)

		self.add('mesh.faces_select_linked_flat',	'F',			'PRESS', shift=True)
		# self.add('mesh.edge_face_add',			'F',			'PRESS', alt=True)
		# self.add('mesh.armored_f2',			'F',			'PRESS', alt=True)
		self.add('mesh.armored_flatten',		'F',			'PRESS', ctrl=True, alt=True)
		self.add('mesh.armored_extrude',		'E',			'PRESS', alt=True)
		self.add('mesh.armored_extract',		'E',			'PRESS', ctrl=True, shift=True)
		self.add('mesh.armored_duplicate',		'D',			'PRESS', ctrl=True, shift=True)
		self.add('transform.shrink_fatten',		'S',			'PRESS', alt=True)
		self.prop('use_even_offset', True)
		
		self.add('mesh.armored_select_adjacent',	'WHEELUPMOUSE',		'PRESS', ctrl=True, shift=True)
		self.add('mesh.armored_fast_bevel',		'B',			'PRESS')
		self.add('mesh.bridge_edge_loops',		'B',			'PRESS', shift=True)
		self.add('mesh.loop_multi_select',		'R',			'PRESS', alt=True)
		self.prop('ring', True)

		self.add('mesh.armored_connect',		'C',			'PRESS', shift=True)
		self.add('mesh.armored_align_verts',		'V',			'PRESS', shift=True)
		# self.add('mesh.looptools_gstretch',		'V',			'PRESS', shift=True)
		self.add('mesh.armored_smart_crease',		'E',			'PRESS', shift=True)
		self.add('mesh.armored_mark_edges',		'BUTTON5MOUSE',		'PRESS', shift=True)
		self.prop('action', 'MARK')
		self.prop('face_limit_method', 'BORDER')
		
		self.add('mesh.armored_mark_edges',		'BUTTON5MOUSE',		'PRESS', ctrl=True, shift=True)
		self.prop('action', 'MARK')
		self.prop('face_limit_method', 'ANGLE')

		self.add('mesh.armored_mark_edges',		'BUTTON4MOUSE',		'PRESS', shift=True)
		self.prop('action', 'CLEAR')

		self.add('mesh.armored_mark_edges',		'BUTTON4MOUSE',		'PRESS', ctrl=True, shift=True)
		self.prop('action', 'CLEAR')

		self.add('mesh.select_linked_pick',		'LEFTMOUSE',		'DOUBLE_CLICK', alt=True)
		self.prop('deselect', False)
		
		self.add('mesh.select_more',			'WHEELUPMOUSE',		'PRESS', ctrl=True)
		self.add('mesh.select_less',			'WHEELDOWNMOUSE',	'PRESS', ctrl=True)
		self.add('mesh.region_to_loop',			'BUTTON5MOUSE',		'PRESS')
		self.add('mesh.armored_select_hard_edges',	'FIVE',			'PRESS', alt=True)
		self.add('mesh.armored_subd_view_in_edit',	'ONE',			'PRESS', alt=True)
		self.prop('mode', 'OFF')

		self.add('mesh.armored_subd_view_in_edit',	'TWO',			'PRESS', alt=True)
		self.prop('mode', 'HYBRID')

		self.add('mesh.armored_subd_view_in_edit',	'THREE',		'PRESS', alt=True)
		self.prop('mode', 'FULL')


		# ========================================================================================================
		# CURVE

		self.km = kc.keymaps.new('Curve', space_type='EMPTY')

		self.add('curve.shortest_path_pick',		'LEFTMOUSE', 'PRESS', ctrl=True, shift=True)
		# self.add('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)

		self.status_message('ENABLED')


def register():
	# We register this separately so the user defined value is persistent and uncoupled from the `focus keymap override`.
	create_abstract_armored_focus_kmi()

	# We do this here to delay the instancing until `special_keymaps` is populated.
	for cls in classes:
		keymap_groups[cls.__name__.lower()] = cls()

	for cls_name, cls_instance in keymap_groups.items():
		if getattr(addon.prefs(), cls_name.lower()):
			cls_instance.register()


def unregister():
	# Classes that never registered keymaps will return early from their `unregister`` method.
	for cls_instance in keymap_groups.values():
		cls_instance.unregister()

	for km, kmi in special_keymaps:
		km.keymap_items.remove(kmi)


# KEEP THIS AT THE END OF THE FILE
classes = mod_utils.get_module_classes(sys.modules[__name__])

