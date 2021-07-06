bl_info = {
    'name'        : 'Toolkit',
    'description' : 'A collection of Scripts, Hotkeys and more',
    'author'      : 'Armored Colony',
    'version'     : (0, 1, 2),
    'blender'     : (2, 90),
    'location'    : 'Search Menu (ARMORED prefix)',
    # 'warning'     : 'Whatever', # Used for warning icon and text in addons panel.
    # 'wiki_url'    : 'www.armoredColony.com', # This should be for Documentation.
    'category'    : 'ARMORED',
}

import bpy
import os
from . import preferences


def import_modules(folderstring, reportstring='Found', debug=False):
    path = os.path.join(os.path.dirname(__file__), folderstring)
    files = [f[:-3] for f in os.listdir(path) if f.endswith('.py') and f != '__init__.py']

    modules = []
    for file in files:
        mod = __import__('.'.join([__name__, folderstring, file]), fromlist=[file])
        modules.append(mod)

        if debug: print(f'  {reportstring}: {file}')
    if debug: print(f"{reportstring.upper()} {len(modules)} MODULES IN '/{folderstring}'\n")

    return modules


# FOLDERS WITH CLASSES THAT NEED TO BE REGISTERED IN BLENDER (operators, keymaps, etc)
sub_folders = [
    'ui',  # Must be registered first and unregistered last.
    'operators_internal',
    'operators',
    'customize',
]

ALL_MODULES = []

for folder in sub_folders:
    mods = import_modules(folder)
    ALL_MODULES.extend(mods)


def register():
    preferences.register()
    for mod in ALL_MODULES:
        # print(f'registered mod: {mod.__name__}')
        mod.register()


def unregister():
    preferences.unregister()
    for mod in reversed(ALL_MODULES):
        mod.unregister()