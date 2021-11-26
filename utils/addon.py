import bpy
import os

from .. customize import keymaps, resources
from . import(
    config,
)
# from configparser import ConfigParser





def path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def name():
    return __package__.split(".")[0]

def prefs():
    return bpy.context.preferences.addons[name()].preferences

def debug():
    return prefs().debug


def update_resource(prop, category):
# def update(prop, category):
    '''Load or Unload different resources based on the Addon Preferences'''

    state = getattr(prefs(), prop)

    if category == 'keymaps':
        # cls = getattr(keymaps, prop.upper())
        keymap_group = keymaps.keymap_groups[prop]

        if state:   keymap_group.register()
        else:       keymap_group.unregister()

    elif category == 'matcaps':
        if state:   resources.Matcaps.load()
        else:       resources.Matcaps.unload()

    elif category == 'hdris':
        if state:   resources.HDRIs.load()
        else:       resources.HDRIs.unload()

    elif category == 'studio_lights':
        if state:   resources.StudioLights.load()
        else:       resources.StudioLights.unload()

    # elif category == 'theme':
    #     if state:   themes.apply_theme()
    #     else:       themes.reset_theme()

    # elif category == 'system':
    #     if state:   system.apply_system_preferences()
    #     else:       system.reset_system_preferences()

    elif category == 'operator_refresh':
        from .. operators import ARMORED_mode_toggle

        ARMORED_mode_toggle.unregister()
        ARMORED_mode_toggle.register()

    if category != 'operator_refresh':
        config.set_config(prop, category, str(state))




# def write_config():
#     return
#     maya_navigation    = True if prefs().maya_navigation    == 'ENABLED' else False
#     loop_selection     = True if prefs().loop_selection     == 'ENABLED' else False
#     deselect_with_ctrl = True if prefs().deselect_with_ctrl == 'ENABLED' else False
#     tab_skips_undo     = True if prefs().tab_skips_undo     == 'ENABLED' else False
#     sculpting_setup    = True if prefs().tab_skips_undo     == 'ENABLED' else False
#     operator_shortcuts = True if prefs().operator_shortcuts == 'ENABLED' else False

#     config.set('keymap', 'maya_navigation', str(maya_navigation))
#     config.set('keymap', 'loop_selection', str(loop_selection))
#     config.set('keymap', 'deselect_with_ctrl', str(deselect_with_ctrl))
#     config.set('keymap', 'tab_skips_undo', str(tab_skips_undo))
#     config.set('keymap', 'sculpting_setup', str(sculpting_setup))
#     config.set('keymap', 'operator_shortcuts', str(operator_shortcuts))

    
#     with open(config_path, 'w') as configfile:
#         config.write(configfile)
#     pass