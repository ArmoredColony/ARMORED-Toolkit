import bpy
import os


keymap_names = [
    'maya_navigation',
    'loop_selection',
    'focus_selected_with_f',
    'deselect_with_ctrl',
    'transform_with_gizmos',
    'smart_tab',
    'sculpting_setup',
    'operator_shortcuts',
]

wm = bpy.context.window_manager
kc = wm.keyconfigs.addon


class KeymapGroup():
    '''Keymaps that override or supersede default Blender Keymaps'''

    def __init__(self):
        self.keymap_list = []
    
    def add(self, km, idname, key, event, ctrl=False, alt=False, shift=False):
        kmi = km.keymap_items.new(idname, key, event, ctrl=ctrl, alt=alt, shift=shift)
        self.keymap_list.append((km, kmi))

        return kmi
    
    def unregister(self):
        for km, kmi in self.keymap_list:
            # print(f'    unregistering: {kmi}')
            try:
                km.keymap_items.remove(kmi)
            except RuntimeError as e:
                pass
                # print(f'ARMORED Toolkit [INFO]: Probably an F2 Exception')
        
        self.keymap_list.clear()


def kmi_props(kmi_props, attr, value):
    try:
        setattr(kmi_props, attr, value)
        
    except AttributeError:
        print(f'Warning: property {attr} not found in keymap item {kmi_props.__class__.__name__}')

    except Exception as e:
        print(f'Warning: {e}')


class MAYA_NAVIGATION(KeymapGroup):
    def register(self):
        km = kc.keymaps.new('3D View', space_type='VIEW_3D')

        self.add(km, 'view3d.rotate', 'LEFTMOUSE',   'CLICK_DRAG', alt=True)
        self.add(km, 'view3d.move',   'MIDDLEMOUSE', 'PRESS', alt=True)
        self.add(km, 'view3d.zoom',   'RIGHTMOUSE',  'PRESS', alt=True)

        print('ENABLED Maya Navigation')


class LOOP_SELECTION(KeymapGroup):
    def register(self):
        km = kc.keymaps.new(name='Mesh')

        # Loop Select
        kmi = self.add(km, 'mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK')
        kmi_props(kmi.properties, 'extend',   False)
        kmi_props(kmi.properties, 'deselect', False)
        kmi_props(kmi.properties, 'toggle',   False)

        # Loop Select ADD
        kmi = self.add(km, 'mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK', shift=True)
        kmi_props(kmi.properties, 'extend',   True)
        kmi_props(kmi.properties, 'deselect', False)
        kmi_props(kmi.properties, 'toggle',   False)

        # Loop Select REMOVE
        kmi = self.add(km, 'mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK', ctrl=True)
        kmi_props(kmi.properties, 'extend',   False)
        kmi_props(kmi.properties, 'deselect', True)
        kmi_props(kmi.properties, 'toggle',   False)

        print('ENABLED Select Loops with Double Click')


class FOCUS_SELECTED_WITH_F(KeymapGroup):
    def register(self):
        '''
        Some keymaps work with the global km = kc.keymaps.new('Window') (space_type defaults to EMPTY)
        ...but others get overriden by more specific category names, not sure how space_type affects priority.
        Individual KMs is ugly but it guarantees priority
        '''

        km = kc.keymaps.new('Outliner', space_type='OUTLINER')
        self.add(km, 'outliner.show_active',  'F', 'PRESS')

        km = kc.keymaps.new('Object Mode')  # Not sure why these sub-categories require EMPTY as space_type, which is the default.
        self.add(km, 'view3d.view_selected',    'F', 'PRESS')

        km = kc.keymaps.new('Mesh')
        self.add(km, 'view3d.view_selected',    'F', 'PRESS')
        
        km = kc.keymaps.new('Curve')
        self.add(km, 'view3d.view_selected',    'F', 'PRESS')

        km = kc.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR')
        self.add(km, 'graph.view_selected',     'F', 'PRESS')

        km = kc.keymaps.new('Image', space_type='IMAGE_EDITOR')
        self.add(km, 'image.view_selected',     'F', 'PRESS')

        km = kc.keymaps.new('Node Editor', space_type='NODE_EDITOR')
        self.add(km, 'node.view_selected',      'F', 'PRESS')

        km = kc.keymaps.new('File Browser Main', space_type='FILE_BROWSER')
        self.add(km, 'file.view_selected',      'F', 'PRESS')

        km = kc.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR')
        self.add(km, 'action.view_selected',    'F', 'PRESS')

        km = kc.keymaps.new('NLA Editor', space_type='OUTLINER')
        self.add(km, 'nla.view_selected',       'F', 'PRESS')

        km = kc.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR')
        self.add(km, 'sequencer.view_selected', 'F', 'PRESS')

        km = kc.keymaps.new('Outliner', space_type='OUTLINER')
        self.add(km, 'clip.view_selected',      'F', 'PRESS')



    
class DESELECT_WITH_CTRL(KeymapGroup):
    def register(self):
        km = kc.keymaps.new(name='Object Mode')
        self.add(km, 'armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        km = kc.keymaps.new(name='Mesh')
        self.add(km, 'armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        km = kc.keymaps.new('Curve', space_type='EMPTY')
        self.add(km, 'armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        print('ENABLED Deselect with Ctrl')


class TRANSFORM_WITH_GIZMOS(KeymapGroup):
    def register(self):
        km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        # self.add(km, 'wm.tool_set_by_id', 'G', 'PRESS').properties.name = 'builtin.move'
        # self.add(km, 'wm.tool_set_by_id', 'R', 'PRESS').properties.name = 'builtin.rotate'
        # self.add(km, 'wm.tool_set_by_id', 'S', 'PRESS').properties.name = 'builtin.scale'
        # self.add(km, 'view3d.armored_toggle_transform_tool', 'G', 'PRESS').properties.tool = 'builtin.move'
        self.add(km, 'view3d.armored_toggle_transform_tool', 'R', 'PRESS').properties.tool = 'builtin.rotate'
        self.add(km, 'view3d.armored_toggle_transform_tool', 'S', 'PRESS').properties.tool = 'builtin.scale'

        # print('ENABLED Transform with Gizmos')


class SMART_TAB(KeymapGroup):
    def register(self):
        km = kc.keymaps.new('Object Non-modal')
        self.add(km, 'armored.mode_toggle', 'TAB', 'PRESS')

        print('ENABLED Smart TAB')


class SCULPTING_SETUP(KeymapGroup):
    def register(self):
        km = kc.keymaps.new(name='Sculpt')

        self.add(km, 'view3d.view_center_pick', 'F', 'PRESS', alt=True)
        self.add(km, 'view3d.view_center_pick', 'C', 'PRESS')
        # self.add(km, 'view3d.view_center_pick', 'SPACE', 'PRESS')
        self.add(km, 'view3d.armored_smart_subdivide', 'D', 'PRESS', ctrl=True)
        # self.add(km, 'transform.translate', 'G', 'PRESS')
        # self.add(km, 'view3d.armored_toggle_transform_tool', 'W', 'PRESS').properties.tool = 'builtin.move'

        # Invert brush stroke (set to ALT instead of CTRL)
        self.add(km, 'sculpt.brush_stroke', 'LEFTMOUSE', 'PRESS', alt=True).properties.mode = 'INVERT'

        # BRUSHES
        self.add(km, 'wm.tool_set_by_id', 'ONE',   'PRESS'          ).properties.name = 'builtin_brush.Clay Strips'
        self.add(km, 'wm.tool_set_by_id', 'ONE',   'PRESS', alt=True).properties.name = 'builtin_brush.Clay'

        self.add(km, 'wm.tool_set_by_id', 'TWO',   'PRESS'          ).properties.name = 'builtin_brush.Draw Sharp'
        self.add(km, 'wm.tool_set_by_id', 'TWO',   'PRESS', alt=True).properties.name = 'builtin_brush.Draw'

        self.add(km, 'wm.tool_set_by_id', 'THREE', 'PRESS'          ).properties.name = 'builtin_brush.Scrape'
        self.add(km, 'wm.tool_set_by_id', 'THREE', 'PRESS', alt=True).properties.name = 'builtin_brush.Flatten'

        self.add(km, 'wm.tool_set_by_id', 'FOUR',  'PRESS'          ).properties.name = 'builtin_brush.Grab'
        self.add(km, 'wm.tool_set_by_id', 'FOUR',  'PRESS', alt=True).properties.name = 'builtin_brush.Snake Hook'

        self.add(km, 'wm.tool_set_by_id', 'FIVE',  'PRESS'          ).properties.name = 'builtin_brush.Crease'
        self.add(km, 'wm.tool_set_by_id', 'FIVE',  'PRESS', alt=True).properties.name = 'builtin_brush.Inflate'

        self.add(km, 'wm.context_toggle',  'W', 'PRESS', shift=True).properties.data_path = 'space_data.overlay.show_wireframes'


class OPERATOR_SHORTCUTS(KeymapGroup):
    def register(self):
        def global_focus_key():
            pass
            # self.add(km, 'mesh.armored_focus', 'F','PRESS')

        def Global_Keys():
            self.add(km, 'screen.userpref_show', 'COMMA', 'PRESS', ctrl=True)

        km = kc.keymaps.new('Window', space_type='EMPTY')
        self.add(km, 'script.reload', 'F5', 'PRESS')


        # Generic (doesn't work unless separate from 3D View)
        km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        self.add(km, 'screen.redo_last', 'T', 'PRESS')


        km = kc.keymaps.new('3D View', space_type='VIEW_3D')
        Global_Keys()

        self.add(km, 'view3d.zoom_border', 'F',            'PRESS', ctrl=True, shift=True)
        self.add(km, 'view3d.zoom_border', 'BUTTON4MOUSE', 'PRESS')

        # self.add(km, 'wm.tool_set_by_id', 'Q', 'PRESS')        .properties.name = 'builtin.select_box'
        self.add(km, 'view3d.armored_paint_select', 'Q', 'PRESS') # Tapping this will activate select_box instead.
        self.add(km, 'wm.call_menu_pie', 'Q', 'DOUBLE_CLICK') .properties.name = 'ARMORED_MT_PIE_select'

        self.add(km, 'wm.context_toggle',  'W', 'PRESS', shift=True).properties.data_path = 'space_data.overlay.show_wireframes'
        self.add(km, 'wm.context_toggle',  'W', 'PRESS', alt=True  ).properties.data_path = 'space_data.overlay.show_overlays'

        self.add(km, 'view3d.armored_toggle_transform_tool', 'W', 'PRESS').properties.tool = 'builtin.move'
        # self.add(km, 'view3d.armored_toggle_transform_tool', 'S', 'PRESS').properties.tool = 'builtin.scale'
        # self.add(km, 'view3d.armored_toggle_transform_tool', 'R', 'PRESS').properties.tool = 'builtin.rotate'

        self.add(km, 'view3d.armored_open_most_recent',  'R', 'PRESS', alt=True,  shift=True)
        self.add(km, 'view3d.armored_autosmooth',        'A', 'PRESS', ctrl=True, shift=True)
        self.add(km, 'object.armored_rest_on_ground',    'R', 'PRESS', ctrl=True)

        self.add(km, 'view3d.armored_toggle_cavity',     'C', 'PRESS', alt=True)
        self.add(km, 'view3d.armored_cycle_cavity_type', 'C', 'PRESS', alt=True, shift=True)
        self.add(km, 'view3d.armored_smart_loopcut',     'C', 'PRESS')
        # self.add(km, 'view3d.armored_subdivide',         'D', 'PRESS', ctrl=True)
        self.add(km, 'view3d.armored_smart_subdivide',         'D', 'PRESS', ctrl=True)

        self.add(km, 'view3d.armored_single_subdivision_level', 'PAGE_UP',   'PRESS').properties.action = 'INCREASE'
        self.add(km, 'view3d.armored_single_subdivision_level', 'PAGE_DOWN', 'PRESS').properties.action = 'DECREASE'
        

        km = kc.keymaps.new(name='Object Mode')
        Global_Keys()
        global_focus_key()

        self.add(km, 'object.delete', 'X', 'PRESS').properties.confirm = False

        kmi = self.add(km, 'object.move_to_collection', 'N', 'PRESS', shift=True)
        kmi_props(kmi.properties, 'collection_index', 0)
        kmi_props(kmi.properties, 'is_new', True)


        km = kc.keymaps.new(name='Mesh')
        Global_Keys()
        global_focus_key()

        self.add(km, 'mesh.faces_select_linked_flat', 'F', 'PRESS', shift=True)
        self.add(km, 'mesh.edge_face_add',            'F', 'PRESS', alt=True)
        self.add(km, 'mesh.f2',                       'F', 'PRESS', alt=True) # Same keymap as above, but seems to take prio if f2 is installed and viceversa.

        self.add(km, 'mesh.armored_extract',    'E', 'PRESS', ctrl=True, shift=True)
        self.add(km, 'mesh.armored_duplicate',  'D', 'PRESS', ctrl=True, shift=True)

        self.add(km, 'transform.shrink_fatten', 'S', 'PRESS', alt=True).properties.use_even_offset = True
        
        self.add(km, 'mesh.armored_select_adjacent',  'HOME',         'PRESS', shift=True)
        self.add(km, 'mesh.armored_select_adjacent',  'WHEELUPMOUSE', 'PRESS', ctrl=True, shift=True)

        self.add(km, 'mesh.armored_fast_bevel', 'B', 'PRESS')
        self.add(km, 'mesh.bridge_edge_loops',  'B', 'PRESS', shift=True)

        self.add(km, 'object.armored_rest_on_ground', 'R', 'PRESS', ctrl=True)
        self.add(km, 'mesh.loop_multi_select',        'R', 'PRESS', alt=True).properties.ring = True # Fallback for the next entry.
        self.add(km, 'mesh.armored_select_edge_ring', 'R', 'PRESS', alt=True) 

        self.add(km, 'mesh.armored_connect',     'C',    'PRESS', shift=True)
        self.add(km, 'mesh.armored_align_verts', 'V',    'PRESS', shift=True)

        self.add(km, 'mesh.armored_crease', 'BUTTON5MOUSE', 'PRESS', shift=True).properties.crease_mode = 'CREASE'
        self.add(km, 'mesh.armored_crease', 'BUTTON4MOUSE', 'PRESS', shift=True).properties.crease_mode = 'UNCREASE'
        self.add(km, 'mesh.armored_crease', 'NUMPAD_PLUS',  'PRESS', shift=True).properties.crease_mode = 'CREASE'
        self.add(km, 'mesh.armored_crease', 'NUMPAD_MINUS', 'PRESS', shift=True).properties.crease_mode = 'UNCREASE'

        self.add(km, 'mesh.select_linked_pick', 'LEFTMOUSE', 'DOUBLE_CLICK', alt=True )           .properties.deselect = False
        self.add(km, 'mesh.select_linked_pick', 'LEFTMOUSE', 'DOUBLE_CLICK', alt=True, shift=True).properties.deselect = True
        
        self.add(km, 'mesh.select_more','WHEELUPMOUSE',   'PRESS', shift=True)
        self.add(km, 'mesh.select_less','WHEELDOWNMOUSE', 'PRESS', shift=True)

        self.add(km, 'mesh.region_to_loop', 'FIVE',         'PRESS', alt=True)
        self.add(km, 'mesh.region_to_loop', 'BUTTON5MOUSE', 'PRESS')

        self.add(km, 'mesh.armored_subd_toggle', 'ONE',   'PRESS', alt=True).properties.mode = 'OFF'
        self.add(km, 'mesh.armored_subd_toggle', 'TWO',   'PRESS', alt=True).properties.mode = 'HYBRID'
        self.add(km, 'mesh.armored_subd_toggle', 'THREE', 'PRESS', alt=True).properties.mode = 'FULL'

        self.add(km, 'mesh.armored_center_vertices', 'X', 'PRESS', ctrl=True, alt=True).properties.axis = 'X'
        self.add(km, 'mesh.armored_center_vertices', 'Y', 'PRESS', ctrl=True, alt=True).properties.axis = 'Y'
        self.add(km, 'mesh.armored_center_vertices', 'Z', 'PRESS', ctrl=True, alt=True).properties.axis = 'Z'

        # SubD Hotkeys for Edit Mode
        self.add(km, 'object.subdivision_set', 'ZERO',  'PRESS', ctrl=True).properties.level = 0
        self.add(km, 'object.subdivision_set', 'ONE',   'PRESS', ctrl=True).properties.level = 1
        self.add(km, 'object.subdivision_set', 'TWO',   'PRESS', ctrl=True).properties.level = 2
        self.add(km, 'object.subdivision_set', 'THREE', 'PRESS', ctrl=True).properties.level = 3
        self.add(km, 'object.subdivision_set', 'FOUR',  'PRESS', ctrl=True).properties.level = 4
        self.add(km, 'object.subdivision_set', 'FIVE',  'PRESS', ctrl=True).properties.level = 5
        self.add(km, 'object.subdivision_set', 'SIX',   'PRESS', ctrl=True).properties.level = 6
        self.add(km, 'object.subdivision_set', 'SEVEN', 'PRESS', ctrl=True).properties.level = 7
        self.add(km, 'object.subdivision_set', 'EIGHT', 'PRESS', ctrl=True).properties.level = 8
        self.add(km, 'object.subdivision_set', 'NINE',  'PRESS', ctrl=True).properties.level = 9


        km = kc.keymaps.new('Curve', space_type='EMPTY')
        Global_Keys()
        global_focus_key()

        self.add(km, 'curve.shortest_path_pick', 'LEFTMOUSE', 'PRESS', ctrl=True, shift=True)
        # self.add(km, 'curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)


    # Property Editor
        # km = kc.keymaps.new('Property Editor', space_type='PROPERTIES')

        # Works for other key combos, like CTRL+Shift, but not for Shift Only.
        # self.add(km, 'screen.space_context_cycle', 'WHEELUPMOUSE',   'PRESS', shift=True).properties.direction = 'PREV'
        # self.add(km, 'screen.space_context_cycle', 'WHEELDOWNMOUSE', 'PRESS', shift=True).properties.direction = 'NEXT'


        km = kc.keymaps.new('Window', space_type='EMPTY')
        Global_Keys()
        # self.add(km, 'wm.search_menu', 'SPACE', 'PRESS')
        

        km = kc.keymaps.new('Outliner', space_type='OUTLINER')
        Global_Keys()
        self.add(km, 'outliner.show_active', 'F', 'PRESS', ctrl=True, shift=True)

        print('ENABLED Operator Keymaps')


def unregister_keymaps(prop):
    listname = prop + '_keymaps'
    keymaps_list = eval(prop + '_keymaps')
    name = prop.replace('_', ' ').title()

    # print(f'Unregistering {name} Keymaps >>')
    
    for km, kmi in keymaps_list:
        # print(f'    unregistered: {kmi}')
        try:
            km.keymap_items.remove(kmi)
        except RuntimeError as e:
            pass
            # print(f'ARMORED Toolkit [INFO]: Probably an F2 Exception')

    keymaps_list.clear()

    # print(f'DISABLED {name}')


def register():
    '''Not sure if loading properties from config.ini file automatically triggers their update function
    and registration, but I still have to check them anyway in case some properties have not been
    written to config.ini in the first place'''

    from .. utils import addon 
    addon.load_config()

    for name in keymap_names:
        if getattr(addon.preferences(), name):
            keymap_classes.get(name).register()


def unregister():
    # It's better to unregister everything.
    for cls in keymap_classes.values():
        cls.unregister()

# Does nothing except init classes (no methods are run).
keymap_classes = {name: eval(name.upper())() for name in keymap_names}