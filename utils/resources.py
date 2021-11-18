import bpy
import os
import shutil

from . import addon
from . import paths


def check_dir(path):
    if path is None:
        raise MissingClassAttributes()
    
    import os
    if not os.path.exists(path):
        os.makedirs(path)
    
    return path


def copy_files(source_path, target_path):
    for file in os.listdir(source_path):
        if file not in os.listdir(target_path):
            shutil.copy(os.path.join(source_path, file), target_path)
            if addon.debug(): print(f'Added {file}')


def delete_files(source_path, target_path):
    for file in os.listdir(source_path):
        if file in os.listdir(target_path):
            os.remove(os.path.join(target_path, file))
            if addon.debug(): print(f'Removed {file}')


class StudioLightResource():
    '''Made purely for inheritance'''

    source_path = None
    target_path = None

    @classmethod
    def load(cls):
        copy_files(cls.source_path, check_dir(cls.target_path))
        bpy.context.preferences.studio_lights.refresh()

    @classmethod
    def unload(cls):
        delete_files(cls.source_path, check_dir(cls.target_path))
        bpy.context.preferences.studio_lights.refresh()
        

class Matcaps(StudioLightResource):
    source_path = paths.ResourcePaths.matcaps
    target_path = paths.BlenderPaths.matcaps


class HDRI(StudioLightResource):
    source_path = paths.ResourcePaths.hdri
    target_path = paths.BlenderPaths.hdri


class StudioLights(StudioLightResource):
    source_path = paths.ResourcePaths.studiolights
    target_path = paths.BlenderPaths.studiolights



# CUSTOM EXCEPTIONS

class MissingClassAttributes(ValueError):
    def __init__(self, message=(
            'You must define valid <source_path> and <target_path> class attributes '
            'for any Sub-Class of <StudioLightResource>')):

        self.message = message
        super().__init__(self.message)