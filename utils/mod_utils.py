from .. utils import addon
import importlib
import os


def import_module(folder, module_name):
    return importlib.import_module('.'.join([addon.get_name(), folder, module_name]))


def import_modules(folder, debug=False):
    path = os.path.join(addon.get_path(), folder)
    module_names = [file[:-3] for file in os.listdir(path) if file.endswith('.py') and file != '__init__.py']
    return [import_module(folder, module) for module in module_names]


def register_modules(modules, action='register', debug=False):
    if debug:
        print(f'\n{action.upper()}ING {addon.get_name()}...')

    for module in modules:
        method = getattr(module, action, None)

        if method is not None:
            method()
            if debug: 
                print(f'  {action.title()}ed: {module.__name__}')


def reload_modules(modules, debug=False):
    if debug:
        print(f'\nRELOADING {addon.get_name()}...')

    for module in modules:
        importlib.reload(module)

        if debug: 
            print(f'  Reloaded: {module.__name__}')
