# v2.1

import bpy
import bmesh


class ARMORED_OT_vitaly_poke(bpy.types.Operator):
	'''Converts a selection of quads into a diamond pattern (similar to Vitaly Bulgarov's technique).

armoredColony.com '''

	bl_idname = 'mesh.armored_vitaly_poke'
	bl_label = 'ARMORED Vitaly Poke'
	bl_options = {'REGISTER', 'UNDO'}

	deselect : bpy.props.EnumProperty(name='Deselect', default='NONE',
		items=[ ('NONE',          'None',          'Deselect Nothing'), 
			('CORNERS',       'Corners',       'Deselect Corner Triangles'),
			('ALL_TRIANGLES', 'All Triangles', 'Deselect All Triangles'),   
			])

	def draw(self, context):
		layout = self.layout

		layout.label(text='Deselect:')
		row = layout.row()
		row.prop(self, 'deselect', expand=True)
		layout.separator()

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'
	
	def execute(self, context):

		for ob in context.objects_in_mode:

			if not ob.data.total_vert_sel:
				continue

			bm = bmesh.from_edit_mesh(ob.data)

			# WE NEED UNSELECTED FACES TOO FOR SOME FRINGE CASES.

			sel_faces, unsel_faces = [], []
			for f in bm.faces:
				if f.select:
					sel_faces.append(f)
				else:
					unsel_faces.append(f)

			sel_edges = {e for e in bm.edges if e.select}
			border_edges = {e for e in sel_edges
				if (e.is_boundary or not all(f.select for f in e.link_faces))}
			

			# POKE AND DISSOLVE EDGES TO CREATE THE NEW PATTERN.

			poked = bmesh.ops.poke(bm, faces=sel_faces)
			for f in poked['faces']:
				f.select = True

			dissolve_edges = list(sel_edges - border_edges)
			bmesh.ops.dissolve_edges(bm, edges=dissolve_edges)

			bm.select_mode = {'VERT'}
			bm.select_flush_mode()


			# DESELECT BASED ON PROPERTY.

			if self.deselect == 'CORNERS':
				self._deselect_corners(bm)

			elif self.deselect == 'ALL_TRIANGLES':
				self._deselect_all_triangles(bm)

			bm.select_flush(False)


			# THIS DESELECTS ANY EXTRA FACES WE MIGHT GET FROM THE VERTEX SELECT FLUSH.

			for f in unsel_faces:
				f.select = False

			sel_faces = (f for f in bm.faces if f.select)
			face_edges = {e for f in sel_faces for e in f.edges}
			for e in face_edges:
				e.select = True

			bmesh.update_edit_mesh(ob.data)

		return {'FINISHED'}


	# PRIVATE HELPERS

	def _deselect_corners(self, bm):
		sel_verts = (v for v in bm.verts if v.select)
		corner_verts = (v for v in sel_verts if len([e for e in v.link_edges if e.select]) == 3)
		for v in corner_verts:
			v.select = False

	def _deselect_all_triangles(self, bm):
		bm.select_mode = {'FACE'}	# IMPORTANT FOR LATER FLUSHING.
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