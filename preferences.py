import bpy
from bpy.props import EnumProperty, BoolProperty, StringProperty

from . utils import (
    addon,
    extrapy,
)
# from . utils.addon import get_name, get_path, update, folder_paths

import os
from os.path import dirname

# FOLDERS
# datafiles_path = bpy.utils.user_resource('DATAFILES', create=True)
# datafiles_path = bpy.utils.user_resource('SCRIPTS', 'ADDONS', create=True)
# scripts_path   = bpy.utils.user_resource('SCRIPTS', create=True)
# startup_path   = bpy.utils.user_resource('SCRIPTS', 'startup', create=True)
# theme_path     = bpy.utils.user_resource('SCRIPTS',   os.path.join('presets', 'interface_theme'), create=True)
# matcap_path    = bpy.utils.user_resource('DATAFILES', os.path.join('studiolights', 'matcap'), create=True)
# operators_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'operators')

# print(f'testerino patherino {folder_paths.datafiles_path}')

class ARMORED_PT_Toolkit_Preferences(bpy.types.AddonPreferences):
    bl_idname = addon.get_name()

    def update_theme(self, context):
        addon.update(prop='themes', category='theme')

    def update_maya_navigation(self, context):
        addon.update(prop='maya_navigation', category='keymap')

    def update_loop_selection(self, context):
        addon.update(prop='loop_selection', category='keymap')

    def update_deselect_with_ctrl(self, context):
        addon.update(prop='deselect_with_ctrl', category='keymap')

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
        addon.update(prop='system_preferences', category='system')

    def test_func(self, context):
        write_default_config()
        

    maya_navigation: BoolProperty(name='Maya Navigation', default=False,
            description='Maya style navigation (ALT + Mouse Buttons)',
            update=update_maya_navigation)

    loop_selection: BoolProperty(
        name='Double Click to Select Loops', 
        default=False,
        update=update_loop_selection,
        description='Double Click to select component loops',
        # items=[ ('ENABLED',  'On', ''), 
                # ('DISABLED', 'Off (default)', ''),
            # ]
        )

    deselect_with_ctrl: BoolProperty(
        name='Deselect with CTRL', 
        default=False,
        update=update_deselect_with_ctrl,
        description='CTRL Click now deselects stuff (both in Edit and Object mode)',
        # items=[ ('ENABLED',  'On', ''), 
        #         ('DISABLED', 'Off (default)', ''),
        #     ]
        )

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
        'SHIFT W - Wireframe'
    ]

    packed_description = '\n'.join(line for line in list_description)

    sculpting_setup: BoolProperty(
        name='Sculpting Setup', 
        default=False,
        update=update_sculpting_setup,
        description='Enables number row keymaps for brushes and more\n\n' + packed_description,
        # items=[ ('ENABLED',  'On', packed_description), 
        #         ('DISABLED', 'Off (default)', ''),
        #     ]
        )

    operator_shortcuts: BoolProperty(
        name='Operator Keymaps', 
        default=False,
        update=update_operator_shortcuts,
        description='Enables the predefined keymaps for a bunch of operators in the Armored Toolkit',
        # items=[ ('ENABLED',  'On', ''), 
        #         ('DISABLED', 'Off (default)', ''),
        #     ]
        )
    
    list_description = [
        'Change the undo history behaviour of TAB press',
        'Sculpt mode toggles to Object mode instead of Edit mode',
        'Try to always toggle between Edit and Object modes (except when sculpting)'
    ]

    packed_description = '\u2022 ' + ( '\n\u2022 '.join(line for line in list_description) )
    
    smart_tab: BoolProperty(
        name='Smart TAB', 
        default=False,
        update=update_smart_tab,
        description='Use custom TAB functionality',
        # items=[ ('ENABLED',  'On', packed_description), 
        #         ('DISABLED', 'Off (default)', 'Use blender\'s default TAB operator'),
        #     ]
        )

    tab_undo_mode: EnumProperty(
        name='Undo behaviour for smart TAB', 
        default='GROUPED',
        update=update_tab_undo_mode,
        description='TAB Undo Behaviour ',
        items=[ ('NORMAL',  'Blender Default', 'Create one undo step for each TAB press'), 
                ('GROUPED', 'Grouped Undo (recommended)', 'Combine repeated TAB presses into a single Undo step'),
                ('NONE', 'No Undo', 'Pressing TAB does NOT generate undo history'),
            ]
        )

    matcaps: BoolProperty(
        name='Matcaps', 
        default=False,
        update=update_matcaps,
        description='Consult the PDF for a detailed list of my personal keymaps, what PDF LUL',
        # items=[ ('ENABLED', 'On (default)', 'Override Blender\'s default Keymaps with my personal setup.'), 
        #         ('DISABLED', 'Off', 'Disable my personal Keymaps and leave Blender\'s keymaps as they were'),
        #     ]
        )

    themes: BoolProperty(
        name='Themes', 
        default=False,
        update=update_theme,
        description='Consult the PDF for a detailed list of my personal keymaps, what PDF LUL',
        # items=[ ('ENABLED', 'On', 'Use one of my custom themes.'), 
        #         ('DISABLED', 'Off (default)', 'Use whatever theme oyu had before.'),
        #     ]
        )

    # theme_list: BoolProperty(
    #     name='Themes', 
    #     default='BLENDER_DARK',
    #     # update=update_theme,
    #     description='Consult the PDF for a detailed list of my personal keymaps',
    #     # items=[ ('BLENDER_DARK', 'Blender Dark (default)', 'Default Blender Theme.'), 
    #     #         ('ARMORED_PINK', 'Armored Pink (NEW)', 'My current theme (dark).'),
    #     #         ('ARMORED_PINK_LEGACY', 'Armored Pink (legacy)', 'My previous theme (not as dark).'),
    #     #     ]
    #     )

    list_description = [
        'Show Splash OFF',
        'Python Tooltips ON',
        'Mouse Drag Threshold 1',
        'Invert Mouse Zoom ON',
        'Undo Steps 90',
    ]

    packed_description = '\u2022 ' + ( '\n\u2022 '.join(line for line in list_description) )
    
    system_preferences: BoolProperty(
        name='Armored Preferences', 
        default=False,
        update=update_system_preferences,
        description='My custom system preferences',
        # items=[ ('ENABLED', 'On', packed_description), 
        #         ('DISABLED', 'Off (default)', 'Use default system preferences'),
        #     ]
        )
    
    matcaps_folder: StringProperty(
        name='Example File Path',
        # subtype='FILE_PATH',
        )
    
    boolean : BoolProperty(name='Bool Prop', default=True, update=test_func)
    # theme : BoolProperty(name='Armored Theme', default=True, update=update_theme)


    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        def enum_line(prop, icon, url):
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
        enum_line(prop='maya_navigation',    icon='FILE_MOVIE', url='www.youtube.com')
        enum_line(prop='loop_selection',     icon='FILE_MOVIE', url='www.youtube.com')
        enum_line(prop='deselect_with_ctrl', icon='FILE_MOVIE', url='www.youtube.com')
        enum_line(prop='sculpting_setup', icon='FILE_MOVIE', url='www.youtube.com')
        enum_line(prop='operator_shortcuts', icon='FILE_MOVIE', url='www.youtube.com')
        col1.separator()

        # box = col2.box()
        # box.label(text='Smart TAB')
        # enum_line(prop='smart_tab', icon='FILE_MOVIE', url='www.youtube.com')
        # if self.smart_tab == 'ENABLED':
        #     box.prop(self, 'tab_undo_mode', text='', expand=False)
        # col2.separator()
        
        box = col1.box()
        box.label(text='Extra Matcaps')
        enum_line(prop='matcaps', icon='MATERIAL', url='www.youtube.com')
        col1.separator()

        box = col1.box()
        box.label(text='Armored Preferences')
        enum_line(prop='system_preferences', icon='TOPBAR', url='www.youtube.com')
        col1.separator()
        
        box = col2.box()
        box.label(text='Custom Theme')
        box.operator('armored.theme_install', text='Load Armored Theme')
        box.operator('preferences.reset_default_theme', text='Reset to Default Theme')
        col2.separator()

        col2.separator()
        box = col2.box()
        box.label(text='Useful Directories')
        box.operator('armored.open_folder', text='Open Operator Folder', icon='ERROR')     .path = addon.folder_paths.operators
        box.operator('armored.open_folder', text='Open Startup Folder', icon='FILE_FOLDER').path = addon.folder_paths.startup
        box.operator('armored.open_folder', text='Open Matcaps Folder', icon='MATERIAL')   .path = addon.folder_paths.matcaps
        box.operator('armored.open_folder', text='Open Themes Folder', icon='TOPBAR')      .path = addon.folder_paths.themes



classes = (
    ARMORED_PT_Toolkit_Preferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
