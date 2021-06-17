import bpy
import os

# from bpy.app import handlers
# from .. utils.update_preferences import update, get_prefs


# @handlers.persistent
# def apply_theme_delay(*args):
#     print('Calling Apply Function')
#     apply_theme()
#     handlers.load_post.remove(apply_theme_delay)


# @handlers.persistent
# def reset_theme_delay(*args):
#     reset_theme()
#     handlers.load_post.remove(reset_theme_delay)


def apply_theme(filename='armored_colony.xml'):
    from .. utils.update_preferences import get_path

    path = os.path.join(get_path(), 'resources', 'themes', filename)

    bpy.ops.preferences.theme_install(filepath=path, overwrite=True)

    print('LOADED Armored Theme.')


def reset_theme():
     bpy.ops.preferences.reset_default_theme()
     print('RESET Theme to Defaults.')


def register():
    return
    # state = True if preferences().themes == 'ENABLED' else False

    # if state:
    #     handlers.load_post.append(apply_theme_delay)
    # else:
    #     handlers.load_post.append(reset_theme_delay)


def unregister():
    return
    if isinstance(bpy.context.space_data, bpy.types.SpacePreferences):
        print('Reset Theme because addon was Disabled')
        reset_theme()