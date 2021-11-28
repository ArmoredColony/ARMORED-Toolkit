import os
from configparser import ConfigParser, DuplicateSectionError

from . import(
    addon,
    debug,
    paths,
)

file_name = 'ARM-TK_Config.ini'
config_path = os.path.join(paths.BlenderPaths.config, file_name)
parser = ConfigParser()

def read_config(config_path=config_path):
    parser.read(config_path)


def set_config(prop_name, category, state):
    add_config_section(category)
    parser.set(category, prop_name, str(state))
    write_config()


def add_config_section(category):
    if not parser.has_section(category):
        parser.add_section(category)


def write_config(config_path=config_path):
    with open(config_path, 'w') as config_file:
        parser.write(config_file)


def load_config(config_path=config_path):
    if config_not_found(config_path):
        return

    debug.msg('ARM-TK INFO: Loading Config from', config_path)
    iterate_through_config()




def iterate_through_config():
    ''' NOTE: All variables extracted by or related to the parser (prop, section, etc) 
    are strings until converted with getboolean or similar parser methods '''
    
    read_config()
    
    for section in parser.sections():
        for prop in parser.options(section):
            if property_not_found(prop):
                remove_prop_from_config(section, prop)
                continue
            
            if property_value_mismatch(section, prop):
                update_addon_prop(section, prop)
                continue

            debug.msg(f'ARM-TK Config: KEY {prop}', '[Matches Blender]', spaces=43)


def property_value_mismatch(section, prop):
    config_prop_val = get_val_from_config(section, prop)
    addon_prop_val = getattr(addon.prefs(), prop, None)
    if config_prop_val != addon_prop_val:
        return True


def property_not_found(prop):
    addon_prop_val = getattr(addon.prefs(), prop, None)
    if addon_prop_val is None:
        return True


def remove_prop_from_config(section, prop):
    parser.remove_option(section, prop)
    write_config()
    debug.msg(f'ARM-TK Config: Removed legacy KEY {prop} from SECTION {section}')


def update_addon_prop(section, prop):
    config_prop_val = get_val_from_config(section, prop)
    setattr(addon.prefs(), prop, config_prop_val)
    debug.msg(f'ARM-TK Config: Updating {prop} to match config KEY')


def section_is_empty(section):
    if not parser.options(section):
        debug.msg(f'  Section {section} is empty.')
        return True


def  get_val_from_config(section, prop):
    try:
        config_prop_val = parser.getboolean(section, prop)
    except ValueError:
        config_prop_val = parser.get(section, prop)
    return config_prop_val


def config_not_found(config_path=config_path):
    if not os.path.exists(config_path):
        debug.msg(f'ARM-TK INFO: Specified Config Path {config_path} does not exist.\n')
        return True