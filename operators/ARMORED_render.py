version = (2, 0, 1)

import bpy
import pathlib
import os


# Probably does NOT work if you move your desktop folder.
default_path = str(pathlib.Path.home() / 'Desktop')


class RENDER_OT_armored_render(bpy.types.Operator):
	'''Render selected/all cameras.

	armoredColony.com '''

	bl_idname = 'render.armored_render'
	bl_label = 'ARMORED Render'
	bl_options = {'REGISTER', 'UNDO'}

	render_mode: bpy.props.EnumProperty(
		name='Render Camera',
		default='ALL',
		items=[
			('SCENE',    'Scene',    'Render the current scene camera (numpad 0).'),
			('SELECTED', 'Selected', 'Render the selected cameras.'),
			('ALL',      'All',      'Render all cameras in the scene.'),
		],
	)
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		
		col = layout.column(align=True)

		row = col.row(align=True)
		row.prop(self, 'render_mode', expand=True)
		col.separator()

	def invoke(self, context, event):
		try:
			self.render_path = self._get_path_from_addon(context)

		except Exception as e:
			print(e)
			print(f'Could not get path from ARMORED-Toolkit, using default path \'{default_path}\'')
			self.render_path = default_path

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		camera_objects = self._get_cameras_to_render(context, self.render_mode)

		if not camera_objects:
			self.report({'WARNING'}, 'No Cameras Found!')
			return {'CANCELLED'}

		for camera in camera_objects:
			context.scene.camera = camera
			
			file_path = os.path.join(self.render_path, camera.name)
			context.scene.render.filepath = file_path
			
			bpy.ops.render.render(write_still=True)

		self.report({'INFO'}, 'Rendering Complete!')

		return {'FINISHED'}
	

	# PRIVATE METHODS  __________________________________________________

	def _get_path_from_addon(self, context):
		armored_toolkit = context.preferences.addons['ARMORED-Toolkit']
		props = armored_toolkit.preferences

		return getattr(props, 'render_path')

	def _get_cameras_to_render(self, context, render_mode) -> list[bpy.types.Camera]:
		if render_mode == 'SCENE':
			return [context.scene.camera]

		if render_mode == 'SELECTED':
			return [obj for obj in context.selected_objects if obj.type == 'CAMERA']

		return [obj for obj in context.scene.objects if obj.type == 'CAMERA']


classes = (
	RENDER_OT_armored_render,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)