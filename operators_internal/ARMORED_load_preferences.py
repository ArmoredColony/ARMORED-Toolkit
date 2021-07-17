# v1.0

import bpy
import os
from bpy.props import StringProperty

from .. utils import addon



def load_system_preferences(context=bpy.context):
    context.preferences.view.show_splash = False
    context.preferences.view.show_tooltips_python = True
    context.preferences.inputs.drag_threshold_mouse = 1
    context.preferences.inputs.invert_mouse_zoom = True
    context.preferences.edit.undo_steps = 90

    if addon.debug(): 
        print('LOADED Armored Preferences')


def unload_system_preferences(context=bpy.context):
    context.preferences.view.show_splash = True
    context.preferences.view.show_tooltips_python = False
    context.preferences.inputs.drag_threshold_mouse = 3
    context.preferences.inputs.invert_mouse_zoom = False
    context.preferences.edit.undo_steps = 32

    if addon.debug(): 
        print('UNLOADED Armored Preferences')


class ARMORED_OT_load_custom_preferences(bpy.types.Operator):
    bl_idname = 'armored.load_custom_preferences'
    bl_label = 'ARMORED Load Custom Preferences'
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def description(cls, context, event):
        list_description = [
            'Show Splash OFF',
            'Python Tooltips ON',
            'Mouse Drag Threshold 1',
            'Invert Mouse Zoom ON',
            'Undo Steps 90',
        ]
        return 'Loads my custom system preferences\n NOTE: these settings persist even if the addon is disabled:\n' + ' \u2022 ' + ('\n\u2022 '.join(list_description))

    def execute(self, context):
        load_system_preferences(context)
        return {'FINISHED'}


class ARMORED_OT_unload_custom_preferences(bpy.types.Operator):
    bl_idname = 'armored.unload_custom_preferences'
    bl_label = 'ARMORED Unload Custom Preferences'
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def description(cls, context, event):
        list_description = [
            'Show Splash On',
            'Python Tooltips Off',
            'Mouse Drag Threshold 3',
            'Invert Mouse Zoom Off',
            'Undo Steps 32',
        ]
        return 'Set the following preferences back to factory Blender values:\n' + ' \u2022 ' + ('\n\u2022 '.join(list_description))

    def execute(self, context):
        unload_system_preferences(context)
        return {'FINISHED'}


classes = (
    ARMORED_OT_load_custom_preferences,
    ARMORED_OT_unload_custom_preferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)