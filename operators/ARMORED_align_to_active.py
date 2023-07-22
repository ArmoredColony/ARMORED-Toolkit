version = (1, 1, 0)

import bpy
import bmesh
import mathutils

import itertools
from typing import Union


class MESH_OT_armored_align_to_active(bpy.types.Operator):
	'''Align the selected vertices to the active vertex (must click to select, box selecting does NOT work).

armoredColony.com '''

	bl_idname = 'mesh.armored_align_to_active'
	bl_label = 'ARMORED Align to active'
	bl_options = {'REGISTER', 'UNDO'}

	axis: bpy.props.EnumProperty(
		name='Axis', default={'X'}, 
		description='Flatten selection to',
		options={'ENUM_FLAG'},
		items=[ 
			('X', 'X', ''), 
			('Y', 'Y', ''), 
			('Z', 'Z', ''), 
			])
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		row = layout.row()
		row.prop(self, 'axis', expand=True)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		ob = context.edit_object
		me = ob.data
		bm = bmesh.from_edit_mesh(me)

		active = self._get_active_vert(bm)
		sel_verts = {v for v in bm.verts if v.select}
		
		if active is None:
			target_coords = self._get_average_coords(sel_verts)
		else:
			sel_verts.remove(active)
			target_coords = active.co
		

		for v, axis in itertools.product(sel_verts, self.axis):
			setattr(v.co, axis.lower(), getattr(target_coords, axis.lower()))

		bmesh.update_edit_mesh(me)
		return {'FINISHED'}


	def _get_active_vert(self, bm) -> Union[bmesh.types.BMVert, None]:
		if bm.select_history:
			elem = bm.select_history[-1]
			if isinstance(elem, bmesh.types.BMVert):
				return elem
		return None
	
	def _get_average_coords(self, verts: bmesh.types.BMVertSeq) -> mathutils.Vector:
		return sum((v.co for v in verts), mathutils.Vector()) / len(verts)

classes = (
	MESH_OT_armored_align_to_active,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)