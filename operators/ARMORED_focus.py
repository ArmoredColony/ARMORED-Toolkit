# v3.1

import bpy
from bpy.types import Operator
from bpy_extras import view3d_utils


class Focus:
	'''Provides different view_selected methods for different context modes.'''

	bl_label = 'ARMORED Focus'
	bl_options = {'REGISTER'}

	# def execute(self, context):
	# 	print('\nRan Execute\n')
	# 	return self.invoke(context, event=None) 

	def invoke(self, context, event):
		mode = context.mode

		if mode == 'OBJECT':
			self.object_focus(context)
		
		elif mode == 'EDIT_MESH':
			self.edit_mesh_focus(context)
		
		elif mode == 'SCULPT':
			self.sculpting_focus(context, event)
		
		return {'FINISHED'}


	def object_focus(self, context):
		if context.selected_objects:
			bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
			return

		bpy.ops.view3d.view_all('INVOKE_DEFAULT')

	def edit_mesh_focus(self, context):
		obj = context.edit_object
		selection = obj.data.total_vert_sel
		
		if not selection: 
			bpy.ops.mesh.select_all(action='SELECT')

		bpy.ops.view3d.view_selected('INVOKE_DEFAULT')

		if not selection: 
			bpy.ops.mesh.select_all(action='DESELECT')

	def sculpting_focus(self, context, event):
		if self._in_local_view(context):
			bpy.ops.view3d.view_all('INVOKE_DEFAULT')
			return
		
		bpy.ops.view3d.localview('INVOKE_DEFAULT', frame_selected=False)
		bpy.ops.view3d.view_all('INVOKE_DEFAULT')
		bpy.ops.view3d.localview('INVOKE_DEFAULT', frame_selected=False)
		
		# if self._raycast_hit(context, event):
		# 	bpy.ops.view3d.localview('INVOKE_DEFAULT', frame_selected=False)
		# 	bpy.ops.view3d.view_all('INVOKE_DEFAULT')
		# 	bpy.ops.view3d.localview('INVOKE_DEFAULT', frame_selected=False)
		# 	return

		# bpy.ops.view3d.view_all('INVOKE_DEFAULT')
	
	def _in_local_view(self, context):
		return bool(context.space_data.local_view)
	
	def _raycast_hit(self, context, event):
		scene = context.scene
		region = context.region
		rv3d = context.region_data
		coord = event.mouse_region_x, event.mouse_region_y

		depsgraph = context.evaluated_depsgraph_get()
		# view_layer = context.view_layer # for older blenders

		# get the ray from the viewport and mouse
		direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
		origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

		result, location, normal, index, obj, matrix = scene.ray_cast(depsgraph, origin, direction)

		return result


class MESH_OT_armored_focus(Operator, Focus):
	'''Provides additional functionality to the view_selected operator.

armoredColony.com '''

	bl_idname = 'mesh.armored_focus'

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'


class VIEW_OT_armored_focus(Operator, Focus):
	'''Provides additional functionality to the view_selected operator.

armoredColony.com '''
	
	bl_idname = 'view3d.armored_focus'

	@classmethod
	def poll(cls, context):
		return context.mode != 'EDIT_MESH'
	
	
classes = (
	VIEW_OT_armored_focus,
	MESH_OT_armored_focus,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)