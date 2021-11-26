import os
from configparser import ConfigParser, DuplicateSectionError

from . import(
    addon,
    paths,
)

file_name = 'ARM-TK_Config.ini'
config_path = os.path.join(paths.BlenderPaths.config, file_name)
section_names = [
    'keymaps',
    'matcaps',
    'hdris',
    'studio_lights',
    # 'themes',
    # 'system',
]

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
    print('Loading Config')
    read_config()

    for section in parser.sections():
        if not parser.items(section):
            print(f'  Section {section} is empty.')
            continue

        for (prop_name, _) in parser.items(section):
            prop_val = getattr(addon.prefs(), prop_name, None)

            if prop_val is None:
                remove_prop_from_config(section, prop_name)
                continue

            config_prop_val = parser.getboolean(section, prop_name)
            if prop_val != config_prop_val:
                update_addon_prop(prop_name, config_prop_val)

            else:
                print(f'ARM-TK Config: KEY {prop_name} matches blender')

def update_addon_prop(prop_name, config_prop_val):
    setattr(addon.prefs(), prop_name, config_prop_val)
    print(f'ARM-TK Config: KEY {prop_name} different from blender')

def remove_prop_from_config(section, prop_name):
    parser.remove_option(section, prop_name)
    write_config()
    print(f'ARM-TK Config: Removed KEY {prop_name} from SECTION {section}')
