import importlib
import os
import inspect

from .. utils import addon


def import_module(folder, module_name):
    return importlib.import_module('.'.join([addon.name(), folder, module_name]))


def import_modules(folder, debug=False):
    path = os.path.join(addon.path(), folder)
    module_names = [file[:-3] for file in os.listdir(path) if file.endswith('.py') and file != '__init__.py']
    return [import_module(folder, module) for module in module_names]


def register_modules(modules, action='register', debug=False):
    if debug:
        print(f'\n{action.upper()}ING: {addon.name()}...')

    for module in modules:
        if debug:
            print(f'  {action.title()}ing: {module.__name__}')

        method = getattr(module, action, None)
        if method is not None:
            method()


def reload_modules(modules, debug=False):
    if debug:
        print(f'\nRELOADING {addon.name()}...')

    for module in modules:
        importlib.reload(module)

        if debug: 
            print(f'  Reloaded: {module.__name__}')


def get_module_classes(module):
    return [(name, obj) for name, obj in inspect.getmembers(module) if inspect.isclass(obj)]


def get_module_class_names(module):
    return [name for name, ignore_obj in inspect.getmembers(module) if inspect.isclass(ignore_obj)]