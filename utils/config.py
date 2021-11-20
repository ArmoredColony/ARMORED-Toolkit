import os
from configparser import ConfigParser

from . import(
    addon,
    paths,
)

parser = ConfigParser()
file_name = 'ARM-TK_Config.ini'
config_path = os.path.join(paths.BlenderPaths.config, file_name)
section_names = [
    'keymaps',
    'matcaps',
    'hdris',
    'studio_lights',
    'themes',
    'system',
]

def new_config(config_path=config_path, section_names=section_names):
    for name in section_names:
        parser.add_section(name)
    write_config(config_path)

def read_config(config_path=config_path):
    parser.read(config_path)

def set_config(prop, category, state):
    parser.set(category, prop, str(state))
    
def write_config(config_path=config_path):
    with open(config_path, 'w') as config_file:
        parser.write(config_file)

def load_config(config_path=config_path):
    parser.read(config_path)

    for section in parser.sections():
        for (prop, _) in parser.items(section):
            attr = getattr(addon.prefs(), prop, None)

            if attr is None:
                parser.remove_option(section, prop)
                write_config()
                if addon.debug():
                    print(f'ARM-TK Config: Removed KEY {prop} from SECTION {section}')
                continue

            state = parser.getboolean(section, prop)
            if state != attr:
                setattr(addon.prefs(), prop, state)
                if addon.debug():
                    print(f'ARM-TK Config: KEY {prop} different from blender')

            elif addon.debug():
                print(f'ARM-TK Config: KEY {prop} matches blender')