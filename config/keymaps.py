import bpy

import sys

from .. utils import(
    addon, 
    keymap_utils,
    mod_utils,
)

# We need instances so they can keep track of their own keymaps,
# and we know exactly which to unregister when the need arises.
# classes = mod_utils.get_module_classes(sys.modules[__name__])
# print(classes)
# keymap_groups = {cls[0]: cls[1]() for cls in classes}
# keymap_groups = dict(mod_utils.get_module_class_names(sys.modules[__name__]))
# print(f'items {keymap_groups.items()}')
# for key in keymap_groups.items():
#     print(key)

# Use underscores in the class names so the addon.update function can call them by
# formatting the property names (in our preferences) with <cls = getattr(keymaps, prop.upper())>.

wm = bpy.context.window_manager
kc = wm.keyconfigs.addon

class MAYA_NAVIGATION(keymap_utils.KeymapGroup):
    # @classmethod
    def register(self):
        km = kc.keymaps.new('3D View', space_type='VIEW_3D')

        self.add(km, 'view3d.rotate', 'LEFTMOUSE',   'CLICK_DRAG', alt=True)
        self.add(km, 'view3d.move',   'MIDDLEMOUSE', 'PRESS', alt=True)
        self.add(km, 'view3d.zoom',   'RIGHTMOUSE',  'PRESS', alt=True)

        self.enabled_message()


# class MAYA_EXTRUDE(keymap_utils.KeymapGroup):
#     def register(self):
#         km = kc.keymaps.new(name='Mesh')

#         self.add(km, 'mesh.armored_extrude', 'E', 'PRESS', alt=True)

#         if addon.debug():
            # print(f'Enabled {self.__name__.replace("_", " ").title()}')


class LOOP_SELECTION(keymap_utils.KeymapGroup):
    # @classmethod
    def register(self):
        km = kc.keymaps.new(name='Mesh')

        # Loop Select
        kmi = self.add(km, 'mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK')
        self.kmi_props(kmi.properties, 'extend',   False)
        self.kmi_props(kmi.properties, 'deselect', False)
        self.kmi_props(kmi.properties, 'toggle',   False)

        # Loop Select ADD
        kmi = self.add(km, 'mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK', shift=True)
        self.kmi_props(kmi.properties, 'extend',   True)
        self.kmi_props(kmi.properties, 'deselect', False)
        self.kmi_props(kmi.properties, 'toggle',   True)

        # Loop Select REMOVE
        kmi = self.add(km, 'mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK', ctrl=True)
        self.kmi_props(kmi.properties, 'extend',   False)
        self.kmi_props(kmi.properties, 'deselect', True)
        self.kmi_props(kmi.properties, 'toggle',   False)

        self.enabled_message()


class FOCUS_SELECTED_WITH_F(keymap_utils.KeymapGroup):
    # @classmethod
    def register(self):
        '''
        Some keymaps work with the global km = kc.keymaps.new('Window') (space_type defaults to EMPTY)
        ...but others get overriden by more specific category names. Not sure how space_type affects priority.
        Individual KMs is ugly but it guarantees priority
        '''

        km = kc.keymaps.new('Outliner', space_type='OUTLINER')
        self.add(km, 'outliner.show_active',  'F', 'PRESS')

        # km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        # self.add(km, 'view3d.view_selected',    'F', 'PRESS')

        km = kc.keymaps.new('Object Mode')  # DEFAULT space_type is 'EMPTY'
        # self.add(km, 'view3d.view_selected',    'F', 'PRESS')
        self.add(km, 'mesh.armored_focus', 'F', 'PRESS')

        km = kc.keymaps.new('Mesh')
        # self.add(km, 'view3d.view_selected',    'F', 'PRESS')
        self.add(km, 'mesh.armored_focus', 'F', 'PRESS')
        
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

        self.enabled_message()

    
class DESELECT_WITH_CTRL(keymap_utils.KeymapGroup):
    # @classmethod
    def register(self):
        km = kc.keymaps.new(name='Object Mode')
        self.add(km, 'armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        km = kc.keymaps.new(name='Mesh')
        self.add(km, 'armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        km = kc.keymaps.new('Curve', space_type='EMPTY')
        self.add(km, 'armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        self.enabled_message()


class TRANSFORM_WITH_GIZMOS(keymap_utils.KeymapGroup):
    # @classmethod
    def register(self):
        km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        # self.add(km, 'wm.tool_set_by_id', 'G', 'PRESS').properties.name = 'builtin.move'
        # self.add(km, 'wm.tool_set_by_id', 'R', 'PRESS').properties.name = 'builtin.rotate'
        # self.add(km, 'wm.tool_set_by_id', 'S', 'PRESS').properties.name = 'builtin.scale'
        # self.add(km, 'view3d.armored_toggle_tool', 'G', 'PRESS').properties.name = 'builtin.move'
        self.add(km, 'view3d.armored_toggle_tool', 'R', 'PRESS').properties.name = 'builtin.rotate'
        self.add(km, 'view3d.armored_toggle_tool', 'S', 'PRESS').properties.name = 'builtin.scale'

        self.enabled_message()


class ALLOW_GIZMO_CLICK(keymap_utils.KeymapGroup):
    # @classmethod
    def register(self):
        km = kc.keymaps.new('Generic Gizmo Maybe Drag', space_type='EMPTY')     # Makes Gizmos activate on click instead of drag.
        self.add(km, 'gizmogroup.gizmo_tweak', 'LEFTMOUSE', 'PRESS')

        self.enabled_message()


class TAB_HISTORY(keymap_utils.KeymapGroup):
    # @classmethod
    def register(self):
        # return
        km = kc.keymaps.new('Object Non-modal')
        self.add(km, 'armored.mode_toggle', 'TAB', 'PRESS')

        self.enabled_message()


class SCULPTING_SETUP(keymap_utils.KeymapGroup):
    # @classmethod
    def register(self):
        km = kc.keymaps.new(name='Sculpt')

        self.add(km, 'view3d.view_center_pick', 'F', 'PRESS', alt=True)
        # self.add(km, 'view3d.view_center_pick', 'C', 'PRESS')
        # self.add(km, 'view3d.view_center_pick', 'SPACE', 'PRESS')
        self.add(km, 'view3d.armored_subdivide', 'D', 'PRESS', ctrl=True)
        # self.add(km, 'transform.translate', 'G', 'PRESS')
        # self.add(km, 'view3d.armored_toggle_tool', 'W', 'PRESS').properties.name = 'builtin.move'

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

        self.enabled_message()


class OPERATOR_SHORTCUTS(keymap_utils.KeymapGroup):
    # @classmethod
    def register(self):

        def Global_Keys():
            self.add(km, 'screen.userpref_show', 'COMMA', 'PRESS', ctrl=True)

        # km = kc.keymaps.new('Window', space_type='EMPTY')
        # self.add(km, 'script.reload', 'F5', 'PRESS')


        # Generic (doesn't work unless separate from 3D View)
        km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        self.add(km, 'screen.redo_last', 'T', 'PRESS')


        km = kc.keymaps.new('3D View', space_type='VIEW_3D')
        Global_Keys()

        self.add(km, 'view3d.zoom_border', 'F',            'PRESS', ctrl=True, shift=True)
        self.add(km, 'view3d.zoom_border', 'BUTTON4MOUSE', 'PRESS')

        # self.add(km, 'wm.tool_set_by_id', 'Q', 'PRESS')        .properties.name = 'builtin.select_box'
        self.add(km, 'view3d.armored_paint_select', 'Q', 'PRESS') # Tapping this will activate select_box instead.
        self.add(km, 'wm.call_menu_pie',            'Q', 'DOUBLE_CLICK') .properties.name = 'ARMORED_MT_PIE_select'

        self.add(km, 'wm.context_toggle',  'W', 'PRESS', shift=True).properties.data_path = 'space_data.overlay.show_wireframes'
        self.add(km, 'wm.context_toggle',  'W', 'PRESS', alt=True  ).properties.data_path = 'space_data.overlay.show_overlays'

        # self.add(km, 'view3d.armored_toggle_tool', 'W', 'PRESS').properties.name = 'builtin.move'
        self.add(km, 'view3d.armored_toggle_tool', 'W', 'PRESS').properties.name = 'tool.gizmo_pro'

        self.add(km, 'view3d.armored_autosmooth',        'A', 'PRESS', ctrl=True, shift=True)
        self.add(km, 'view3d.armored_open_most_recent',  'R', 'PRESS', alt=True,  shift=True)
        self.add(km, 'object.armored_rest_on_ground',    'R', 'PRESS', ctrl=True)

        self.add(km, 'view3d.armored_toggle_cavity',     'C', 'PRESS', alt=True)
        self.add(km, 'view3d.armored_cycle_cavity_type', 'C', 'PRESS', alt=True, shift=True)
        self.add(km, 'view3d.armored_smart_loopcut',     'C', 'PRESS')
        self.add(km, 'view3d.armored_subdivide',         'D', 'PRESS', ctrl=True)

        self.add(km, 'view3d.armored_single_subdivision_level', 'PAGE_UP',   'PRESS').properties.action = 'INCREASE'
        self.add(km, 'view3d.armored_single_subdivision_level', 'PAGE_DOWN', 'PRESS').properties.action = 'DECREASE'
        

        km = kc.keymaps.new(name='Object Mode')
        Global_Keys()

        self.add(km, 'object.delete', 'X', 'PRESS').properties.confirm = False
        
        self.add(km, 'object.armored_export_fbx', 'E', 'PRESS', ctrl=True)

        kmi = self.add(km, 'object.move_to_collection', 'N', 'PRESS', shift=True)
        self.kmi_props(kmi.properties, 'collection_index', 0)
        self.kmi_props(kmi.properties, 'is_new', True)


        km = kc.keymaps.new(name='Mesh')
        Global_Keys()

        self.add(km, 'mesh.faces_select_linked_flat', 'F', 'PRESS', shift=True)
        self.add(km, 'mesh.edge_face_add',            'F', 'PRESS', alt=True)
        self.add(km, 'mesh.f2',                       'F', 'PRESS', alt=True) # Same keymap as above, but seems to take prio if f2 is installed and viceversa.

        self.add(km, 'mesh.armored_custom_orientation', 'D', 'PRESS')

        self.add(km, 'mesh.armored_extrude', 'E', 'PRESS', alt=True)

        self.add(km, 'mesh.armored_extract',    'E', 'PRESS', ctrl=True, shift=True)
        self.add(km, 'mesh.armored_duplicate',  'D', 'PRESS', ctrl=True, shift=True)

        self.add(km, 'transform.shrink_fatten', 'S', 'PRESS', alt=True).properties.use_even_offset = True
        
        self.add(km, 'mesh.armored_select_adjacent',  'HOME',         'PRESS', shift=True)
        self.add(km, 'mesh.armored_select_adjacent',  'WHEELUPMOUSE', 'PRESS', ctrl=True, shift=True)

        self.add(km, 'mesh.armored_fast_bevel', 'B', 'PRESS')
        self.add(km, 'mesh.bridge_edge_loops',  'B', 'PRESS', shift=True)

        self.add(km, 'object.armored_rest_on_ground', 'R', 'PRESS', ctrl=True)
        self.add(km, 'mesh.loop_multi_select',        'R', 'PRESS', alt=True).properties.ring = True # Fallback for the next entry.
        # self.add(km, 'mesh.armored_select_edge_ring', 'R', 'PRESS', alt=True) 

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

        kmi = self.add(km, 'mesh.armored_subd_view_in_edit', 'ONE',   'PRESS', alt=True)
        kmi.properties.mode = 'OFF'
        kmi.properties.only_affect_last = False

        kmi = self.add(km, 'mesh.armored_subd_view_in_edit', 'TWO',   'PRESS', alt=True)
        kmi.properties.mode = 'HYBRID'
        kmi.properties.only_affect_last - False

        kmi = self.add(km, 'mesh.armored_subd_view_in_edit', 'THREE', 'PRESS', alt=True)
        kmi.properties.mode = 'FULL'
        kmi.properties.only_affect_last = False

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

        self.add(km, 'curve.shortest_path_pick', 'LEFTMOUSE', 'PRESS', ctrl=True, shift=True)
        # self.add(km, 'curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)


        km = kc.keymaps.new('Window', space_type='EMPTY')
        Global_Keys()

        self.enabled_message()


# classes = mod_utils.get_module_classes(sys.modules[__name__])

def register():
    # return
    '''Not sure if loading properties from config.ini file automatically triggers their update function
    and registration, but I still have to check them anyway in case some properties have not been
    written to config.ini in the first place'''

    # from .. utils import addon 
    # addon.load_config()

    for name, cls_instance in keymap_groups.items():
        if getattr(addon.prefs(), name.lower()):
            cls_instance.register()


def unregister():
    # return
    for name, cls_instance in keymap_groups.items():
        # if not cls_instance.keymap_list:
            # continue
        # print(f'{name} has {len(cls_instance.keymap_list)} elements')
        # for km, kmi in cls_instance.keymap_list:
        #     print(kmi.idname)
        cls_instance.unregister()

# Create an instance of each class so we can loop through them when we register/unregister.
# keymap_classes = {name: eval(name.upper())() for name in keymap_names}

# clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
# print(f'CLS MEMBERS {clsmembers}')

classes = mod_utils.get_module_classes(sys.modules[__name__])
# for cls in classes:
    # print(cls)

keymap_groups = {cls[0].lower(): cls[1](name=cls[0]) for cls in classes}
# keymap_groups = dict(classes)
# print(f'items {keymap_groups.items()}')

for key, value in keymap_groups.items():
    print(key.title().ljust(22, ' '), value)
