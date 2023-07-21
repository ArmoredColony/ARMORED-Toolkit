version = (3, 0, 0)

import bpy
import os
import pathlib


# IF THE ARMORED TOOLKIT IS INSTALLED, YOU CAN NOW CHANGE THE EXPORT PATH IN THE ADDON PREFERENCES.

fallback_path = str(pathlib.Path.home() / 'Desktop')


class Export:
	'''
	Abstract class for exporting your viewport selection without any prompts in Blender.
	'''
 
	bl_options = {'REGISTER', 'UNDO'}
	bl_property = 'export_path'
	extension = NotImplemented

	file_name : bpy.props.StringProperty(
		name='File Name', default='')

	dir_path_override : bpy.props.StringProperty(
		name='File Path', default='', subtype='DIR_PATH', options={'SKIP_SAVE'})

	def invoke(self, context, event):		
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		if self.dir_path_override:
			print('Using override path')
			self.export_path = self.dir_path_override

		else:
			
			try:
				self.export_path = self._get_path_from_addon(context)
				print('Using addon path')

			except Exception as e:
				print(e)
				print(f'Could not get path from ARMORED-Toolkit, using fallback path \'{fallback_path}\'')
				self.export_path = fallback_path
			
			print(f'Export Path is {self.export_path}')

		self._validate_extension()

		if self._nothing_selected(context):
			self._report_nothing_selected()
			return {'CANCELLED'}

		if self._path_does_not_exist(self.export_path):
			self._report_path_does_not_exist()
			return {'CANCELLED'}

		if not self.file_name:
			self.file_name = 'temp'

		self.file_path = os.path.join(self.export_path, self.file_name + self.extension)

		self._run_exporter()
		self._report_finished(context)

		return {'FINISHED'}
	

	def _run_exporter(self):
		raise NotImplementedError
	
	def _get_path_from_addon(self, context):
		armored_toolkit = context.preferences.addons['ARMORED-Toolkit']
		props = armored_toolkit.preferences

		return getattr(props, 'export_path')
	

	# VALIDATION >>
	
	def _nothing_selected(self, context):
		return not context.selected_objects

	def _path_does_not_exist(self, path):
		return not os.path.exists(path)
			
	def _validate_extension(self):
		if self.extension is NotImplemented:
			raise NotImplementedError(
				'All sub-classes of Export must have the <extension> attribute (example: extension = \'.ext\')')
	

	# ERROR MESSAGES >>

	def _report_nothing_selected(self):
		self.report({'WARNING'}, 'Select the objects you want to export')
	
	def _report_path_does_not_exist(self):
		self.report({'ERROR'}, f'Path \'{self.export_path}\' does not exist. Check the <Fast Export> path in the Blender file path preferences.')

	def _report_finished(self, context):
		self.report({'INFO'}, f"Exported '{self.file_name}' to '{self.export_path}'")



class ARMORED_OT_export_OBJ(bpy.types.Operator, Export):
	'''Export selected as OBJ.

	armoredColony.com '''
 
	bl_idname = 'object.armored_export_obj'
	bl_label = 'ARMORED Export OBJ'
	extension = '.obj'

	material_split : bpy.props.BoolProperty(name='Material Split', default=False)

	def _run_exporter(self):
		bpy.ops.wm.obj_export(
			filepath=self.file_path,
			export_selected_objects=True,
			global_scale=1,
			export_uv=False,
			export_normals=False,
			apply_modifiers=True,
			export_materials=True,
			export_pbr_extensions=True,
			# export_object_groups=not self.material_split,
			export_object_groups=False,
			export_material_groups=self.material_split,
		)


class ARMORED_OT_export_FBX(bpy.types.Operator, Export):
	'''Export selected as FBX.

	armoredColony.com '''
 
	bl_idname = 'object.armored_export_fbx'
	bl_label = 'ARMORED Export FBX'
	extension = '.fbx'

	def _run_exporter(self):
		bpy.ops.export_scene.fbx(
			filepath=self.file_path, 
			use_selection=True, 
			# bake_space_transform=True,
			# mesh_smooth_type='FACE',
			bake_anim=False,
			object_types={
				# 'ARMATURE', 
				# 'CAMERA', 
				# 'EMPTY', 
				# 'LIGHT', 
				'MESH', 
				# 'OTHER'
				}
		)


classes = (
	ARMORED_OT_export_OBJ,
	ARMORED_OT_export_FBX,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)