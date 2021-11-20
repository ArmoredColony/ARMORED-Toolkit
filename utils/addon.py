import bpy
import os

from .. config import matcaps, keymaps, themes, system, resources
from . import paths
from configparser import ConfigParser


config = ConfigParser()
filename = 'ARMORED_Toolkit_Prefs.ini'
config_path = os.path.join(paths.BlenderPaths.config, filename)

config.add_section('keymap')
config.add_section('matcap')
config.add_section('hdri')
config.add_section('studio_light')
config.add_section('theme')
config.add_section('system')
config.add_section('operator_refresh')


def update_config_file():
    with open(config_path, 'w') as configfile:
        config.write(configfile)


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

    if category == 'keymap':
        # cls = getattr(keymaps, prop.upper())
        cls = keymaps.keymap_groups[prop]

        if state:   cls.register()
        else:       cls.unregister()

    elif category == 'matcap':
        if state:   resources.Matcaps.load()
        else:       resources.Matcaps.unload()

    elif category == 'hdri':
        if state:   resources.HDRI.load()
        else:       resources.HDRI.unload()

    elif category == 'studio_light':
        if state:   resources.StudioLights.load()
        else:       resources.StudioLights.unload()

    elif category == 'theme':
        if state:   themes.apply_theme()
        else:       themes.reset_theme()

    # elif category == 'system':
    #     if state:   system.apply_system_preferences()
    #     else:       system.reset_system_preferences()

    elif category == 'operator_refresh':
        from .. operators import ARMORED_mode_toggle

        ARMORED_mode_toggle.unregister()
        ARMORED_mode_toggle.register()

    if category != 'operator_refresh':
        config.set(category, prop, str(state))
        update_config_file()


def load_config():
    config.read(config_path)

    for section in config.sections():
        for (prop, _) in config.items(section):
            attr = getattr(prefs(), prop, None)

            if attr is None:
                config.remove_option(section, prop)
                update_config_file()
                if debug():
                    print(f'ARM-TK Config: Removed KEY {prop} from SECTION {section}')
                continue

            state = config.getboolean(section, prop)
            if state != attr:
                setattr(prefs(), prop, state)
                if debug():
                    print(f'ARM-TK Config: KEY {prop} different from blender')

            elif debug():
                print(f'ARM-TK Config: KEY {prop} matches blender')


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

