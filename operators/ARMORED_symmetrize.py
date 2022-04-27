import bpy
import bmesh
from bpy.props import EnumProperty

from contextlib import suppress

from typing import TypeVar, Union
BMVertSeq = TypeVar('BMVertSeq')
BMEdgeSeq = TypeVar('BMEdgeSeq')
BMFaceSeq = TypeVar('BMFaceSeq')


class MESH_OT_armored_symmetrize(bpy.types.Operator):
	'''Bisects and Symmetrizes the entire mesh geometry across the specifiec world axis.

armoredColony.com '''

	bl_idname = 'mesh.armored_symmetrize'
	bl_label = 'ARMORED Symmetrize'
	bl_options = {'REGISTER', 'UNDO'}

	axis: EnumProperty(
		name='Axis', default='POSITIVE_X', 
		description='Symmetry Axis',
		items=[ 
			('POSITIVE_X', '+X', 'Positive X to Negative X.'), 
			('POSITIVE_Y', '+Y', 'Positive Y to Negative Y.'), 
			('POSITIVE_Z', '+Z', 'Positive Z to Negative Z.'), 

			('NEGATIVE_X', '-X', 'Negative X to Positive X.'), 
			('NEGATIVE_Y', '-Y', 'Negative Y to Positive Y.'), 
			('NEGATIVE_Z', '-Z', 'Negative Z to Positive Z.'), 
			])
	
	def draw(self, context):
		layout = self.layout
		layout.label(text='Global Axis')
		row = layout.row()
		row.prop(self, 'axis', expand=True)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		ob = context.edit_object
		me = ob.data
		bm = bmesh.from_edit_mesh(me)

		mode = context.tool_settings.mesh_select_mode

		sel_verts = [v for v in bm.verts if v.select]

		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.symmetrize(direction=self.axis)
		bpy.ops.mesh.select_all(action='DESELECT')

		for v in sel_verts:
			with suppress(Exception):
				v.select = True

		bm.select_mode = {'VERT'}
		bm.select_flush_mode()
		return {'FINISHED'}


classes = (
	MESH_OT_armored_symmetrize,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)