import bpy

from .. utils import debug


@bpy.app.handlers.persistent
def developer_extras_delay(*args):
	bpy.context.preferences.view.show_developer_ui = True
	print('ARMORED Toolkit: Enabled Developer Extras')


def register():
	bpy.app.handlers.load_post.append(developer_extras_delay)
	

def unregister():
	bpy.app.handlers.load_post.remove(developer_extras_delay)