# v0.1

import bpy
import os
import shutil

from .. utils import addon


debug = False


# def get_source_matcaps():
#     matcap_source_path = os.path.join(addon.get_path(), 'resources', 'matcaps')
#     return os.listdir(matcap_source_path)


def makedir(pathstring):
    import os
    
    if not os.path.exists(pathstring):
        os.makedirs(pathstring)
    return pathstring


def load_matcaps():
    data_files_path = bpy.utils.user_resource('DATAFILES', create=True)
    matcap_target_path = makedir(os.path.join(data_files_path, 'studiolights', 'matcap'))
    
    matcap_source_path = os.path.join(addon.get_path(), 'resources', 'matcaps')
    source_matcaps = os.listdir(matcap_source_path)

    installed_matcaps = set(os.listdir(matcap_target_path))

    for matcap in source_matcaps:
        if matcap in installed_matcaps:
            if debug:
                print(f'matcap {matcap} already exists')
            continue

        shutil.copy(os.path.join(matcap_source_path, matcap), matcap_target_path)

        if debug:
            print(f'Installed Matcap: {matcap}')

    bpy.context.preferences.studio_lights.refresh()


def unload_matcaps():
    data_files_path = bpy.utils.user_resource('DATAFILES', create=True)
    matcap_target_path = makedir(os.path.join(data_files_path, 'studiolights', 'matcap'))

    matcap_source_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'matcaps')
    source_matcaps = os.listdir(matcap_source_path)

    installed_matcaps = set(os.listdir(matcap_target_path))

    for matcap in source_matcaps:
        if matcap not in installed_matcaps:
            if debug:
                print(f'matcap {matcap} doesnt even exist')
            continue

        os.remove(os.path.join(matcap_target_path, matcap))
        if debug:
            print(f'Uninstalled Matcap: {matcap}')

    bpy.context.preferences.studio_lights.refresh()


def register():
    state = addon.preferences().matcaps

    if state:
        load_matcaps()
    else:
        unload_matcaps()


def unregister():

    if isinstance(bpy.context.space_data, bpy.types.SpacePreferences):
        unload_matcaps()