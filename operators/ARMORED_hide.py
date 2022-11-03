# v1.0

import bpy


class OBJECT_OT_armored_hide(bpy.types.Operator):
	'''Hides or unhides the selected objects.

armoredColony.com '''

	bl_idname = 'object.armored_hide'
	bl_label = 'ARMORED Hide'
	bl_options = {'REGISTER', 'UNDO'}

	# @classmethod
	# def poll(cls, context):
	# 	return context.active_object is not None

	def execute(self, context):
		scene = context.scene
		selected_objects = context.selected_objects
		
		hidden_objects_prop = scene.get('ARC_hidden_objects', None)
		
		if selected_objects:
			self._hide_objects(selected_objects)
			context.scene['ARC_hidden_objects'] = selected_objects
		
		elif hidden_objects_prop is not None and len(hidden_objects_prop) > 0:
			self._unhide_objects(hidden_objects_prop[:])
			del scene['ARC_hidden_objects']
		
		return {'FINISHED'}
	
	def _hide_objects(self, objects: list[bpy.types.Object]):
		for ob in objects:
			ob.hide_set(True)
		
	def _unhide_objects(self, objects: list[bpy.types.Object]):
		for ob in objects:
			ob.hide_set(False)
			ob.select_set(True)


classes = (
	OBJECT_OT_armored_hide,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)