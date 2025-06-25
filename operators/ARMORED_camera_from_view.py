version = (2, 0, 0)

import bpy


class OBJECT_OT_armored_camera_from_view(bpy.types.Operator):
	'''Create a new camera and align it to viewport or simply align a selected camera.

	armoredColony.com '''

	bl_idname = 'object.armored_camera_from_view'
	bl_label = 'ARMORED Camera from View'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		cameras = [obj for obj in context.selected_objects if obj.type == 'CAMERA']

		if not cameras:
			bpy.ops.object.camera_add(align='VIEW')
			bpy.ops.view3d.camera_to_view()
		
		for camera in cameras:
			context.scene.camera = camera
			bpy.ops.view3d.camera_to_view()
			bpy.ops.view3d.view_camera()
		# bpy.ops.view3d.camera_to_view()

		return {'FINISHED'}

classes = (
	OBJECT_OT_armored_camera_from_view,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)