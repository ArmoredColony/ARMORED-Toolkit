version = (2, 0, 1)

import bpy
import os


export_path = 'D:\Desktop'
export_name = 'temp'       # NOTE: file extension will be added automatically based on the exporter.


class Export:
	'''
	Abstract class for exporting your viewport selection without any prompts in Blender.
	'''
 
	bl_options = {'REGISTER'}
	extension = NotImplemented

	def execute(self, context):
		self._validate_extension()

		if self._nothing_selected(context):
			self._report_nothing_selected()
			return {'CANCELLED'}

		self.export_path = self._validate_path(export_path)
		self.file_path = os.path.join(self.export_path, export_name + self.extension)

		self._run_exporter()
		self._report_finished()

		return {'FINISHED'}
	

	def _run_exporter(self):
		raise NotImplementedError
	

	# VALIDATION >>
	
	def _nothing_selected(self, context):
		return not context.selected_objects

	def _validate_path(self, path):
		return path if os.path.exists(path) else os.path.expanduser("~/Desktop")
	
	def _validate_extension(self):
		if self.extension is NotImplemented:
			raise NotImplementedError(
				'All sub-classes of Export must have the <extension> attribute (example: extension = \'.ext\')')
	

	# ERROR MESSAGES >>

	def _report_nothing_selected(self):
		self.report({'WARNING'}, 'Select the objects you want to export')

	def _report_finished(self):
		self.report({'INFO'}, f'Exported {export_name + self.extension} to {self.export_path}')



class ARMORED_OT_export_OBJ(bpy.types.Operator, Export):
	'''Export selected as OBJ.

www.armoredColony.com '''
 
	bl_idname = 'object.armored_export_obj'
	bl_label = 'ARMORED Export OBJ'
	extension = '.obj'

	def _run_exporter(self):
		bpy.ops.wm.obj_export(
			filepath=self.file_path,
			export_selected_objects=True,
			export_uv=False,
			export_normals=False,
			apply_modifiers=True,
			export_materials=True,
			export_pbr_extensions=True,
			export_object_groups=False,
			export_material_groups=True,
		)


class ARMORED_OT_export_FBX(bpy.types.Operator, Export):
	'''Export selected as FBX.

www.armoredColony.com '''
 
	bl_idname = 'object.armored_export_fbx'
	bl_label = 'ARMORED Export FBX'
	extension = '.fbx'

	def _run_exporter(self):
		bpy.ops.export_scene.fbx(
			filepath=self.file_path, 
			use_selection=True, 
			bake_space_transform=True,
			mesh_smooth_type='FACE',
			bake_anim=True,
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