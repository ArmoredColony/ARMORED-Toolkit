import bpy
from abc import ABC, abstractmethod
# import sys, inspect

from .. utils import addon


wm = bpy.context.window_manager
kc = wm.keyconfigs.addon


class KeymapGroup():
    '''Keymaps that override or supersede default Blender Keymaps'''

    keymap_list = []
    
    @classmethod
    def add(cls, km, idname, key, event, ctrl=False, alt=False, shift=False):
        kmi = km.keymap_items.new(idname, key, event, ctrl=ctrl, alt=alt, shift=shift)
        cls.keymap_list.append((km, kmi))
        return kmi
    
    def register():
        raise NotImplementedError
    
    @classmethod
    def unregister(cls):
        for km, kmi in cls.keymap_list:
            try:
                km.keymap_items.remove(kmi)
            except RuntimeError:    # Probably an F2 Addon Exception
                pass
        
        cls.keymap_list.clear()

        if addon.debug():
            print(f'Disabled {cls._format_class_name()}')

    @classmethod
    def debug(cls):
        if addon.debug():
            print(f'Enabled {cls._format_class_name()}')

    @classmethod
    def _format_class_name(cls):
        return cls.__name__.replace("_", " ").title()


def kmi_props(kmi_props, attr, value):
    try:
        setattr(kmi_props, attr, value)
        
    except AttributeError:
        print(f'Warning: property {attr} not found in keymap item {kmi_props.__class__.__name__}')

    except Exception as e:
        print(f'Warning: {e}')


class MAYA_NAVIGATION(KeymapGroup):
    @classmethod
    def register(cls):
        km = kc.keymaps.new('3D View', space_type='VIEW_3D')

        cls.add(km, 'view3d.rotate', 'LEFTMOUSE',   'CLICK_DRAG', alt=True)
        cls.add(km, 'view3d.move',   'MIDDLEMOUSE', 'PRESS', alt=True)
        cls.add(km, 'view3d.zoom',   'RIGHTMOUSE',  'PRESS', alt=True)

        cls.debug()


# class MAYA_EXTRUDE(KeymapGroup):
#     def register(self):
#         km = kc.keymaps.new(name='Mesh')

#         self.add(km, 'mesh.armored_extrude', 'E', 'PRESS', alt=True)

#         if addon.debug():
            # print(f'Enabled {cls.__name__.replace("_", " ").title()}')


class LOOP_SELECTION(KeymapGroup):
    @classmethod
    def register(cls):
        km = kc.keymaps.new(name='Mesh')

        # Loop Select
        kmi = cls.add(km, 'mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK')
        kmi_props(kmi.properties, 'extend',   False)
        kmi_props(kmi.properties, 'deselect', False)
        kmi_props(kmi.properties, 'toggle',   False)

        # Loop Select ADD
        kmi = cls.add(km, 'mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK', shift=True)
        kmi_props(kmi.properties, 'extend',   True)
        kmi_props(kmi.properties, 'deselect', False)
        kmi_props(kmi.properties, 'toggle',   False)

        # Loop Select REMOVE
        kmi = cls.add(km, 'mesh.loop_select', 'LEFTMOUSE', 'DOUBLE_CLICK', ctrl=True)
        kmi_props(kmi.properties, 'extend',   False)
        kmi_props(kmi.properties, 'deselect', True)
        kmi_props(kmi.properties, 'toggle',   False)

        cls.debug()


class FOCUS_SELECTED_WITH_F(KeymapGroup):
    @classmethod
    def register(cls):
        '''
        Some keymaps work with the global km = kc.keymaps.new('Window') (space_type defaults to EMPTY)
        ...but others get overriden by more specific category names. Not sure how space_type affects priority.
        Individual KMs is ugly but it guarantees priority
        '''

        km = kc.keymaps.new('Outliner', space_type='OUTLINER')
        cls.add(km, 'outliner.show_active',  'F', 'PRESS')

        # km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        # cls.add(km, 'view3d.view_selected',    'F', 'PRESS')

        km = kc.keymaps.new('Object Mode')  # DEFAULT space_type is 'EMPTY'
        # cls.add(km, 'view3d.view_selected',    'F', 'PRESS')
        cls.add(km, 'mesh.armored_focus', 'F', 'PRESS')

        km = kc.keymaps.new('Mesh')
        # cls.add(km, 'view3d.view_selected',    'F', 'PRESS')
        cls.add(km, 'mesh.armored_focus', 'F', 'PRESS')
        
        km = kc.keymaps.new('Curve')
        cls.add(km, 'view3d.view_selected',    'F', 'PRESS')

        km = kc.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR')
        cls.add(km, 'graph.view_selected',     'F', 'PRESS')

        km = kc.keymaps.new('Image', space_type='IMAGE_EDITOR')
        cls.add(km, 'image.view_selected',     'F', 'PRESS')

        km = kc.keymaps.new('Node Editor', space_type='NODE_EDITOR')
        cls.add(km, 'node.view_selected',      'F', 'PRESS')

        km = kc.keymaps.new('File Browser Main', space_type='FILE_BROWSER')
        cls.add(km, 'file.view_selected',      'F', 'PRESS')

        km = kc.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR')
        cls.add(km, 'action.view_selected',    'F', 'PRESS')

        km = kc.keymaps.new('NLA Editor', space_type='OUTLINER')
        cls.add(km, 'nla.view_selected',       'F', 'PRESS')

        km = kc.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR')
        cls.add(km, 'sequencer.view_selected', 'F', 'PRESS')

        km = kc.keymaps.new('Outliner', space_type='OUTLINER')
        cls.add(km, 'clip.view_selected',      'F', 'PRESS')

        cls.debug()

    
class DESELECT_WITH_CTRL(KeymapGroup):
    @classmethod
    def register(cls):
        km = kc.keymaps.new(name='Object Mode')
        cls.add(km, 'armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        km = kc.keymaps.new(name='Mesh')
        cls.add(km, 'armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        km = kc.keymaps.new('Curve', space_type='EMPTY')
        cls.add(km, 'armored.deselect', 'LEFTMOUSE', 'CLICK', ctrl=True)

        cls.debug()


class TRANSFORM_WITH_GIZMOS(KeymapGroup):
    @classmethod
    def register(cls):
        km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        # cls.add(km, 'wm.tool_set_by_id', 'G', 'PRESS').properties.name = 'builtin.move'
        # cls.add(km, 'wm.tool_set_by_id', 'R', 'PRESS').properties.name = 'builtin.rotate'
        # cls.add(km, 'wm.tool_set_by_id', 'S', 'PRESS').properties.name = 'builtin.scale'
        # cls.add(km, 'view3d.armored_toggle_transform_tool', 'G', 'PRESS').properties.tool = 'builtin.move'
        cls.add(km, 'view3d.armored_toggle_transform_tool', 'R', 'PRESS').properties.tool = 'builtin.rotate'
        cls.add(km, 'view3d.armored_toggle_transform_tool', 'S', 'PRESS').properties.tool = 'builtin.scale'

        cls.debug()


class ALLOW_GIZMO_CLICK(KeymapGroup):
    @classmethod
    def register(cls):
        km = kc.keymaps.new('Generic Gizmo Maybe Drag', space_type='EMPTY')     # Makes Gizmos activate on click instead of drag.
        cls.add(km, 'gizmogroup.gizmo_tweak', 'LEFTMOUSE', 'PRESS')

        cls.debug()


class TAB_HISTORY(KeymapGroup):
    @classmethod
    def register(cls):
        # return
        km = kc.keymaps.new('Object Non-modal')
        cls.add(km, 'armored.mode_toggle', 'TAB', 'PRESS')

        cls.debug()


class SCULPTING_SETUP(KeymapGroup):
    @classmethod
    def register(cls):
        km = kc.keymaps.new(name='Sculpt')

        cls.add(km, 'view3d.view_center_pick', 'F', 'PRESS', alt=True)
        # cls.add(km, 'view3d.view_center_pick', 'C', 'PRESS')
        # cls.add(km, 'view3d.view_center_pick', 'SPACE', 'PRESS')
        cls.add(km, 'view3d.armored_subdivide', 'D', 'PRESS', ctrl=True)
        # cls.add(km, 'transform.translate', 'G', 'PRESS')
        # cls.add(km, 'view3d.armored_toggle_transform_tool', 'W', 'PRESS').properties.tool = 'builtin.move'

        # Invert brush stroke (set to ALT instead of CTRL)
        cls.add(km, 'sculpt.brush_stroke', 'LEFTMOUSE', 'PRESS', alt=True).properties.mode = 'INVERT'

        # BRUSHES
        cls.add(km, 'wm.tool_set_by_id', 'ONE',   'PRESS'          ).properties.name = 'builtin_brush.Clay Strips'
        cls.add(km, 'wm.tool_set_by_id', 'ONE',   'PRESS', alt=True).properties.name = 'builtin_brush.Clay'

        cls.add(km, 'wm.tool_set_by_id', 'TWO',   'PRESS'          ).properties.name = 'builtin_brush.Draw Sharp'
        cls.add(km, 'wm.tool_set_by_id', 'TWO',   'PRESS', alt=True).properties.name = 'builtin_brush.Draw'

        cls.add(km, 'wm.tool_set_by_id', 'THREE', 'PRESS'          ).properties.name = 'builtin_brush.Scrape'
        cls.add(km, 'wm.tool_set_by_id', 'THREE', 'PRESS', alt=True).properties.name = 'builtin_brush.Flatten'

        cls.add(km, 'wm.tool_set_by_id', 'FOUR',  'PRESS'          ).properties.name = 'builtin_brush.Grab'
        cls.add(km, 'wm.tool_set_by_id', 'FOUR',  'PRESS', alt=True).properties.name = 'builtin_brush.Snake Hook'

        cls.add(km, 'wm.tool_set_by_id', 'FIVE',  'PRESS'          ).properties.name = 'builtin_brush.Crease'
        cls.add(km, 'wm.tool_set_by_id', 'FIVE',  'PRESS', alt=True).properties.name = 'builtin_brush.Inflate'

        cls.add(km, 'wm.context_toggle',  'W', 'PRESS', shift=True).properties.data_path = 'space_data.overlay.show_wireframes'

        cls.debug()


class OPERATOR_SHORTCUTS(KeymapGroup):
    @classmethod
    def register(cls):

        def Global_Keys():
            cls.add(km, 'screen.userpref_show', 'COMMA', 'PRESS', ctrl=True)

        # km = kc.keymaps.new('Window', space_type='EMPTY')
        # cls.add(km, 'script.reload', 'F5', 'PRESS')


        # Generic (doesn't work unless separate from 3D View)
        km = kc.keymaps.new('3D View Generic', space_type='VIEW_3D')
        cls.add(km, 'screen.redo_last', 'T', 'PRESS')


        km = kc.keymaps.new('3D View', space_type='VIEW_3D')
        Global_Keys()

        cls.add(km, 'view3d.zoom_border', 'F',            'PRESS', ctrl=True, shift=True)
        cls.add(km, 'view3d.zoom_border', 'BUTTON4MOUSE', 'PRESS')

        # cls.add(km, 'wm.tool_set_by_id', 'Q', 'PRESS')        .properties.name = 'builtin.select_box'
        cls.add(km, 'view3d.armored_paint_select', 'Q', 'PRESS') # Tapping this will activate select_box instead.
        cls.add(km, 'wm.call_menu_pie',            'Q', 'DOUBLE_CLICK') .properties.name = 'ARMORED_MT_PIE_select'

        cls.add(km, 'wm.context_toggle',  'W', 'PRESS', shift=True).properties.data_path = 'space_data.overlay.show_wireframes'
        cls.add(km, 'wm.context_toggle',  'W', 'PRESS', alt=True  ).properties.data_path = 'space_data.overlay.show_overlays'

        # cls.add(km, 'view3d.armored_toggle_tool', 'W', 'PRESS').properties.name = 'builtin.move'
        cls.add(km, 'view3d.armored_toggle_tool', 'W', 'PRESS').properties.name = 'tool.gizmo_pro'

        cls.add(km, 'view3d.armored_autosmooth',        'A', 'PRESS', ctrl=True, shift=True)
        cls.add(km, 'view3d.armored_open_most_recent',  'R', 'PRESS', alt=True,  shift=True)
        cls.add(km, 'object.armored_rest_on_ground',    'R', 'PRESS', ctrl=True)

        cls.add(km, 'view3d.armored_toggle_cavity',     'C', 'PRESS', alt=True)
        cls.add(km, 'view3d.armored_cycle_cavity_type', 'C', 'PRESS', alt=True, shift=True)
        cls.add(km, 'view3d.armored_smart_loopcut',     'C', 'PRESS')
        cls.add(km, 'view3d.armored_subdivide',         'D', 'PRESS', ctrl=True)

        cls.add(km, 'view3d.armored_single_subdivision_level', 'PAGE_UP',   'PRESS').properties.action = 'INCREASE'
        cls.add(km, 'view3d.armored_single_subdivision_level', 'PAGE_DOWN', 'PRESS').properties.action = 'DECREASE'
        

        km = kc.keymaps.new(name='Object Mode')
        Global_Keys()

        cls.add(km, 'object.delete', 'X', 'PRESS').properties.confirm = False
        
        cls.add(km, 'object.armored_export_fbx', 'E', 'PRESS', ctrl=True)

        kmi = cls.add(km, 'object.move_to_collection', 'N', 'PRESS', shift=True)
        kmi_props(kmi.properties, 'collection_index', 0)
        kmi_props(kmi.properties, 'is_new', True)


        km = kc.keymaps.new(name='Mesh')
        Global_Keys()

        cls.add(km, 'mesh.faces_select_linked_flat', 'F', 'PRESS', shift=True)
        cls.add(km, 'mesh.edge_face_add',            'F', 'PRESS', alt=True)
        cls.add(km, 'mesh.f2',                       'F', 'PRESS', alt=True) # Same keymap as above, but seems to take prio if f2 is installed and viceversa.

        cls.add(km, 'mesh.armored_custom_orientation', 'D', 'PRESS')

        cls.add(km, 'mesh.armored_extrude', 'E', 'PRESS', alt=True)

        cls.add(km, 'mesh.armored_extract',    'E', 'PRESS', ctrl=True, shift=True)
        cls.add(km, 'mesh.armored_duplicate',  'D', 'PRESS', ctrl=True, shift=True)

        cls.add(km, 'transform.shrink_fatten', 'S', 'PRESS', alt=True).properties.use_even_offset = True
        
        cls.add(km, 'mesh.armored_select_adjacent',  'HOME',         'PRESS', shift=True)
        cls.add(km, 'mesh.armored_select_adjacent',  'WHEELUPMOUSE', 'PRESS', ctrl=True, shift=True)

        cls.add(km, 'mesh.armored_fast_bevel', 'B', 'PRESS')
        cls.add(km, 'mesh.bridge_edge_loops',  'B', 'PRESS', shift=True)

        cls.add(km, 'object.armored_rest_on_ground', 'R', 'PRESS', ctrl=True)
        cls.add(km, 'mesh.loop_multi_select',        'R', 'PRESS', alt=True).properties.ring = True # Fallback for the next entry.
        # cls.add(km, 'mesh.armored_select_edge_ring', 'R', 'PRESS', alt=True) 

        cls.add(km, 'mesh.armored_connect',     'C',    'PRESS', shift=True)
        cls.add(km, 'mesh.armored_align_verts', 'V',    'PRESS', shift=True)

        cls.add(km, 'mesh.armored_crease', 'BUTTON5MOUSE', 'PRESS', shift=True).properties.crease_mode = 'CREASE'
        cls.add(km, 'mesh.armored_crease', 'BUTTON4MOUSE', 'PRESS', shift=True).properties.crease_mode = 'UNCREASE'
        cls.add(km, 'mesh.armored_crease', 'NUMPAD_PLUS',  'PRESS', shift=True).properties.crease_mode = 'CREASE'
        cls.add(km, 'mesh.armored_crease', 'NUMPAD_MINUS', 'PRESS', shift=True).properties.crease_mode = 'UNCREASE'

        cls.add(km, 'mesh.select_linked_pick', 'LEFTMOUSE', 'DOUBLE_CLICK', alt=True )           .properties.deselect = False
        cls.add(km, 'mesh.select_linked_pick', 'LEFTMOUSE', 'DOUBLE_CLICK', alt=True, shift=True).properties.deselect = True
        
        cls.add(km, 'mesh.select_more','WHEELUPMOUSE',   'PRESS', shift=True)
        cls.add(km, 'mesh.select_less','WHEELDOWNMOUSE', 'PRESS', shift=True)

        cls.add(km, 'mesh.region_to_loop', 'FIVE',         'PRESS', alt=True)
        cls.add(km, 'mesh.region_to_loop', 'BUTTON5MOUSE', 'PRESS')

        kmi = cls.add(km, 'mesh.armored_subd_view_in_edit', 'ONE',   'PRESS', alt=True)
        kmi.properties.mode = 'OFF'
        kmi.properties.only_affect_last = False

        kmi = cls.add(km, 'mesh.armored_subd_view_in_edit', 'TWO',   'PRESS', alt=True)
        kmi.properties.mode = 'HYBRID'
        kmi.properties.only_affect_last - False

        kmi = cls.add(km, 'mesh.armored_subd_view_in_edit', 'THREE', 'PRESS', alt=True)
        kmi.properties.mode = 'FULL'
        kmi.properties.only_affect_last = False

        cls.add(km, 'mesh.armored_center_vertices', 'X', 'PRESS', ctrl=True, alt=True).properties.axis = 'X'
        cls.add(km, 'mesh.armored_center_vertices', 'Y', 'PRESS', ctrl=True, alt=True).properties.axis = 'Y'
        cls.add(km, 'mesh.armored_center_vertices', 'Z', 'PRESS', ctrl=True, alt=True).properties.axis = 'Z'

        # SubD Hotkeys for Edit Mode
        cls.add(km, 'object.subdivision_set', 'ZERO',  'PRESS', ctrl=True).properties.level = 0
        cls.add(km, 'object.subdivision_set', 'ONE',   'PRESS', ctrl=True).properties.level = 1
        cls.add(km, 'object.subdivision_set', 'TWO',   'PRESS', ctrl=True).properties.level = 2
        cls.add(km, 'object.subdivision_set', 'THREE', 'PRESS', ctrl=True).properties.level = 3
        cls.add(km, 'object.subdivision_set', 'FOUR',  'PRESS', ctrl=True).properties.level = 4
        cls.add(km, 'object.subdivision_set', 'FIVE',  'PRESS', ctrl=True).properties.level = 5
        cls.add(km, 'object.subdivision_set', 'SIX',   'PRESS', ctrl=True).properties.level = 6
        cls.add(km, 'object.subdivision_set', 'SEVEN', 'PRESS', ctrl=True).properties.level = 7
        cls.add(km, 'object.subdivision_set', 'EIGHT', 'PRESS', ctrl=True).properties.level = 8
        cls.add(km, 'object.subdivision_set', 'NINE',  'PRESS', ctrl=True).properties.level = 9


        km = kc.keymaps.new('Curve', space_type='EMPTY')
        Global_Keys()

        cls.add(km, 'curve.shortest_path_pick', 'LEFTMOUSE', 'PRESS', ctrl=True, shift=True)
        # cls.add(km, 'curve.draw', 'LEFTMOUSE', 'PRESS', alt=True)


        km = kc.keymaps.new('Window', space_type='EMPTY')
        Global_Keys()

        cls.debug()


def register():
    return
    '''Not sure if loading properties from config.ini file automatically triggers their update function
    and registration, but I still have to check them anyway in case some properties have not been
    written to config.ini in the first place'''

    from .. utils import addon 
    addon.load_config()

    for name in keymap_names:
        if getattr(addon.preferences(), name):
            keymap_classes.get(name).register()


def unregister():
    return
    # It's better to unregister everything.
    for cls in keymap_classes.values():
        cls.unregister()

# Create an instance of each class so we can loop through them when we register/unregister.
# keymap_classes = {name: eval(name.upper())() for name in keymap_names}

# clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
# print(f'CLS MEMBERS {clsmembers}')
