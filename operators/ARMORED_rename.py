version = (1, 2, 0)

import bpy
# import string


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


class OBJECT_OT_armored_rename_objects(bpy.types.Operator):
	'''Rename the selected objects.

	armoredColony.com '''

	bl_idname = 'object.armored_rename_objects'
	bl_label = 'ARMORED Rename Objects'
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

		# Give the objects temporary names first to avoid name conflicts.
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


class OBJECT_OT_armored_rename_data(bpy.types.Operator):
	'''Rename the data to match the name of the selected objects.

	armoredColony.com '''

	bl_idname = 'object.armored_rename_data'
	bl_label = 'ARMORED Rename Data'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		selected_objects = context.selected_objects

		objects_to_rename = [obj for obj in selected_objects if obj.type != 'EMPTY' and obj.data.name != obj.name]

		if not objects_to_rename:
			self.report({'INFO'}, 'Nothing needed renaming')
			return {'CANCELLED'}

		for obj in objects_to_rename:
			print(f'Renaming {obj}')

		# Give the data temporary names first to avoid name conflicts.
		for obj in objects_to_rename:
			obj.data.name = 'temp_name'
		
		for obj in objects_to_rename:
			print(f'Renaming Data of \'{obj.name}\'')
			obj.data.name = obj.name
		
		# Check again for any objects that were NOT renamed.
		objects_to_rename = [obj for obj in selected_objects if obj.type != 'EMPTY' and obj.data.name != obj.name]

		if objects_to_rename:
			self.report({'ERROR'}, 'Failed to rename. Check for unused Data-Blocks holding the required name')
			print('Failed to rename the following Objects. Check for unused Data-Blocks holding the required name:')
			for obj in objects_to_rename:
				print(obj.name)
		
		else:
			self.report({'INFO'}, 'Renaming Completed without Errors')

		return {'FINISHED'}


classes = (
	OBJECT_OT_armored_rename_objects,
	OBJECT_OT_armored_rename_data,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)