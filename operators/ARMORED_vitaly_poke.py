# v2.0

import bpy
import bmesh
from bpy.props import EnumProperty


class ARMORED_OT_vitaly_poke(bpy.types.Operator):
	'''Converts a selection of quads into a diamond pattern by using the poke operator and some weird code.

(www.armoredColony.com)'''

	bl_idname = 'mesh.armored_vitaly_poke'
	bl_label = 'ARMORED Vitaly Poke'
	bl_options = {'REGISTER', 'UNDO'}

	deselect : EnumProperty(name='Deselect', default='NONE',
	items=[ ('NONE',          'None',          'Deselect Nothing'), 
		('CORNERS',       'Corners',       'Deselect Corner Triangles'),
		('ALL_TRIANGLES', 'All Triangles', 'Deselect All Triangles'),   ])

	def draw(self, context):
		layout = self.layout
		layout.label(text='Deselect:')
		row = layout.row()
		row.prop(self, 'deselect', expand=True)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None
	
	def execute(self, context):
		ob = context.edit_object
		me = ob.data
		bm = bmesh.from_edit_mesh(me)

		sel_faces = (f for f in bm.faces if f.select)
		sel_edges = {e for e in bm.edges if e.select}
		border_edges = {e for e in sel_edges
			if (e.is_boundary or not all(f.select for f in e.link_faces))}

		poked = bmesh.ops.poke(bm, faces=list(sel_faces))
		for f in poked['faces']:
			f.select = True

		dissolve_edges = sel_edges - border_edges
		bmesh.ops.dissolve_edges(bm, edges=list(dissolve_edges))

		bm.select_mode = {'VERT'}
		bm.select_flush_mode()

		if self.deselect == 'CORNERS':
			self._deselect_corners(bm)
			
		elif self.deselect == 'ALL_TRIANGLES':
			self._deselect_all_triangles(bm)

		bm.select_flush_mode()
		bm.select_mode = {'FACE'}	# DO NOT REMOVE THIS LINE OR SHIT BREAKS!!!
		bmesh.update_edit_mesh(me)
		return {'FINISHED'}
	

	def _deselect_corners(self, bm):
		sel_verts = (v for v in bm.verts if v.select)
		corner_verts = (v for v in sel_verts if len([e for e in v.link_edges if e.select]) == 3)
		for v in corner_verts:
			v.select = False

	def _deselect_all_triangles(self, bm):
		bm.select_mode = {'FACE'}	# for later flushing.
		triangles = (f for f in bm.faces if f.select and len(f.verts) == 3)
		for f in triangles:
			f.select = False


classes = (
	ARMORED_OT_vitaly_poke,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)