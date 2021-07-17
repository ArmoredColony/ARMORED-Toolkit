import bpy
import os

from .. customize import matcaps, keymaps, themes, system
from configparser import ConfigParser


config = ConfigParser()
filename = 'ARMORED_toolkit_prefs.ini'
config_path = os.path.join(bpy.utils.user_resource('SCRIPTS', create=True), filename)

config.add_section('keymap')
config.add_section('matcap')
config.add_section('theme')
config.add_section('system')
config.add_section('operator_refresh')


def update_config_file():
    with open(config_path, 'w') as configfile:
        config.write(configfile)


def get_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_name():
    return __package__.split(".")[0]
    # return os.path.basename(get_path())


def preferences():
    return bpy.context.preferences.addons[get_name()].preferences


def debug():
    return preferences().debug


class FolderPaths():
    datafiles = bpy.utils.user_resource('DATAFILES', create=True)
    scripts   = bpy.utils.user_resource('SCRIPTS', create=True)
    startup   = bpy.utils.user_resource('SCRIPTS', path='startup', create=True)
    themes    = bpy.utils.user_resource('SCRIPTS',   path=os.path.join('presets', 'interface_theme'), create=True)
    matcaps   = bpy.utils.user_resource('DATAFILES', path=os.path.join('studiolights', 'matcap'), create=True)
    operators = os.path.join(get_path(), 'operators')
    keymaps   = os.path.join(get_path(), 'customize', 'keymaps.py')


def update(prop, category):
    '''Enable or Disable different aspects of the Addon based on the Preferences'''

    # state = True if getattr(preferences(), prop) == 'ENABLED' else False
    # state = getattr(preferences(), prop) == 'ENABLED'
    state = getattr(preferences(), prop)
    
    # state = getattr(AddonClass.preferences(), prop)
    # print(f'STATE: {state}')

    if category == 'keymap':
        cls = keymaps.keymap_classes[prop]

        if state:   
            cls.register()
        else:       
            cls.unregister()

    elif category == 'matcap':
        if state:   matcaps.load_matcaps()
        else:       matcaps.unload_matcaps()

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
            attr = getattr(preferences(), prop, None)

            if attr is None:
                config.remove_option(section, prop)
                update_config_file()
                if debug():
                    print(f'ARM-TK Config: Removed KEY {prop} from SECTION {section}')
                continue

            state = config.getboolean(section, prop)
            if state != attr:
                setattr(preferences(), prop, state)
                if debug():
                    print(f'ARM-TK Config: KEY {prop} different from blender')

            elif debug():
                print(f'ARM-TK Config: KEY {prop} matches blender')


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

    
#     with open(config_path, 'w') as configfile:
#         config.write(configfile)
#     pass

