import bpy
from bpy.props import EnumProperty, BoolProperty, StringProperty

from . utils import (
    addon,
    extrapy,
)


class ARMORED_PT_Toolkit_Preferences(bpy.types.AddonPreferences):
    bl_idname = addon.get_name()

    def update_theme(self, context):
        addon.update(prop='themes', category='theme')

    def update_maya_navigation(self, context):
        addon.update(prop='maya_navigation', category='keymap')

    # def update_maya_extrude(self, context):
    #     addon.update(prop='maya_extrude', category='keymap')

    def update_loop_selection(self, context):
        addon.update(prop='loop_selection', category='keymap')

    def update_focus_selected_with_f(self, context):
        addon.update(prop='focus_selected_with_f', category='keymap')

    def update_deselect_with_ctrl(self, context):
        addon.update(prop='deselect_with_ctrl', category='keymap')

    def update_transform_with_gizmos(self, context):
        addon.update(prop='transform_with_gizmos', category='keymap')

    def update_allow_gizmo_click(self, context):
        addon.update(prop='allow_gizmo_click', category='keymap')

    def update_sculpting_setup(self, context):
        addon.update(prop='sculpting_setup', category='keymap')

    def update_operator_shortcuts(self, context):
        addon.update(prop='operator_shortcuts', category='keymap')
    
    def update_smart_tab(self, context):
        addon.update(prop='smart_tab', category='keymap')

    def update_tab_undo_mode(self, context):
        addon.update(prop='tab_undo_mode', category='operator_refresh')

    def update_matcaps(self, context):
        addon.update(prop='matcaps', category='matcap')
    
    def update_system_preferences(self, context):
        return
        # addon.update(prop='system_preferences', category='system')


    maya_navigation: BoolProperty(name='Maya Navigation', default=False,
            description='Maya style navigation (ALT + Mouse Buttons)', update=update_maya_navigation)

    # maya_extrude: BoolProperty(name='Maya Extrude', default=False,
    #         description='Extrude faces along their individual normals (like Maya)', update=update_maya_extrude)

    loop_selection: BoolProperty(name='Double Click to Select Loops', default=False,
            description='Double Click to select component loops', update=update_loop_selection,)
        
    focus_selected_with_f: BoolProperty(name='Focus Selected with F', default=False,
            description='Frame your selection with the F key (NUMPAD_PERIOD can still be used)', update=update_focus_selected_with_f,)

    deselect_with_ctrl: BoolProperty(name='Deselect with CTRL', default=False,
            description='CTRL Click now deselects stuff (both in Edit and Object mode)', update=update_deselect_with_ctrl,)

    transform_with_gizmos: BoolProperty(name='Transform with Gizmos', default=False,
            description='Use the Gizmo version of the Move, Rotate and Scale Tools', update=update_transform_with_gizmos,)

    allow_gizmo_click: BoolProperty(name='Allow Gizmo Click', default=False,
            description='Activate Gizmos on Click instead of waiting for a Drag event', update=update_allow_gizmo_click,)

    list_description = [
        '       1 - Clay Buildup',
        'ALT 1 - Clay',
        '       2 - Dam Standard',
        'ALT 2 - Standard',
        '       3 - Scrape',
        'ALT 3 - Flatten',
        '       4 - Move',
        'ALT 4 - Snake Hook',
        '       5 - Crease',
        'ALT 5 - Inflate',
        'ALT F - Set Pivot',
        'SHIFT W - Wireframe',
        'CTRL D - Add Multires Level',
        'ALT - Inverts Brush Stroke'
    ]
    packed_description = '\n'.join(line for line in list_description)
    # packed_description = '\u2022 ' + ( '\n\u2022 '.join(line for line in list_description) )

    sculpting_setup: BoolProperty(name='Sculpting Setup', default=False,
            description='Enables number row keymaps for brushes and more\n\n' + packed_description, update=update_sculpting_setup,)

    list_description = [
        '[Global]',
        'CTRL COMMA - Blender Preferences',

        '\n[3D View]',
        'T                      - Redo Panel',
        'Q                     - Border Select, Paint Select (if held down)',
        'QQ                   - Select Tools Pie',
        'SHIFT W          - Toggle Wireframe',
        'ALT W              - Toggle Overlays',
        'W                     - Toggle Move Gizmo',
        'CTRL SHIFT A  - Autosmooth',
        'ALT SHIFT R     - Open Most Recent',
        'CTRL R             - Rest on Ground',
        'ALT C               - Toggle Cavity',
        'ALT SHIFT C    - Cycle Cavity Types',
        'C (Mesh)         - Loopcut',
        'CTRL D           - Destructive Subdivision',
        'PAGE_UP        - Increase Subdivision Modifier Level',
        'PAGE_DOWN  - Decrease Subdivision Modifier Level',
        'CTRL SHIFT F - Marquee Zoom',
        'F5                    - Reload Scripts',

        # '\n\u2022Object',
        # 'SHIFT N - Move to New Collection',

        '\nThis isn\'t even half but the rest don\'t fit LMAO, I\'ll make a PDF with all my Operator Hotkeys later',

        # '\n\u2022Mesh',
        # 'SHIFT F - Select Linked Flat Faces',
        # 'ALT F - Make Face/F2 Addon',
        # 'D - Set Custom Orientation',
        # 'CTRL SHIFT LMOUSE - Select Shortest Path',
        # 'CTRL SHIFT E - Extract Faces',
        # 'CTRL SHIFT D - Duplicate Faces',
        # 'SHIFT SCROLL - Select More/Less',
        # 'CTRL SHIFT SCROLL UP - Select Adjacent Components',
        # 'B - Fast Bevel',
        # 'SHIFT B - Bridge Edges',
        # 'CTRL R - Rest on Ground',
        # 'ALT R - Select Edge Ring',
        # 'SHIFT C - Connect',
        # 'SHIFT V - Align Verts (Experimental)',
        # 'SHIFT NUMPAD_PLUS - Crease Selected',
        # 'SHIFT NUMPAD_MINUS - Uncrease Selected/All',
        # 'ALT DOUBLE_CLICK - Select Linked',
        # 'ALT 5 - Region to Loop',
        # 'ALT 1/2/3 - SubD in Edit Toggles',
        # 'CTRL ALT X,Y,Z - Align Verts to World Axis',
        # 'CTRL 1-9 - SubD Modifier Level in Edit',

        # '\n\u2022Curve',
        # 'CTRL SHIFT LMOUSE - Select SHortest Path',
    ]
    packed_description = '\n'.join(line for line in list_description)
    # packed_description = '\u2022 ' + ( '\n\u2022 '.join(line for line in list_description) )

    operator_shortcuts: BoolProperty(name='Operator Keymaps', default=False, 
            description='Enables predefined keymaps for a bunch of my operators (scripts) in the Armored Toolkit\n\n' + packed_description, update=update_operator_shortcuts,)
    

    list_description = [
        'Change the undo history behaviour of TAB press',
        'Sculpt mode toggles to Object mode instead of Edit mode',
        'Try to always toggle between Edit and Object modes (except when sculpting)'
    ]
    packed_description = '\u2022 ' + ( '\n\u2022 '.join(line for line in list_description) )
    
    smart_tab: BoolProperty(name='Smart TAB', default=False,
            description='Use custom TAB functionality', update=update_smart_tab,)

    tab_undo_mode: EnumProperty(name='Undo behaviour for smart TAB', default='GROUPED',
            description='TAB Undo Behaviour ', update=update_tab_undo_mode,
            items=[ ('NORMAL',  'Blender Default', 'Create one undo step for each TAB press'), 
                    ('GROUPED', 'Grouped Undo (recommended)', 'Combine repeated TAB presses into a single Undo step'),
                    ('NONE', 'No Undo', 'Pressing TAB does NOT generate undo history'), ])

    matcaps: BoolProperty(name='Matcaps', default=False,
            description='Just some barely useful matcaps', update=update_matcaps,)

    # themes: BoolProperty(name='Themes', default=False,
    #         description='Only one theme here: "Armored Pink", cuz it\'s not quite red but sometimes feels like pink', update=update_theme,)


    # list_description = [
    #     'Show Splash OFF',
    #     'Python Tooltips ON',
    #     'Mouse Drag Threshold 1',
    #     'Invert Mouse Zoom ON',
    #     'Undo Steps 90',
    # ]
    # packed_description = '\u2022 ' + ( '\n\u2022 '.join(line for line in list_description) )
    
    # system_preferences: BoolProperty(name='Armored Preferences', default=False,
            # description='My custom system preferences' + packed_description, update=update_system_preferences,)
    
    debug: BoolProperty(name='Debug', default=False,
            description='Prints developer oriented information in the console window. Not really meant for end users.')


    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        def prop_line(prop, icon, url):
            row = box.column(align=True).row()
            
            row.label(text=extrapy.format_string(prop))
            row.separator()
            row.prop(self, prop, text='On' if getattr(self, prop) else 'Off', toggle=True); 
            # row.separator()
            row.operator('wm.url_open', icon=icon, text='').url = url
        
        box = layout.box()
        col = box.column(align=True)
        col.label(text='This addon automatically enables developer extras', icon='ERROR')

        split = layout.split(factor=0.6)
        col1 = split.column(align=True)
        col2 = split.column(align=True)

        box = col1.box()
        box.label(text='Keymap Overrides')
        prop_line(prop='maya_navigation',       icon='FILE_MOVIE', url='www.youtube.com')
        # prop_line(prop='maya_extrude',          icon='FILE_MOVIE', url='www.youtube.com')
        prop_line(prop='loop_selection',        icon='FILE_MOVIE', url='www.youtube.com')
        prop_line(prop='focus_selected_with_f', icon='FILE_MOVIE', url='www.youtube.com')
        prop_line(prop='deselect_with_ctrl',    icon='FILE_MOVIE', url='www.youtube.com')
        # prop_line(prop='transform_with_gizmos', icon='FILE_MOVIE', url='www.youtube.com')
        prop_line(prop='allow_gizmo_click',     icon='FILE_MOVIE', url='www.youtube.com')
        prop_line(prop='sculpting_setup',       icon='FILE_MOVIE', url='www.youtube.com')
        prop_line(prop='operator_shortcuts',    icon='FILE_MOVIE', url='www.youtube.com')
        
        # for name in keymaps.keymap_names:
            # prop_line(prop=name, icon='FILE_MOVIE', url='www.youtube.com')

        col1.separator()

        box = col2.box()
        box.label(text='Smart TAB')
        prop_line(prop='smart_tab', icon='FILE_MOVIE', url='www.youtube.com')
        if self.smart_tab:
            box.prop(self, 'tab_undo_mode', text='', expand=False)
        col2.separator()
        
        box = col1.box()
        box.label(text='Extra Matcaps')
        prop_line(prop='matcaps', icon='MATERIAL', url='www.youtube.com')
        col1.separator()

        box = col2.box()
        box.label(text='Armored Preferences')
        layout.use_property_split = True
        box.operator('armored.load_custom_preferences', text='Load Preferences')
        box.operator('armored.unload_custom_preferences', text='Unload Preferences')
        # prop_line(prop='system_preferences', icon='TOPBAR', url='www.youtube.com')
        layout.use_property_split = False
        col2.separator()
        
        box = col2.box()
        box.label(text='Custom Theme')
        box.operator('armored.theme_install', text='Load Armored Theme')
        box.operator('preferences.reset_default_theme', text='Reset to Default Theme')
        col2.separator()

        col2.separator()
        box = col2.box()
        box.label(text='Useful Directories')
        box.operator('armored.open_folder', text='Operators Folder', icon='ERROR')      .path = addon.FolderPaths.operators
        box.operator('armored.open_folder', text='Keymaps File',     icon='FILE_SCRIPT').path = addon.FolderPaths.keymaps
        box.operator('armored.open_folder', text='Startup Folder',   icon='FILE_FOLDER').path = addon.FolderPaths.startup
        box.operator('armored.open_folder', text='Matcaps Folder',   icon='MATERIAL')   .path = addon.FolderPaths.matcaps
        box.operator('armored.open_folder', text='Themes Folder',    icon='TOPBAR')     .path = addon.FolderPaths.themes

        col2.separator()
        box = col2.box()
        box.label(text='Developer Tools')
        box.prop(self, 'debug', toggle=True)


classes = (
    ARMORED_PT_Toolkit_Preferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
