version = (3, 0, 1)

import bpy
import bmesh


def any_elements_selected(context) -> bool:
	objects = context.objects_in_mode
	selection = sum(obj.data.total_vert_sel for obj in objects)

	return bool(selection)


def set_property_percent(self, context) -> None:
	c = self.cuts - 1
	self.width_percent = c / (c + 2) * 100


class MESH_OT_armored_connect(bpy.types.Operator):
	'''Connects the selected components with the specified number of edges.

	armoredColony.com '''

	bl_idname = 'mesh.armored_connect'
	bl_label = 'ARMORED Connect'
	bl_options = {'REGISTER', 'UNDO', 'PRESET'}

	cuts: bpy.props.IntProperty(
		name='Cuts', default=1, min=1, max=24, update=set_property_percent)
	
	width_percent: bpy.props.FloatProperty(
		name='Width Percent', default=0, min=0, max=100, step=100)
	
	grid_fill: bpy.props.BoolProperty(
		name='Grid Fill', default=True, description='Affects intersecting face loops')

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		col = layout.column(align=True)
		col.separator()

		col.prop(self, 'cuts')

		sub = col.row()
		sub.prop(self, 'width_percent')
		sub.enabled = self.cuts > 1 
		col.separator()

		col.prop(self, 'grid_fill')
		col.separator()

		col.operator("wm.operator_defaults")

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'

	def execute(self, context):

		if not any_elements_selected(context):
			bpy.ops.mesh.knife_tool('INVOKE_DEFAULT')
			return {'FINISHED'}

		ob = context.edit_object
		me = ob.data
		bm = bmesh.from_edit_mesh(me)

		vert_mode, edge_mode, face_mode = context.tool_settings.mesh_select_mode

		if vert_mode:
			
			selected_verts = self._get_selected_verts(bm)

			if len(selected_verts) == 1:
				bpy.ops.mesh.knife_tool('INVOKE_DEFAULT')
				return {'FINISHED'}

			elif len(selected_verts) > 1:
				try:
					bpy.ops.mesh.vert_connect_path()  
				except Exception:
					bpy.ops.mesh.vert_connect()  
				return {'FINISHED'}


		if edge_mode:

			selected_edges = self._get_selected_edges(bm)
			self._select_set(selected_edges, False)

			if len(selected_edges) == 1:
				bevel_mode = 'VERTICES'
				# self.cuts = 1	# Let the user decide.
			else:
				bevel_mode = 'EDGES'

			# I JUST ASSUME THE USER SELECTED AN EDGE RING.
			cuts = self._connect_edge_ring(bm, edges=list(selected_edges), cuts=self.cuts, bevel_mode=bevel_mode)
			self._select_set(cuts, True)

			if bevel_mode == 'VERTICES':
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

			bmesh.update_edit_mesh(me)

			return {'FINISHED'}

			
		if face_mode:
			
			selected_faces = self._get_selected_faces(bm)
			selected_edges = self._get_selected_edges(bm)
			# ... DO NOT DESELECT ANYTHING YET.
			
			# CONVERT OUT SELECTION OF FACES INTO AN EDGE RING.
			border_edges = self._get_selection_border_edges(selected_edges)
			contained_edges = selected_edges - border_edges

			# WE LOSE 2 EDGES BECAUSE OF THE BORDER EDGE SUBSTRACTION
			# THIS IS PROBABLY SUB-OPTIMAL BUT IT WORKS TO GET THEM BACK.
			self._select_set(selected_faces, False)
			self._select_set(selected_edges, False)
			self._select_set(contained_edges, True)

			linked_faces = set()
			missing_edges = set()
			for e in contained_edges:
				for f in e.link_faces:
					linked_faces.add(f)
				# linked_faces.union(set(e.link_faces))	# THIS DOES NOT WORK FOR SOME REASON.
			
			for f in linked_faces:
				for e in f.edges:
					if not e.verts[0].select and not e.verts[1].select:
						missing_edges.add(e)
			
			edge_ring_to_connect = contained_edges.union(missing_edges)
			self._select_set(contained_edges, False)

			# NOW WE CAN CONNECT THE EDGE RING.
			cuts = self._connect_edge_ring(bm, edges=list(edge_ring_to_connect), cuts=self.cuts)
			self._select_set(cuts, True)

			bmesh.update_edit_mesh(me)

			return {'FINISHED'}

		return {'FINISHED'}	# JUST IN CASE.


	# MAIN CONNECT METHOD >>

	def _connect_edge_ring(self, bm: bmesh.types.BMesh, edges: bmesh.types.BMEdgeSeq, cuts: int, bevel_mode='EDGES') -> bmesh.types.BMElemSeq:
		'''
		Connects the input edge ring(s) with the specified amount of edge loops ('Cuts' in Blender lingo).
		Supports both open and closed edge rings.
		Supports multiple, unconnected edge rings.

		RETURNS: 
			BMEdgeSeq to be selected.
		'''

		# WE CREATE A SINGLE CUT WITH SUBDIVIDE BECAUSE IT DOES NOT HAVE
		# ANY SPACING PARAMETER WE CAN USE FOR THE NEW CUTS.
		subdivided_edges = bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=self.grid_fill)

		if cuts == 1:
			# THIS ONLY FIXES THE OUTPUT FROM PERPENDICULAR FACE LOOP SELECTIONS, BUT I'M A PERFECTIONIST SO HERE IT IS.
			bad_faces = {elem for elem in subdivided_edges['geom_inner'] if isinstance(elem, bmesh.types.BMFace)}

			return set(subdivided_edges['geom_inner']).difference(bad_faces)

		# IF WE NEED MULTIPLE CUTS...
		# WE RELY ON THE BEVEL OPERATOR TO ADD MORE CUTS AND LET THE 
		# USER CONTROL THE SPACING BY MODIFYING THE PERCENT ARGUMENT.
		beveled_edges = bmesh.ops.bevel(
			bm,
			segments=cuts-1,
			offset_type='PERCENT', 
			offset=self.width_percent,
			geom=subdivided_edges['geom_inner'], 
			loop_slide=True, 
			clamp_overlap=True, 
			affect=bevel_mode)

		if bevel_mode == 'EDGES':
			return beveled_edges['faces']
		
		else:
			return beveled_edges['verts']


	# SELECTION GETTERS >>

	def _get_selected_verts(self, bm: bmesh.types.BMesh) -> set[bmesh.types.BMVertSeq]:
		return {v for v in bm.verts if v.select}
	
	def _get_selected_edges(self, bm: bmesh.types.BMesh) -> set[bmesh.types.BMEdgeSeq]:
		return {e for e in bm.edges if e.select}
	
	def _get_selected_faces(self, bm: bmesh.types.BMesh) -> set[bmesh.types.BMFaceSeq]:
		return {f for f in bm.faces if f.select}
	
	def _get_selection_border_edges(self, selected_edges) -> set[bmesh.types.BMEdgeSeq]:
		'''
		Requires edges to be selected for accurate results.
		'''

		return {e for e in selected_edges if (e.is_boundary or not all(f.select for f in e.link_faces))}
	

	# SELECTION SETTERS >>

	def _select_set(self, elements: list[bmesh.types.BMElemSeq], state: bool) -> None:
		for e in elements:
			e.select = state


classes = (
	MESH_OT_armored_connect,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
