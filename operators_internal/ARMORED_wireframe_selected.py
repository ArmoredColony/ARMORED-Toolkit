version = (2, 0, 0)

import bpy

from .. utils import (
	addon,
	debug,
)

last_selection = []


def enable_wireframe(objects):
	for obj in objects:
		try:
			obj.show_wire = True
		except:
			pass
	
	# debug.msg('ENABLED Wireframe on Selected')


def disable_wireframe(objects):
	for obj in objects:
		try:
			obj.show_wire = False
		except:
			pass
	
	# debug.msg('DISABLED Wireframe on Selected')


def wireframe_selected_objects(*args):
	'''
	Enable Wireframe on the current selection and disable it
	for the previous selection.
	'''
	
	global last_selection

	if bpy.context.selected_objects != last_selection:

		disable_wireframe(last_selection)
		last_selection = bpy.context.selected_objects
		enable_wireframe(last_selection)


@bpy.app.handlers.persistent
def add_load_post_handler():
	'''
	Add a `load_post` handler that in turn adds a `depsgraph_update_post` handler.
	'''
	
	bpy.app.handlers.load_post.append(add_depsgraph_handler)
	debug.msg('ARMORED_wireframe_selected: Added Load Post Handler.')


def remove_load_post_handler():
	'''
	Attemp to remove the `load_post` handler.
	'''
	
	try:
		bpy.app.handlers.load_post.remove(add_depsgraph_handler)
		debug.msg('ARMORED_wireframe_selected: Removed Load Post Handler.')

	except RuntimeError:
		debug.msg('ARMORED_wireframe_selected: Could not Remove Load Post Handler.')
		pass


@bpy.app.handlers.persistent
def add_depsgraph_handler(*args):
	'''
	Update the `last_selection` global and add a `depsgraph_update_post` that controls
	wireframe visualization.
	'''
	
	global last_selection
	last_selection = bpy.context.selected_objects
	enable_wireframe(last_selection)

	bpy.app.handlers.depsgraph_update_post.append(wireframe_selected_objects)
	debug.msg('ARMORED_wireframe_selected: Added Depsgraph Handler.')



def remove_depsgraph_handler(*args):
	'''
	Update the `last_selection` global and attempt to remove the `depsgraph_update_post` handler.
	'''
	
	global last_selection
	last_selection = bpy.context.selected_objects
	disable_wireframe(last_selection)
	
	try:
		bpy.app.handlers.depsgraph_update_post.remove(wireframe_selected_objects)
		debug.msg('ARMORED_wireframe_selected: Removed Depsgraph Handler')

	except RuntimeError:
		debug.msg('ARMORED_wireframe_selected: Could not Unregister Depsgraph Handler.')

	
# class ARMORED_OT_wireframe_selected(bpy.types.Operator):
# 	bl_idname = 'armored.wireframe_selected'
# 	bl_label = 'ARMORED Wireframe Selected'
# 	bl_options = {'REGISTER', 'INTERNAL'}

# 	def execute(self, context):
# 		objects = context.selected_objects
# 		enable_wireframe(objects)
		
# 		return {'FINISHED'}


def register():
	if addon.prefs().wireframe_selected:
		add_load_post_handler()


def unregister():
	remove_load_post_handler()
	remove_depsgraph_handler()


# import bpy
# print(bpy.app.handlers.load_post[:])
# print(bpy.app.handlers.depsgraph_update_post[:])