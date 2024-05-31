version = (2, 1, 2)

import bpy
import bmesh


class ARMORED_OT_autosmooth(bpy.types.Operator):
	'''Switches between Autosmooth by angle and Flat Shading (for Blender 4.0 and below).

	armoredColony.com '''
	
	bl_idname = 'view3d.armored_autosmooth_legacy'
	bl_label = 'ARMORED Autosmooth (Legacy)'
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		return context.object is not None

	def execute(self, context):
		if bpy.app.version >= (4, 1, 0):
			self.report({'ERROR'}, 'This operator only works in Blender 4.0 and below.')
			return {'CANCELLED'}

		active_object = context.object
		selected_objects = {ob for ob in context.selected_objects if ob.type == 'MESH'}

		if active_object.type == 'MESH':
			selected_objects.add(active_object)

		mode = context.mode
		autosmooth = active_object.data.use_auto_smooth

		for ob in selected_objects:
			ob.data.use_auto_smooth = not autosmooth

		if context.mode == 'OBJECT':
			# bpy.ops.object.shade_smooth(use_ob.data.use_auto_smooth)
			for ob in selected_objects:
				self._object_smooth_set(ob, value=True)
				
		elif context.mode in {'EDIT_MESH', 'EDIT_CURVE'}:
			for ob in selected_objects:
				self._bmesh_smooth_set(ob, value=True)
		else:
			return {'CANCELLED'}
				
		# for ob in selected_objects:
		# 	ob.data.use_auto_smooth = not autosmooth

		return {'FINISHED'}


	def _object_smooth_set(self, object: bpy.types.Object, value: bool) -> None:
		'''
		We do it this way because the bpy.ops equivalent only works on selections 
		and I want the active object to also be affected even when unselected.
		'''

		mesh = object.data
		values = [value] * len(mesh.polygons)
		mesh.polygons.foreach_set('use_smooth', values)
		mesh.update()

	def _bmesh_smooth_set(self, object: bpy.types.Object, value: bool) -> None:
		'''
		Bmesh smoothing works best for Edit mode.
		'''

		me = object.data
		bm = bmesh.from_edit_mesh(me)
		for f in bm.faces:
			f.smooth = value
		
		bmesh.update_edit_mesh(me)


classes = (
	ARMORED_OT_autosmooth,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)