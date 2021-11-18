import bpy
import os

from .. customize import matcaps, keymaps, themes, system
from . import resources, paths
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

# name = __package__.split(".")[0]


def update_config_file():
    with open(config_path, 'w') as configfile:
        config.write(configfile)

class Addon():
    @classmethod
    @property
    def name(cls):
        return __package__.split(".")[0]

    @classmethod
    @property
    def path(cls):
        return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    @classmethod
    @property
    def prefs(cls):
        # import bpy
        return bpy.context.preferences.addons[cls.name].preferences

    @classmethod
    @property
    def debug(cls):
        return cls.prefs.debug
        # bpy.context.preferences.addons[get_name()].preferences.debug


def get_path():
    return Addon.path
    # return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_name():
    return Addon.name
    # return __package__.split(".")[0]
    # return os.path.basename(get_path())


def preferences():
    return Addon.prefs
    # return bpy.context.preferences.addons[get_name()].preferences


def debug():
    return Addon.debug
    # return preferences().debug


def update_resource(prop, category):
# def update(prop, category):
    '''Load or Unload different resources based on the Addon Preferences'''

    state = getattr(preferences(), prop)

    if category == 'keymap':
        cls = getattr(keymaps, prop.upper())

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

