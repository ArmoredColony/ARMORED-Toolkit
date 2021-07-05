# v0.1

import bpy
# import shutil
import os

from .. utils import addon

debug = True

# class ARMORED_OT_Resources(bpy.types.Operator):
#     bl_idname = 'armored.customize'
#     bl_label = 'MACHIN3: Customize'
#     bl_description = 'Customize various Blender preferences, settings and keymaps.'
#     bl_options = {'INTERNAL'}

# resourcespath = os.path.join(os.path.dirname(__file__), 'matcaps')
# print(f'Matcap Path: {resourcespath}')

# datafilespath = bpy.utils.user_resource('DATAFILES')
# print(f'Data Files Path: {datafilespath}')

# scriptspath = bpy.utils.user_resource('SCRIPTS')

matcapsourcepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'matcaps')
original_matcaps = os.listdir(matcapsourcepath)

def makedir(pathstring):
    import os
    
    if not os.path.exists(pathstring):
        os.makedirs(pathstring)
    return pathstring

def load_matcaps():
    import os
    import shutil

    datafilespath = bpy.utils.user_resource('DATAFILES')
    matcapsourcepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'matcaps')

    matcaptargetpath = makedir(os.path.join(datafilespath, 'studiolights', 'matcap'))
    matcaps = os.listdir(matcapsourcepath)
    installed_matcaps = set(os.listdir(matcaptargetpath))

    
    if debug:
        print(f'installed matcaps {installed_matcaps}')

    for matcap in matcaps:
        if matcap in installed_matcaps:
            if debug:
                print(f'matcap {matcap} already exists')
            continue

        shutil.copy(os.path.join(matcapsourcepath, matcap), matcaptargetpath)

        if debug:
            print(f'Installed Matcap: {matcap}')

    bpy.context.preferences.studio_lights.refresh()

    # if all([mc in matcaps for mc in ['matcap_base.exr', 'matcap_shiny_red.exr']]):
        # preferences().switchmatcap1 = 'matcap_base.exr'

def unload_matcaps():
    import os
    import shutil

    matcapsourcepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'matcaps')
    matcaps = os.listdir(matcapsourcepath)

    datafilespath = bpy.utils.user_resource('DATAFILES')
    matcaptargetpath = makedir(os.path.join(datafilespath, 'studiolights', 'matcap'))
    # matcaps = os.listdir(matcaptargetpath)

    for matcap in matcaps:
        os.remove(os.path.join(matcaptargetpath, matcap))
        if debug:
            print(f'Uninstalled Matcap: {matcap}')

    bpy.context.preferences.studio_lights.refresh()

    # if all([mc in matcaps for mc in ['matcap_base.exr', 'matcap_shiny_red.exr']]):
        # preferences().switchmatcap1 = 'matcap_base.exr'
        # preferences().switchmatcap2 = 'matcap_shiny_red.exr'


def register():
    state = addon.preferences().matcaps

    if state:
        load_matcaps()
    else:
        unload_matcaps()


def unregister():

    if isinstance(bpy.context.space_data, bpy.types.SpacePreferences):

        # disabled = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', 'Instance FALSE.txt')
        # enabled = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', 'Instance TRUE.txt')
        # addon = 'ARMORED_Toolkit'
        # enabled_addons = set(bpy.context.preferences.addons.keys())
        # try:
            # f = open(disabled, "x")
        # except FileExistsError:
            # pass

        unload_matcaps()

    # if addon not in enabled_addons:
        # print(f'Addon: {addon} is DISABLED')
        # f = open(disabled, "x")

        # delete_matcaps()
    # else:
        # print(f'Addon: {addon} is still ENABLED')
        # f = open(enabled, "x")

    # pass


    # for cls in classes:
        # bpy.utils.register_class(cls)

    # for cls in classes:
        # bpy.utils.unregister_class(cls)


# def bookmarks(self, context):
#     print("\n» Setting Custom Bookmarks")

#     path = bpy.utils.user_resource('CONFIG', "bookmarks.txt")

#     lines = ['[Bookmarks]',
#                 '!Archive',
#                 '/home/x/Archive/blender',
#                 '!TEMP',
#                 '/home/x/TEMP/blender',
#                 '!Addons',
#                 '/home/x/TEMP/blender/Addons',
#                 '!Output',
#                 '/home/x/TEMP/blender/Output',
#                 '[Recent]',
#                 '!DECALmachine',
#                 '/home/x/TEMP/blender/Addons/DECALmachine',
#                 '!MESHmachine',
#                 '/home/x/TEMP/blender/Addons/MESHmachine',
#                 ]

#     with open(path, mode='w') as f:
#         f.write('\n'.join(lines))