# v2.0

import bpy
import bmesh
from bpy.props import FloatProperty


class ARMORED_OT_autosmooth(bpy.types.Operator):
	'''Switches between Autosmooth by angle and Flat Shading (ignores any selections that are not Meshes).

www.armoredColony.com '''
	
	bl_idname = 'view3d.armored_autosmooth'
	bl_label = 'ARMORED Autosmooth'
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		return context.object is not None

	def execute(self, context):
		active = context.object
		selected_objects = {ob for ob in context.selected_objects if ob.type == 'MESH'}
		selected_objects.add(active)

		mode = context.mode
		autosmooth = active.data.use_auto_smooth

		if context.mode == 'OBJECT':
			for ob in selected_objects:
				self._object_smooth_set(ob, value=not autosmooth)
				
		elif context.mode in {'EDIT_MESH', 'EDIT_CURVE'}:
			for ob in selected_objects:
				self._bmesh_smooth_set(ob, value=not autosmooth)
		else:
			return {'CANCELLED'}
				
		for ob in selected_objects:
			ob.data.use_auto_smooth = not autosmooth

		return {'FINISHED'}


	def _object_smooth_set(self, object: bpy.types.Object, value: bool) -> None:
		'''
		We do it this way because the bpy.ops requivalent only works on selections 
		and I want the active object to always be affected.
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