version = (4, 1, 0)

import bpy


class Focus():
	'''
	Abstract focus/view_selected class.
	'''

	bl_label = 'ARMORED Focus'
	bl_options = {'REGISTER'}
	bl_description = 'Similar to View Selected but will frame everything if nothing is selected \n\narmoredColony.com '
	poll_mode = NotImplemented

	# The poll isn't strictly needed but it makes it so only one Focus operator will appear in the 
	# search menu (F3) at any given time, based on the context specified in the <poll_mode> attribute.
	@classmethod
	def poll(cls, context):
		if cls.poll_mode is None:
			return True
			
		return context.mode == cls.poll_mode

	def invoke(self, context, event):
		self._focus(context)

		return {'FINISHED'}

	def _focus(self, context):
		raise NotImplementedError
	

class OBJECT_OT_armored_focus(bpy.types.Operator, Focus):
	
	bl_idname = 'object.armored_focus'
	poll_mode = 'OBJECT'

	def _focus(self, context):
		if context.selected_objects:
			bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
			return

		bpy.ops.view3d.view_all('INVOKE_DEFAULT')


class MESH_OT_armored_focus(bpy.types.Operator, Focus):

	bl_idname = 'mesh.armored_focus'
	poll_mode = 'EDIT_MESH'

	def _focus(self, context):
		selection_count = sum(obj.data.total_vert_sel for obj in context.objects_in_mode)

		if not selection_count: 
			bpy.ops.mesh.select_all(action='SELECT')

		bpy.ops.view3d.view_selected('INVOKE_DEFAULT')

		if not selection_count: 
			bpy.ops.mesh.select_all(action='DESELECT')


class LATTICE_OT_armored_focus(bpy.types.Operator, Focus):

	bl_idname = 'lattice.armored_focus'
	poll_mode = 'EDIT_LATTICE'

	def _focus(self, context):
		selection_count = sum(self._get_selected_point_count(obj) for obj in context.objects_in_mode)

		if not selection_count: 
			bpy.ops.lattice.select_all(action='SELECT')

		bpy.ops.view3d.view_selected('INVOKE_DEFAULT')

		if not selection_count: 
			bpy.ops.lattice.select_all(action='DESELECT')
	
	def _get_selected_point_count(self, lattice: bpy.types.Object) -> int:
		points = lattice.data.points

		select_state = [False] * len(points)
		points.foreach_get('select', select_state)

		return sum(select_state)


class CURVE_OT_armored_focus(bpy.types.Operator, Focus):

	bl_idname = 'curve.armored_focus'
	poll_mode = 'EDIT_CURVE'

	def _focus(self, context):
		selection_count = sum(self._get_selected_point_count(curve) for curve in context.objects_in_mode)

		if not selection_count: 
			bpy.ops.curve.select_all(action='SELECT')

		bpy.ops.view3d.view_selected('INVOKE_DEFAULT')

		if not selection_count: 
			bpy.ops.curve.select_all(action='DESELECT')
	
	def _get_selected_point_count(self, curve) -> int:
		selected_points = [
			point for spline in curve.data.splines 
				for point in self._get_spline_points(spline) if self._point_is_selected(spline.type, point)]
		
		return len(selected_points)
	
	def _get_spline_points(self, spline):
		return spline.bezier_points if spline.type =='BEZIER' else spline.points
	
	def _point_is_selected(self, spline_type, point):
		return point.select_control_point if spline_type =='BEZIER' else point.select


class SCULPT_OT_armored_focus(bpy.types.Operator, Focus):
	
	bl_idname = 'sculpt.armored_focus'
	poll_mode = 'SCULPT'
	
	def _focus(self, context):
		if self._in_local_view(context):
			bpy.ops.view3d.view_all('INVOKE_DEFAULT')
			return
		
		bpy.ops.view3d.localview('INVOKE_DEFAULT', frame_selected=False)
		bpy.ops.view3d.view_all('INVOKE_DEFAULT')
		bpy.ops.view3d.localview('INVOKE_DEFAULT', frame_selected=False)
	
	def _in_local_view(self, context):
		return bool(context.space_data.local_view)


class NODE_OT_armored_focus(bpy.types.Operator, Focus):
	
	bl_idname = 'node.armored_focus'

	@classmethod
	def poll(cls, context):
		return context.area.type == 'NODE_EDITOR' and context.active_node is not None


	def _focus(self, context):
		if context.selected_nodes:
			bpy.ops.node.view_selected('INVOKE_DEFAULT')
			return

		bpy.ops.node.view_all('INVOKE_DEFAULT')


class IMAGE_OT_armored_focus(bpy.types.Operator, Focus):
	
	bl_idname = 'image.armored_focus'

	@classmethod
	def poll(cls, context):
		return context.area.type == 'IMAGE_EDITOR'

	def _focus(self, context):
		bpy.ops.image.view_all('INVOKE_DEFAULT', fit_view=True)
	
	
classes = (
	OBJECT_OT_armored_focus,
	MESH_OT_armored_focus,
	LATTICE_OT_armored_focus,
	CURVE_OT_armored_focus,
	SCULPT_OT_armored_focus,
	NODE_OT_armored_focus,
	IMAGE_OT_armored_focus,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)