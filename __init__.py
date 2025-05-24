bl_info = {
    'name'        : 'ARMORED Toolkit',
    'description' : 'A collection of Scripts, Hotkeys and other goodies.',
    'author'      : 'Armored Colony',
    'version'     : (0, 8, 5),
    'blender'     : (2, 83),
    'location'    : 'Type "ARMORED" in the search menu.',
    # 'warning'     : 'Whatever', # Used for warning icon and text in addons panel.
    'doc_url'    : 'https://github.com/ArmoredColony/ARMORED-Toolkit', # This should be for Documentation.
    'category'    : 'ARMORED',
}

DEBUG_MODE = False


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
    mod_utils.reload_addon(DEBUG_MODE)

import bpy


def register():
    mod_utils.register_modules(addon_modules, DEBUG_MODE)


def unregister():
    mod_utils.unregister_modules(reversed(addon_modules), DEBUG_MODE)