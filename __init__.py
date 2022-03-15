bl_info = {
    'name'        : 'Toolkit',
    'description' : 'A collection of Scripts, Hotkeys and more',
    'author'      : 'Armored Colony',
    'version'     : (0, 3, 2),
    'blender'     : (2, 83),
    'location'    : 'Search Menu (ARMORED prefix)',
    # 'warning'     : 'Whatever', # Used for warning icon and text in addons panel.
    # 'wiki_url'    : 'www.armoredColony.com', # This should be for Documentation.
    'category'    : 'ARMORED',
}


debug = False


# FOLDERS WITH MODULES THAT CONTAIN <register> OR <unregister> FUNCTIONS (Operators, UI Panels, etc).
sub_folders = [
    'config',   # Contains the addon preferences (register first and unregister last)
    'operators_internal',
    'operators',
    'customize',
    'ui',
]

from . utils import mod_utils
addon_modules = [module for folder in sub_folders for module in mod_utils.import_modules(folder)]

if 'bpy' in locals():
    mod_utils.reload_addon(debug)

import bpy


def register():
    mod_utils.register_modules(addon_modules, debug)


def unregister():
    mod_utils.unregister_modules(reversed(addon_modules), debug)