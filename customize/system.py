import bpy
from bpy.app import handlers

from .. utils import debug


@handlers.persistent
def developer_extras_delay(*args):
    bpy.context.preferences.view.show_developer_ui = True
    print('ARMORED Toolkit: Enabled Developer Extras')


def register():
    handlers.load_post.append(developer_extras_delay)
    debug.msg(f'ARM-TK System: LOAD_POST handlers in buffer:\n  {handlers.load_post[:]}')


def unregister():
    # handlers.load_post.remove(developer_extras_delay)
    return