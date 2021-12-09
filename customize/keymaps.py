import bpy

import sys

from .. utils import(
    addon, 
    keymap_utils,
    mod_utils,
)


# Use underscores in the class names. Capitalization is irrelevant as long as the letters
# match the property names in the addon preferences

wm = bpy.context.window_manager
kc = wm.keyconfigs.addon

class MAYA_NAVIGATION(keymap_utils.KeymapGroup):
    def register(self):
        self.km = kc.keymaps.new('3D View', space_type='VIEW_3D')

        self.add('view3d.rotate', 'LEFTMOUSE',   'CLICK_DRAG', alt=True)
        self.add('view3d.move',   'MIDDLEMOUSE', 'PRESS', alt=True)
        self.add('view3d.zoom',   'RIGHTMOUSE',  'PRESS', alt=True)

        self.enabled_message()


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

        self.enabled_message()


class FOCUS_SELECTED_WITH_F(keymap_utils.KeymapGroup):
    def register(self):
        '''
        Some keymaps work with the global self.km = kc.keymaps.new('Window') (space_type defaults to EMPTY)
        ...but others get overriden by more specific category names. Not sure how space_type affects priority.
        Individual KMs is ugly but it guarantees priority
        '''

        self.km = kc.keymaps.new('Outliner', space_type='OUTLINER')
        self.add('outliner.show_active',  'F', 'PRESS')

        # self.km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        # self.add('view3d.view_selected',    'F', 'PRESS')

        self.km = kc.keymaps.new('Object Mode')  # DEFAULT space_type is 'EMPTY'
        # self.add('view3d.view_selected',    'F', 'PRESS')
        self.add('mesh.armored_focus', 'F', 'PRESS')

        self.km = kc.keymaps.new('Mesh')
        # self.add('view3d.view_selected',    'F', 'PRESS')
        self.add('mesh.armored_focus', 'F', 'PRESS')
        
        self.km = kc.keymaps.new('Curve')
        self.add('view3d.view_selected',    'F', 'PRESS')

        self.km = kc.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR')
        self.add('graph.view_selected',     'F', 'PRESS')

        self.km = kc.keymaps.new('Image', space_type='IMAGE_EDITOR')
        self.add('image.view_selected',     'F', 'PRESS')

        self.km = kc.keymaps.new('Node Editor', space_type='NODE_EDITOR')
        self.add('node.view_selected',      'F', 'PRESS')

        self.km = kc.keymaps.new('File Browser Main', space_type='FILE_BROWSER')
        self.add('file.view_selected',      'F', 'PRESS')

        self.km = kc.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR')
        self.add('action.view_selected',    'F', 'PRESS')

        self.km = kc.keymaps.new('NLA Editor', space_type='OUTLINER')
        self.add('nla.view_selected',       'F', 'PRESS')

        self.km = kc.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR')
        self.add('sequencer.view_selected', 'F', 'PRESS')

        self.km = kc.keymaps.new('Outliner', space_type='OUTLINER')
        self.add('clip.view_selected',      'F', 'PRESS')

        self.enabled_message()

    
class DESELECT_WITH_CTRL(keymap_utils.KeymapGroup):
    def register(self):
        self.km = kc.keymaps.new(name='Object Mode')
        self.add('armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        self.km = kc.keymaps.new(name='Mesh')
        self.add('armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        self.km = kc.keymaps.new('Curve', space_type='EMPTY')
        self.add('armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        self.enabled_message()


class TRANSFORM_WITH_GIZMOS(keymap_utils.KeymapGroup):
    def register(self):
        self.km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        # self.add('view3d.armored_toggle_tool', 'G', 'PRESS'); self.prop('name', 'builtin.move')
        self.add('view3d.armored_toggle_tool', 'R', 'PRESS'); self.prop('name', 'builtin.rotate')
        self.add('view3d.armored_toggle_tool', 'S', 'PRESS'); self.prop('name', 'builtin.scale')

        self.enabled_message()


class ALLOW_GIZMO_CLICK(keymap_utils.KeymapGroup):
    def register(self):
        self.km = kc.keymaps.new('Generic Gizmo Maybe Drag', space_type='EMPTY')     # Makes Gizmos activate on click instead of drag.
        self.add('gizmogroup.gizmo_tweak', 'LEFTMOUSE', 'PRESS')

        self.enabled_message()


class TAB_HISTORY(keymap_utils.KeymapGroup):
    def register(self):
        self.km = kc.keymaps.new('Object Non-modal')
        self.add('armored.mode_toggle', 'TAB', 'PRESS')

        self.enabled_message()


class SCULPTING_SETUP(keymap_utils.KeymapGroup):
    def register(self):
        self.km = kc.keymaps.new(name='Sculpt')

        self.add('object.transfer_mode', 'D', 'PRESS')
        self.add('view3d.view_center_pick', 'F', 'PRESS', alt=True)
        self.add('view3d.armored_subdivide', 'D', 'PRESS', ctrl=True)

        # Invert brush stroke (set to ALT instead of CTRL)
        self.add('sculpt.brush_stroke', 'LEFTMOUSE', 'PRESS', alt=True); self.prop('mode', 'INVERT')

        # BRUSHES
        self.add('wm.tool_set_by_id', 'ONE',   'PRESS'          ); self.prop('name', 'builtin_brush.Clay Strips')
        self.add('wm.tool_set_by_id', 'ONE',   'PRESS', alt=True); self.prop('name', 'builtin_brush.Clay')

        self.add('wm.tool_set_by_id', 'TWO',   'PRESS'          ); self.prop('name', 'builtin_brush.Draw Sharp')
        self.add('wm.tool_set_by_id', 'TWO',   'PRESS', alt=True); self.prop('name', 'builtin_brush.Draw')

        self.add('wm.tool_set_by_id', 'THREE', 'PRESS'          ); self.prop('name', 'builtin_brush.Scrape')
        self.add('wm.tool_set_by_id', 'THREE', 'PRESS', alt=True); self.prop('name', 'builtin_brush.Flatten')

        self.add('wm.tool_set_by_id', 'FOUR',  'PRESS'          ); self.prop('name', 'builtin_brush.Grab')
        self.add('wm.tool_set_by_id', 'FOUR',  'PRESS', alt=True); self.prop('name', 'builtin_brush.Snake Hook')

        self.add('wm.tool_set_by_id', 'FIVE',  'PRESS'          ); self.prop('name', 'builtin_brush.Crease')
        self.add('wm.tool_set_by_id', 'FIVE',  'PRESS', alt=True); self.prop('name', 'builtin_brush.Inflate')

        self.add('wm.context_toggle',  'W', 'PRESS', shift=True); self.prop('data_path', 'space_data.overlay.show_wireframes')

        # BRUSH SIZE
        self.add('wm.radial_control',  'F', 'PRESS');
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
        self.prop('release_confirm', True)  # Only setting that was changed.

        # BRUSH STRENGTH
        self.add('wm.radial_control',  'F', 'PRESS', shift=True);
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
        self.prop('release_confirm', True)  # Only setting that was changed.

        self.enabled_message()


class OPERATOR_SHORTCUTS(keymap_utils.KeymapGroup):
    def register(self):

        def Global_Keys():
            pass
            # self.add('screen.userpref_show', 'COMMA', 'PRESS', ctrl=True)

        self.km = kc.keymaps.new('Window', space_type='EMPTY')
        self.add('screen.userpref_show', 'COMMA', 'PRESS', ctrl=True)
        # self.add('script.reload', 'F5', 'PRESS')  # best to create this keymap manually in blender's keymap editor, otherwise you wont be able to use it if something crashes.


        # Generic (doesn't work unless separate from 3D View)
        self.km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        self.add('screen.redo_last', 'T', 'PRESS')


        self.km = kc.keymaps.new('3D View', space_type='VIEW_3D')
        Global_Keys()

        self.add('view3d.zoom_border', 'F',            'PRESS', ctrl=True, shift=True)
        self.add('view3d.zoom_border', 'BUTTON4MOUSE', 'PRESS')

        self.add('view3d.armored_paint_select', 'Q', 'PRESS') # Tapping this will activate select_box instead.
        self.add('wm.call_menu_pie',            'Q', 'DOUBLE_CLICK'); self.prop('name', 'ARMORED_MT_PIE_select')

        self.add('wm.context_toggle',  'W', 'PRESS', shift=True); self.prop('data_path', 'space_data.overlay.show_wireframes')
        self.add('wm.context_toggle',  'W', 'PRESS', alt=True  ); self.prop('data_path', 'space_data.overlay.show_overlays')

        self.add('view3d.armored_toggle_tool', 'W', 'PRESS'); self.prop('name', 'builtin.move')
        # self.add('view3d.armored_toggle_tool', 'W', 'PRESS'); self.prop('name', 'tool.gizmo_pro')

        self.add('view3d.armored_autosmooth',        'A', 'PRESS', ctrl=True, shift=True)
        self.add('view3d.armored_open_most_recent',  'R', 'PRESS', alt=True,  shift=True)
        self.add('object.armored_rest_on_ground',    'R', 'PRESS', ctrl=True)

        self.add('view3d.armored_toggle_cavity',     'C', 'PRESS', alt=True)
        self.add('view3d.armored_cycle_cavity_type', 'C', 'PRESS', alt=True, shift=True)
        self.add('view3d.armored_smart_loopcut',     'C', 'PRESS')
        self.add('view3d.armored_subdivide',         'D', 'PRESS', ctrl=True)

        self.add('view3d.armored_single_subdivision_level', 'PAGE_UP',   'PRESS');  self.prop('action', 'INCREASE')
        self.add('view3d.armored_single_subdivision_level', 'PAGE_DOWN', 'PRESS');  self.prop('action', 'DECREASE')
        

        self.km = kc.keymaps.new(name='Object Mode')
        Global_Keys()

        self.add('object.delete', 'X', 'PRESS'); self.prop('confirm', False)
        
        self.add('object.armored_export_fbx', 'E', 'PRESS', ctrl=True)

        self.add('object.move_to_collection', 'N', 'PRESS', shift=True)
        self.prop('collection_index', 0)
        self.prop('is_new', True)


        self.km = kc.keymaps.new(name='Mesh')
        Global_Keys()

        self.add('mesh.faces_select_linked_flat', 'F', 'PRESS', shift=True)
        self.add('mesh.edge_face_add',            'F', 'PRESS', alt=True)
        self.add('mesh.f2',                       'F', 'PRESS', alt=True) # Same keymap as above, but seems to take prio if f2 is installed and viceversa.

        self.add('mesh.armored_custom_orientation', 'D', 'PRESS')

        self.add('mesh.armored_extrude', 'E', 'PRESS', alt=True)

        self.add('mesh.armored_extract',    'E', 'PRESS', ctrl=True, shift=True)
        self.add('mesh.armored_duplicate',  'D', 'PRESS', ctrl=True, shift=True)

        self.add('transform.shrink_fatten', 'S', 'PRESS', alt=True); self.prop('use_even_offset', True)
        
        self.add('mesh.armored_select_adjacent',  'HOME',         'PRESS', shift=True)
        self.add('mesh.armored_select_adjacent',  'WHEELUPMOUSE', 'PRESS', ctrl=True, shift=True)

        self.add('mesh.armored_fast_bevel', 'B', 'PRESS')
        self.add('mesh.bridge_edge_loops',  'B', 'PRESS', shift=True)

        self.add('object.armored_rest_on_ground', 'R', 'PRESS', ctrl=True)
        self.add('mesh.loop_multi_select',        'R', 'PRESS', alt=True); self.prop('ring', True)  # Fallback for the next entry.
        # self.add('mesh.armored_select_edge_ring', 'R', 'PRESS', alt=True) 

        self.add('mesh.armored_connect',     'C',    'PRESS', shift=True)
        self.add('mesh.armored_align_verts', 'V',    'PRESS', shift=True)


        self.add('mesh.armored_crease', 'BUTTON5MOUSE', 'PRESS', shift=True); self.prop('crease_mode', 'CREASE')
        self.add('mesh.armored_crease', 'BUTTON4MOUSE', 'PRESS', shift=True); self.prop('crease_mode', 'UNCREASE')
        self.add('mesh.armored_crease', 'NUMPAD_PLUS',  'PRESS', shift=True); self.prop('crease_mode', 'CREASE')
        self.add('mesh.armored_crease', 'NUMPAD_MINUS', 'PRESS', shift=True); self.prop('crease_mode', 'UNCREASE')

        self.add('mesh.select_linked_pick', 'LEFTMOUSE', 'DOUBLE_CLICK', alt=True );            self.prop('deselect', False)
        self.add('mesh.select_linked_pick', 'LEFTMOUSE', 'DOUBLE_CLICK', alt=True, shift=True); self.prop('deselect', True)
        
        self.add('mesh.select_more','WHEELUPMOUSE',   'PRESS', shift=True)
        self.add('mesh.select_less','WHEELDOWNMOUSE', 'PRESS', shift=True)

        self.add('mesh.region_to_loop', 'FIVE',         'PRESS', alt=True)
        self.add('mesh.region_to_loop', 'BUTTON5MOUSE', 'PRESS')

        self.add('mesh.armored_subd_view_in_edit', 'ONE',   'PRESS', alt=True)
        self.prop('mode', 'OFF')
        self.prop('only_affect_last', False)

        self.add('mesh.armored_subd_view_in_edit', 'TWO',   'PRESS', alt=True)
        self.prop('mode', 'HYBRID')
        self.prop('only_affect_last', False)

        self.add('mesh.armored_subd_view_in_edit', 'THREE', 'PRESS', alt=True)
        self.prop('mode', 'FULL')
        self.prop('only_affect_last', False)

        self.add('mesh.armored_center_vertices', 'X', 'PRESS', ctrl=True, alt=True); self.prop('axis', 'X')
        self.add('mesh.armored_center_vertices', 'Y', 'PRESS', ctrl=True, alt=True); self.prop('axis', 'Y')
        self.add('mesh.armored_center_vertices', 'Z', 'PRESS', ctrl=True, alt=True); self.prop('axis', 'Z')

        # SubD Hotkeys for Edit Mode
        self.add('object.subdivision_set', 'ZERO',  'PRESS', ctrl=True); self.prop('level', 0)
        self.add('object.subdivision_set', 'ONE',   'PRESS', ctrl=True); self.prop('level', 1)
        self.add('object.subdivision_set', 'TWO',   'PRESS', ctrl=True); self.prop('level', 2)
        self.add('object.subdivision_set', 'THREE', 'PRESS', ctrl=True); self.prop('level', 3)
        self.add('object.subdivision_set', 'FOUR',  'PRESS', ctrl=True); self.prop('level', 4)
        self.add('object.subdivision_set', 'FIVE',  'PRESS', ctrl=True); self.prop('level', 5)
        self.add('object.subdivision_set', 'SIX',   'PRESS', ctrl=True); self.prop('level', 6)
        self.add('object.subdivision_set', 'SEVEN', 'PRESS', ctrl=True); self.prop('level', 7)
        self.add('object.subdivision_set', 'EIGHT', 'PRESS', ctrl=True); self.prop('level', 8)
        self.add('object.subdivision_set', 'NINE',  'PRESS', ctrl=True); self.prop('level', 9)


        self.km = kc.keymaps.new('Curve', space_type='EMPTY')
        Global_Keys()

        self.add('curve.shortest_path_pick', 'LEFTMOUSE', 'PRESS', ctrl=True, shift=True)
        # self.add('curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)


        self.km = kc.keymaps.new('Window', space_type='EMPTY')
        Global_Keys()

        self.enabled_message()


def register():
    for cls_name, cls_instance in keymap_groups.items():
        if getattr(addon.prefs(), cls_name.lower()):
            cls_instance.register()


def unregister():
    # It's'safe to unregister everything. 
    # Classes that never registered keymaps will "early return" from their <unregister> method.
    for cls_instance in keymap_groups.values():
        cls_instance.unregister()


# List of (cls_name, cls_obj) tuples. 
# Experiment by putting this in <register> as a global variable.
classes = mod_utils.get_module_classes(sys.modules[__name__])

# Only need 1 instance per class. Each instance can keep track of the keymaps it registers.
# Have to test if importing this module creates duplicate instances which resets the internal <registered_keymaps> list.
keymap_groups = {cls[0].lower(): cls[1]() for cls in classes}

# DEBUGGING
# addon.debug doesnt exist yet, so reference the config file (Not Implemented yet).
# for cls_name, cls_instance in keymap_groups.items():
    # print(cls_name.title().ljust(22, ' '), cls_instance)
