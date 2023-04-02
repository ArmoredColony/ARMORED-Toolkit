version = (1, 0, 0)

import bpy


class OBJECT_OT_armored_camera_from_view(bpy.types.Operator):
	'''Create a Camera based on the current view.

	armoredColony.com '''

	bl_idname = 'object.armored_camera_from_view'
	bl_label = 'ARMORED Camera from View'
	bl_options = {'REGISTER', 'UNDO'}

	# @classmethod
	# def poll(cls, context):
		# return context.active_object is not None

	def execute(self, context):
		context.scene.camera = self._add_camera(context)
		self._align_camera_to_view(context)

		return {'FINISHED'}
	

	# PRIVATE METHODS

	def _add_camera(self, context):
		# Create a new camera object
		camera_data = bpy.data.cameras.new(name='Camera')
		camera_object = bpy.data.objects.new(name='Camera', object_data=camera_data)
		
		# Link the camera to the scene
		context.scene.collection.objects.link(camera_object)
		
		# Make the camera active
		context.view_layer.objects.active = camera_object
		camera_object.select_set(True)
		
		return camera_object

	def _align_camera_to_view(self, context):
		window = context.window
		areas = [area for area in window.screen.areas if area.type == 'VIEW_3D']
		region = [region for region in areas[0].regions if region.type == 'WINDOW']

		with context.temp_override(window=window, area=areas[0], region=region[0]):
			bpy.ops.view3d.camera_to_view()
		
		context.space_data.lock_camera = True


classes = (
	OBJECT_OT_armored_camera_from_view,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)