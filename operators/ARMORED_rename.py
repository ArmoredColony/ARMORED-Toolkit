version = (1, 0, 1)

import bpy
import string


def rename_objects(objects: list[bpy.types.Object], base_string: str, start_int: int, digits: int) -> None:
	'''
	Renames the objects and their data blocks.
	'''

	for i, obj in enumerate(objects):
		obj.name = f'{base_string}{i + start_int:0{digits}d}'
		

		if not obj.data or obj.data.users > 1:
			print(f'ARMORED_Toolkit: Object {obj.name} has no data block or is linked to other objects.')
			continue

		obj.data.name = obj.name


class OBJECT_OT_armored_rename(bpy.types.Operator):
	'''Rename the selected objects.

	armoredColony.com '''

	bl_idname = 'object.armored_rename'
	bl_label = 'ARMORED Rename'
	bl_options = {'REGISTER', 'UNDO'}

	base_string: bpy.props.StringProperty(
		name='Base String', default='Object_A')
	
	start_from: bpy.props.IntProperty(
		name='Start from', default=1)
	
	digits: bpy.props.IntProperty(
		name='Digits', default=2, min=1, max=10)
	
	sort_mode: bpy.props.EnumProperty(
		name='Sort By',
		default='DIMENSIONS',
		items=[
			('NAME', 'Name', 'Sort by name'),
			('VERTEX_COUNT', 'Vertex Count', 'Sort by vertex count'),
			('DIMENSIONS', 'Dimensions', 'Sort by dimensions'), ])

	def invoke(self, context, event):
		# letters = string.ascii_uppercase
		# index = letters.index(self.base_string[-1])
		# next_char = letters[index + 1]
		# self.base_string = self.base_string[:-1] + next_char

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		objects_to_rename = context.selected_objects

		# Give the objects temporary names to avoid name conflicts.
		for obj in objects_to_rename:
			obj.name = 'temp_name'
			obj.data.name = obj.name
		
		if self.digits < len(str(len(objects_to_rename))):
			self.report({'INFO'}, '<Digits> was too small for the amount of objects selected. It was automatically increased.')
			self.digits = len(str(len(objects_to_rename)))

		if self.sort_mode == 'VERTEX_COUNT':
			objects_to_rename = sorted(objects_to_rename, key=lambda obj: len(obj.data.vertices))

		# Largest to Smallest.
		elif self.sort_mode == 'DIMENSIONS':
			objects_to_rename = reversed(sorted(objects_to_rename, key=lambda obj: obj.dimensions))

		rename_objects(objects_to_rename, self.base_string, self.start_from, self.digits)
		
		return {'FINISHED'}


classes = (
	OBJECT_OT_armored_rename,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)