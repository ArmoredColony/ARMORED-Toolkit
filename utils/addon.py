import bpy
import os

from .. customize import matcaps, keymaps, themes, system
from configparser import ConfigParser


config = ConfigParser()
filename = 'ARMORED_toolkit_prefs.ini'
filepath = os.path.join(bpy.utils.user_resource('SCRIPTS', create=True), filename)
# print(f'filepath: {filepath}')

config.add_section('keymap')
config.add_section('matcap')
config.add_section('theme')
config.add_section('system')
config.add_section('operator_refresh')


class folder_paths():
    datafiles = bpy.utils.user_resource('DATAFILES', create=True)
    scripts   = bpy.utils.user_resource('SCRIPTS', create=True)
    startup   = bpy.utils.user_resource('SCRIPTS', 'startup', create=True)
    themes    = bpy.utils.user_resource('SCRIPTS',   os.path.join('presets', 'interface_theme'), create=True)
    matcaps   = bpy.utils.user_resource('DATAFILES', os.path.join('studiolights', 'matcap'), create=True)
    operators = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'operators')


def get_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_name():
    return os.path.basename(get_path())


def preferences():
    return bpy.context.preferences.addons[get_name()].preferences


def update(prop, category):
    '''Enable or Disable different aspects of the Addon based on the Preferences'''

    # state = True if getattr(preferences(), prop) == 'ENABLED' else False
    # state = getattr(preferences(), prop) == 'ENABLED'
    state = getattr(preferences(), prop)
    
    # state = getattr(AddonClass.preferences(), prop)
    # print(f'STATE: {state}')

    if category == 'keymap':
        if state:   getattr(keymaps, ('register_' + prop))()
        else:       keymaps.unregister_keymaps(prop)

    elif category == 'matcap':
        if state:   matcaps.load_matcaps()
        else:       matcaps.unload_matcaps()

    elif category == 'theme':
        if state:   themes.apply_theme()
        else:       themes.reset_theme()

    elif category == 'system':
        if state:   system.apply_system_preferences()
        else:       system.reset_system_preferences()

    elif category == 'operator_refresh':
        from .. operators import ARMORED_mode_toggle

        ARMORED_mode_toggle.unregister()
        ARMORED_mode_toggle.register()


    if category != 'operator_refresh':
        config.set(category, prop, str(state))
        with open(filepath, 'w') as configfile:
            config.write(configfile)


def load_config():
    config.read(filepath)
    for section in config.sections():

        for (prop, _) in config.items(section):
            state = config.getboolean(section, prop)
            # val = config.getboolean(section, prop)
            # state = 'ENABLED' if val else 'DISABLED'
            
            # In case the the preferences reset because the addon was disabled and enabled again.
            if state != getattr(preferences(), prop):
                setattr(preferences(), prop, state)
                # print(f'config {prop} different blender')
            else:
                pass
                # print(f'config {prop} matches blender')


# def write_config():
#     return
#     maya_navigation    = True if preferences().maya_navigation    == 'ENABLED' else False
#     loop_selection     = True if preferences().loop_selection     == 'ENABLED' else False
#     deselect_with_ctrl = True if preferences().deselect_with_ctrl == 'ENABLED' else False
#     tab_skips_undo     = True if preferences().tab_skips_undo     == 'ENABLED' else False
#     sculpting_setup    = True if preferences().tab_skips_undo     == 'ENABLED' else False
#     operator_shortcuts = True if preferences().operator_shortcuts == 'ENABLED' else False

#     config.set('keymap', 'maya_navigation', str(maya_navigation))
#     config.set('keymap', 'loop_selection', str(loop_selection))
#     config.set('keymap', 'deselect_with_ctrl', str(deselect_with_ctrl))
#     config.set('keymap', 'tab_skips_undo', str(tab_skips_undo))
#     config.set('keymap', 'sculpting_setup', str(sculpting_setup))
#     config.set('keymap', 'operator_shortcuts', str(operator_shortcuts))

    
#     with open(filepath, 'w') as configfile:
#         config.write(configfile)
#     pass

