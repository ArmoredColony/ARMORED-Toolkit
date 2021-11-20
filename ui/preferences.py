import bpy
from bpy.props import EnumProperty, BoolProperty, StringProperty

import sys

# from .. utils.addon import Addon
from .. utils import (
    addon,
    descriptions,
    extrapy,
    paths,
)


def update(self, context, prop='', category=''):
    addon.update_resource(prop, category)


class ARMORED_PT_Toolkit_Preferences(bpy.types.AddonPreferences):
    bl_idname = addon.name()

    def closure(prop, category):
        return lambda a, b: update(a, b, prop, category)   # a, b = self, context
    

    maya_navigation: BoolProperty(name='Maya Poop', default=False,
            description='Maya style navigation (ALT + Mouse Buttons)', update=closure(prop='maya_navigation', category='keymap'))

    # maya_extrude: BoolProperty(name='Maya Extrude', default=False,
    #         description='Extrude faces along their individual normals (like Maya)', update=closure(prop='maya_extrude', category='keymap'))

    loop_selection: BoolProperty(name='Double Click to Select Loops', default=False,
            description='Double Click to select component loops', update=closure(prop='loop_selection', category='keymap'),)
        
    focus_selected_with_f: BoolProperty(name='Focus Selected with F', default=False,
            description='Frame your selection with the F key (NUMPAD_PERIOD can still be used)', update=closure(prop='focus_selected_with_f', category='keymap'),)

    deselect_with_ctrl: BoolProperty(name='Deselect with CTRL', default=False,
            description='CTRL Click now deselects stuff (both in Edit and Object mode)', update=closure(prop='deselect_with_ctrl', category='keymap'),)

    transform_with_gizmos: BoolProperty(name='Transform with Gizmos', default=False,
            description='Use the Gizmo version of the Move, Rotate and Scale Tools', update=closure(prop='transform_with_gizmos', category='keymap'),)

    allow_gizmo_click: BoolProperty(name='Allow Gizmo Click', default=False,
            description='Activate Gizmos on Click instead of waiting for a Drag event', update=closure(prop='allow_gizmo_click', category='keymap'),)

    sculpting_setup: BoolProperty(name='Sculpting Setup', default=False,
            description='Enables number row keymaps for brushes and more.\n\n' + descriptions.sculpting_keymaps, update=closure(prop='sculpting_setup', category='keymap'),)

    operator_shortcuts: BoolProperty(name='Operator Keymaps', default=False, 
            description='Enables predefined keymaps for a bunch of my operators (scripts) in the Armored Toolkit.\n\n' + descriptions.operator_keymaps, update=closure(prop='operator_shortcuts', category='keymap'),)

    tab_history: BoolProperty(name='TAB History', default=False,
            description='Use custom TAB functionality.\n\n' + descriptions.smart_tab_functions, update=closure(prop='tab_history', category='keymap'),)

    tab_undo_mode: EnumProperty(name='Undo behaviour for each TAB press', default='GROUPED',
            description='TAB Undo Behaviour ', update=closure(prop='tab_undo_mode', category='operator_refresh'),
            items=[ ('NORMAL',  'Blender Default',            'Create one undo step for each TAB press'), 
                    ('GROUPED', 'Grouped Undo (recommended)', 'Combine repeated TAB presses into a single Undo step'),
                    ('NONE',    'Skip Undo',                  'Pressing TAB does NOT generate undo history'), ])

    matcaps: BoolProperty(name='Matcaps', default=False,
            description='Just some barely useful matcaps', update=closure(prop='matcaps', category='matcap'),)

    hdris: BoolProperty(name='HDRIs', default=False,
            description='Just some barely useful HDRI', update=closure(prop='hdris', category='hdri'),)

    studio_lights: BoolProperty(name='Studio Lights', default=False,
            description='Just some barely useful Studio Lights', update=closure(prop='studio_lights', category='studio_light'),)

    debug: BoolProperty(name='Debug', default=False,
            description='Prints developer oriented information in the console window. Not really meant for end users.')


    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        def prop_line(prop, icon, url='www.youtube.com/armoredcolony', text=''):
            row = box.column(align=True).row()

            row.label(text=text or extrapy.format_string(prop))
            row.separator()
            row.prop(self, prop, text='On' if getattr(self, prop) else 'Off', toggle=True);
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

        box = col1.box()
        box.label(text='Extra Resources')
        prop_line(prop='matcaps', icon='MATERIAL', url='www.youtube.com')
        prop_line(prop='hdris', icon='MATERIAL', url='www.youtube.com', text='HDRIs')
        prop_line(prop='studio_lights', icon='MATERIAL', url='www.youtube.com')
        col1.separator()
        
        box = col1.box()
        box.label(text='TAB History')
        prop_line(prop='tab_history', icon='FILE_MOVIE', url='www.youtube.com')
        if self.tab_history:
            box.prop(self, 'tab_undo_mode', text='', expand=False)
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
        box.operator('armored.open_folder', text='Operators Folder', icon='ERROR')      .path = paths.BlenderPaths.operators
        box.operator('armored.open_folder', text='Keymaps File',     icon='FILE_SCRIPT').path = paths.BlenderPaths.keymaps
        box.operator('armored.open_folder', text='Startup Folder',   icon='FILE_FOLDER').path = paths.BlenderPaths.startup
        box.operator('armored.open_folder', text='Matcaps Folder',   icon='MATERIAL')   .path = paths.BlenderPaths.matcaps
        box.operator('armored.open_folder', text='Themes Folder',    icon='TOPBAR')     .path = paths.BlenderPaths.themes

        col2.separator()
        box = col2.box()
        box.label(text='Developer Tools')
        box.prop(self, 'debug', toggle=True)

        layout.label(text=('Python ' + sys.version))


classes = (
    ARMORED_PT_Toolkit_Preferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
