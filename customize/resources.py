import bpy
import os

from .. utils import (
    addon,
    decorators,
    files,
    paths,
)

@decorators.abstract_class_attributes('SOURCE_PATH', 'TARGET_PATH')
class StudioResources():
    @classmethod
    def load(cls):
        files.copy_files(cls.SOURCE_PATH, cls.TARGET_PATH)
        bpy.context.preferences.studio_lights.refresh()

    @classmethod
    def unload(cls):
        files.delete_files(os.listdir(cls.SOURCE_PATH), cls.TARGET_PATH)
        bpy.context.preferences.studio_lights.refresh()


class Matcaps(StudioResources):
    SOURCE_PATH = paths.ResourcePaths.matcaps
    TARGET_PATH = paths.BlenderPaths.matcaps


class HDRIs(StudioResources):
    SOURCE_PATH = paths.ResourcePaths.hdri
    TARGET_PATH = paths.BlenderPaths.hdri


class StudioLights(StudioResources):
    SOURCE_PATH = paths.ResourcePaths.studiolights
    TARGET_PATH = paths.BlenderPaths.studiolights


def register():
    prefs = addon.prefs()

    Matcaps.load()      if prefs.matcaps       else Matcaps.unload()
    HDRIs.load()        if prefs.hdris         else HDRIs.unload()
    StudioLights.load() if prefs.studio_lights else StudioLights.unload()


def unregister():
    if isinstance(bpy.context.space_data, bpy.types.SpacePreferences):
        Matcaps.unload()
        HDRIs.unload()
        StudioLights.unload()