import importlib
import os
import inspect

from .. utils import addon


def get_immediate_subfolders(path):
    exclude = {'resources'}
    ignore_prefixes = ('.', '__')
    return [f.name for f in os.scandir(path) 
        if f.is_dir() and not f.name.startswith(ignore_prefixes) and f not in exclude]


def import_module(folder, module_name):
    return importlib.import_module('.'.join([addon.name(), folder, module_name]))


def import_modules(folder, debug=False):
    path = os.path.join(addon.path(), folder)
    module_names = (file[:-3] for file in os.listdir(path) if file.endswith('.py') and file != '__init__.py')
    return (import_module(folder, module) for module in module_names)


def register_modules(modules, debug=False):
    for module in modules:
        method = getattr(module, 'register', None)
        if method is not None:
            method()

            if debug:
                print(f'Registered: {module.__name__}')


def unregister_modules(modules, debug=False):
    for module in modules:
        method = getattr(module, 'unregister', None)
        if method is not None:
            method()

            if debug:
                print(f'Unegistered: {module.__name__}')


def reload_addon(debug=False):
    for folder in get_immediate_subfolders(addon.path()):
        modules = import_modules(folder, debug=True)
        for module in modules:
            importlib.reload(module)

            if debug: 
                print(f'Reloaded: {module.__name__}')


def get_module_classes(module):
    return [(name, obj) for name, obj in inspect.getmembers(module) if inspect.isclass(obj)]


def get_module_class_names(module):
    return [name for name, obj in inspect.getmembers(module) if inspect.isclass(obj)]