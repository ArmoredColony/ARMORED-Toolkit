import bpy
import os

from .. utils import (
    addon,
    debug,
    decorators,
    files,
    paths,
)

@decorators.abstract_class_attributes('SOURCE_PATH', 'TARGET_PATH')
class StudioResource():
    @classmethod
    def load(cls):
        files.copy_files(cls.SOURCE_PATH, cls.TARGET_PATH)
        bpy.context.preferences.studio_lights.refresh()

    @classmethod
    def unload(cls):
        files.delete_files(os.listdir(cls.SOURCE_PATH), cls.TARGET_PATH)
        bpy.context.preferences.studio_lights.refresh()


class Matcaps(StudioResource):
    SOURCE_PATH = paths.ResourcePaths.matcaps
    TARGET_PATH = paths.BlenderPaths.matcaps


class HDRI(StudioResource):
    SOURCE_PATH = paths.ResourcePaths.hdri
    TARGET_PATH = paths.BlenderPaths.hdri


class StudioLights(StudioResource):
    SOURCE_PATH = paths.ResourcePaths.studiolights
    TARGET_PATH = paths.BlenderPaths.studiolights
