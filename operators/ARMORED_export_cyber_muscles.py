import bpy
import os
# import pprint


DIR_PATH_OBJ = 'D:\\Desktop\\DESIGN\\KITBASH\\Muscles\\Cyber Muscles\\UPLOAD\\OBJ'
DIR_PATH_FBX = 'D:\\Desktop\\DESIGN\\KITBASH\\Muscles\\Cyber Muscles\\UPLOAD\\FBX'


def deselect_all():
	bpy.ops.object.select_all(action='DESELECT')


def select_objects(objects):
	for obj in objects:
		try:
			obj.select_set(True)
		except ReferenceError:
			pass

def join_objects_similar_name(context) -> list[bpy.types.Object]:
	# selected_objects = [obj for obj in context.selected_objects[:] if obj.type == 'MESH']
	selected_objects = context.selected_objects[:]
		
	max_characters = len('CM01_A')
	names = set(obj.name[:max_characters] for obj in selected_objects)
	
	groups_of_objects_with_similar_name = []

	for name in names:
		objects_with_similar_name = [obj for obj in selected_objects if obj.name.startswith(name)]
		
		if len(objects_with_similar_name) > 1:
			groups_of_objects_with_similar_name.append(
				list(reversed(sorted(objects_with_similar_name, key=lambda obj: obj.dimensions)))		# Biggest Object First
				)
	
	unsorted_objects = []
	for objects_with_similar_name in groups_of_objects_with_similar_name:
		bpy.ops.object.select_all(action='DESELECT')
		
		context.view_layer.objects.active = objects_with_similar_name[0]
		#print(f'objects_with_similar_name {map(lambda obj: obj.name, objects_with_similar_name)}')

		for obj in objects_with_similar_name:
			obj.select_set(True)
                        
		bpy.ops.object.join()
		# print(f'Joined into {objects_with_similar_name[0].name}')
		unsorted_objects.append(objects_with_similar_name[0])

	sorted_objects = sorted(unsorted_objects, key=lambda obj: obj.name)

	# print('Joind Objects:')
	# pprint.pprint(list(
	# 	map(lambda obj: obj.name, sorted_objects)
	# 	))

	return sorted_objects
	
def replace_letter_in_obj(file_path):
	'''
	Replace all instances of 'o' with 'g' in the OBJ file (Maya prefers Groups?)
	'''

	# Read the contents of the OBJ file
	with open(file_path, 'r') as file:
		obj_contents = file.read()

	# Replace all instances of 'o' with 'g'
	replaced_contents = obj_contents.replace('o C', 'g C') # This way we only replace the 3D obects that start with 'C' and not every 'g' in the file.

	# Write the modified contents back to the OBJ file
	with open(file_path, 'w') as file:
		file.write(replaced_contents)


class OBJECT_OT_armored_export_cyber_muscles(bpy.types.Operator):
	'''DEV ONLY - Personal script to export my Cyber Muscles Pack whenever I.make changes to it.

	armoredColony.com '''

	bl_idname = 'object.armored_export_cyber_muscles'
	bl_label = 'ARMORED Export Cyber Muscles'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):

		self._set_materials_to_lighter_colors()

		self.cyber_muscles_straight = [obj for obj in context.scene.objects 
			    if obj.name.startswith('CM') and not obj.name.endswith('.001')]
		
		self.cyber_muscles_curved = [obj for obj in context.scene.objects 
			    if obj.name.startswith('CM') and obj.name.endswith('.001')]
		
		self.cyber_muscle_connectors = [obj for obj in context.scene.objects if obj.name.startswith('C') and len(obj.name) == 3]

		# EXPORT OBJ
		deselect_all()
		self._select_everything_to_export()
		self._export_obj(file_name='Cyber Muscles', dir_path=DIR_PATH_OBJ, material_split=False)

		# JOIN OBJECTS WITH SIMILAR NAMES (CONNECTORS WITH THEIR MUSCLES).
		# JOIN THE STRAIGHT MUSCLES
		deselect_all()
		select_objects(self.cyber_muscles_straight)
		context.view_layer.objects.active = self.cyber_muscles_straight[0]
		bpy.ops.object.convert(target='MESH')	# VISUAL GEO TO MESH
		self.cyber_muscles_straight.extend(join_objects_similar_name(context))

		# JOIN THE CURVED MUSCLES
		deselect_all()
		select_objects(self.cyber_muscles_curved)
		context.view_layer.objects.active = self.cyber_muscles_curved[0]
		bpy.ops.object.convert(target='MESH')	# VISUAL GEO TO MESH
		self.cyber_muscles_curved.extend(join_objects_similar_name(context))

		# EXPORT OBJ MATERIAL SPLIT
		self._select_everything_to_export()
		self._export_obj(file_name='Cyber Muscles Material Split', dir_path=DIR_PATH_OBJ, material_split=True)


		########################
		# BEGIN FBX EXPORT

		# IMPORT OBJ
		self._clear_file_data()
		self._import_obj(file_name='Cyber Muscles', split_objects=True)

		# EXPORT FBX
		bpy.ops.object.select_all(action='SELECT')
		self._export_fbx(file_name='Cyber Muscles', dir_path=DIR_PATH_FBX)

		# IMPORT OBJ MATERIAL SPLIT
		self._clear_file_data()
		self._import_obj(file_name='Cyber Muscles Material Split', split_groups=True)
		
		# EXPORT FBX MATERIAL SPLIT
		bpy.ops.object.select_all(action='SELECT')
		self._export_fbx(file_name='Cyber Muscles Material Split', dir_path=DIR_PATH_FBX)

		# EDIT THE OBJ A LITTLE FOR MAYA.
		replace_letter_in_obj(
			file_path='D:\\Desktop\\DESIGN\\KITBASH\\Muscles\\Cyber Muscles\\UPLOAD\\OBJ\\Cyber Muscles.obj')
		
		return {'FINISHED'}


	# PRIVATE METHODS >>

	def _set_materials_to_lighter_colors(self) -> None:
		bpy.data.materials["Primary"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = [0.207916, 0.207916, 0.207916, 1.000000]
		bpy.data.materials["Secondary"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = [0.384375, 0.384375, 0.384375, 1.000000]
		bpy.data.materials["Tertiary"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = [0.137584, 0.137584, 0.137584, 1.000000]
		bpy.data.materials["Metal"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = [1.000000, 1.000000, 1.000000, 1.000000]
	
	def _select_everything_to_export(self) -> None:
		select_objects(self.cyber_muscles_straight)
		select_objects(self.cyber_muscles_curved)
		select_objects(self.cyber_muscle_connectors)

	def _export_obj(self, file_name: str, dir_path: str, material_split=False) -> None:
		bpy.ops.object.armored_export_obj(
			file_name=file_name,
			dir_path_override=dir_path,
			material_split=material_split,
			)

	def _export_fbx(self, file_name: str, dir_path: str) -> None:
		bpy.ops.object.armored_export_fbx(
			file_name=file_name,
			dir_path_override=dir_path,
			)

	def _import_obj(self, file_name, split_objects=False, split_groups=False) -> None:
		bpy.ops.wm.obj_import(
			filepath=os.path.join(DIR_PATH_OBJ, f'{file_name}.obj'),
			use_split_objects=split_objects, 
			use_split_groups=split_groups)
		
	def _clear_file_data(self) -> None:
		'''
		Delete all the relevant data as an alternative to loading a new file
		'''

		for mesh in bpy.data.meshes:
			bpy.data.meshes.remove(mesh)

		for curve in bpy.data.curves:	# Includes Text Objects
			bpy.data.curves.remove(curve)
		
		for lattice in bpy.data.lattices:
			bpy.data.lattices.remove(lattice)
		
		for material in bpy.data.materials:
			bpy.data.materials.remove(material)
		
		for camera in bpy.data.cameras:
			bpy.data.cameras.remove(camera)

		
classes = (
	OBJECT_OT_armored_export_cyber_muscles,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)