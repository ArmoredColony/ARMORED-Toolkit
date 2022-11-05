import bpy
import os

from . import addon


class BlenderPaths():
    '''
    Common paths used by Blender.
    '''

    config        = bpy.utils.user_resource('CONFIG', create=True)

    scripts       = bpy.utils.user_resource('SCRIPTS', create=True)
    addons        = bpy.utils.user_resource('SCRIPTS', path='addons', create=True)
    startup       = bpy.utils.user_resource('SCRIPTS', path='startup', create=True)
    themes        = bpy.utils.user_resource('SCRIPTS', path=os.path.join('presets', 'interface_theme'), create=True)

    datafiles     = bpy.utils.user_resource('DATAFILES', create=True)
    matcaps       = bpy.utils.user_resource('DATAFILES', path=os.path.join('studiolights', 'matcap'), create=True)
    hdris         = bpy.utils.user_resource('DATAFILES', path=os.path.join('studiolights', 'world'), create=True)
    studio_lights = bpy.utils.user_resource('DATAFILES', path=os.path.join('studiolights', 'studio'), create=True)
    

class AddonPaths():
    '''
    Common paths used by the Addon.
    '''

    resources = os.path.join(addon.path(), 'resources')

    matcaps       = os.path.join(resources, 'matcaps')
    hdris         = os.path.join(resources, 'hdris')
    studio_lights = os.path.join(resources, 'studio_lights')
    themes        = os.path.join(resources, 'themes')
    materials     = os.path.join(resources, 'materials')
    
    icons         = os.path.join(addon.path(), 'icons')
    docs          = os.path.join(addon.path(), 'docs')
    docs_keymaps  = os.path.join(docs, 'ARMORED-Toolkit-Keymaps.pdf')

    operators    = os.path.join(addon.path(), 'operators')
    keymaps      = os.path.join(addon.path(), 'customize', 'keymaps.py')