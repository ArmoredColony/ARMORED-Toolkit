import bpy
import os
import contextlib
import logging

from bpy.app import handlers

from .. utils import addon


@handlers.persistent
def developer_extras_delay(*args):
    bpy.context.preferences.view.show_developer_ui = True
    print('ARMORED Toolkit: Enabled Developer Extras')



# def apply_system_preferences():
#     bpy.context.preferences.view.show_splash = False
#     bpy.context.preferences.view.show_tooltips_python = True
#     # bpy.context.preferences.view.show_developer_ui = True     # Not needed here, force it on all the time
#     # bpy.context.preferences.view.smooth_view = 100
#     bpy.context.preferences.inputs.drag_threshold_mouse = 1
#     bpy.context.preferences.inputs.invert_mouse_zoom = True
#     bpy.context.preferences.edit.undo_steps = 90

#     if addon.debug(): 
#         print('ENABLED Armored Preferences')


# def reset_system_preferences():
#     bpy.context.preferences.view.show_splash = True
#     bpy.context.preferences.view.show_tooltips_python = False
#     # bpy.context.preferences.view.show_developer_ui = False     # Not needed here, force it on all the time
#     # bpy.context.preferences.view.smooth_view = 200
#     bpy.context.preferences.inputs.drag_threshold_mouse = 3
#     bpy.context.preferences.inputs.invert_mouse_zoom = False
#     bpy.context.preferences.edit.undo_steps = 32

#     # handlers.load_post.remove(apply_delay)

#     if addon.debug(): 
#         print('RESET System Preferences.')


def register():
    handlers.load_post.append(developer_extras_delay)

    if addon.debug():
        print(f'ARM-TK System: LOAD_POST handlers in buffer:\n  {handlers.load_post[:]}')


def unregister():
    return
    # if isinstance(bpy.context.space_data, bpy.types.SpacePreferences):
        # from .. operators_internal import ARMORED_load_preferences
        # ARMORED_load_preferences.unload_system_preferences()
        # reset_system_preferences()
        
        # if addon.debug(): 
        #     print('ARM-TK System: Reset System Preferences because addon was Disabled')