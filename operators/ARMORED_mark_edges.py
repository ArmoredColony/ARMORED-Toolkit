version = (3, 0, 0)

import bpy
import bmesh
import math


def any_elements_selected(context) -> bool:
	objects = context.objects_in_mode
	selection = sum(obj.data.total_vert_sel for obj in objects)

	return bool(selection)


def get_selection_mode(context):
	return context.tool_settings.mesh_select_mode[:]


class ARMORED_OT_mark_edges(bpy.types.Operator):
	'''Instantly Mark selected edges (will affect the entire mesh if nothing is selected).

	armoredColony.com '''
	
	bl_idname = 'mesh.armored_mark_edges'
	bl_label = 'ARMORED Mark Edges'
	bl_options = {'REGISTER', 'UNDO'}


	action: bpy.props.EnumProperty(
		name='Action', 
		description='Mark or Clear the selection',
		default='MARK',
		items=[
			('MARK',  'Mark',  'Mark the selection'),
			('CLEAR', 'Clear', 'Clear the specified mark'), 
		]
	)

	mark_type: bpy.props.EnumProperty(
		name='Mark as', 
		description='Mark as Crease, Seam or Sharp',
		default='CREASE',
		items=[
			('CREASE',     'Crease',     'Crease'),
			('SEAM',       'UV Seam',    'Mark as UV Seam'),
			('SHARP',      'Sharp',      'Mark as Sharp (shading)'), 
			('SHARP_SEAM', 'Sharp Seam', 'Mark as UV Seam and Sharp'), 
		]
	)

	crease_value: bpy.props.FloatProperty(
		name='Value', default=1.0,
		description='Crease value to apply to the selection',
		min=0, max=1,
		step=0.1,
	)

	edge_limit_method: bpy.props.EnumProperty( 
		name='Limit Method', 
		description='Apply a filter to your selection', 
		default='NONE', 
		items=[ 
			('NONE',   'None',   'All Edges'),
			('BORDER', 'Border', 'The borders of the selection'),
			('ANGLE',  'Angle',  'Edges by angle'),
		]
	)
	
	face_limit_method: bpy.props.EnumProperty( 
		name='Limit Method', 
		description='Apply a filter to your selection', 
		default='BORDER', 
		items=[ 
			('NONE',   'None',   'All Edges'),
			('BORDER', 'Border', 'The borders of the selection'),
			('ANGLE',  'Angle',  'Edges by angle'),
		]
	)
			
	edge_angle: bpy.props.FloatProperty(
		name='Edge Angle', default=30,
		description='Edges over this angle will be marked',
		min=0, max=180,
	)

	include_open_edges: bpy.props.BoolProperty(
		name='Include Open Edges', default=False,
		description='Include the Open Edges of the mesh (edges with only one linked face)',
	)

	deselect_after: bpy.props.BoolProperty(
		name='Deselect after', default=False,
		description='Deselect everything after the operation is finished',
	)
	

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		select_mode = context.tool_settings.mesh_select_mode[:]

		col = layout.column(align=True)

		row = col.row()
		row.prop(self, 'action', expand=True)
		col.separator()

		col.prop(self, 'mark_type')
		col.separator()

		if self.mark_type == 'CREASE':
			col.prop(self, 'crease_value')
			col.separator()

		row = col.row()
		if select_mode[1]:
			row.prop(self, 'edge_limit_method', expand=True)
			if self.edge_limit_method == 'ANGLE':
				col.prop(self, 'edge_angle')
			
		elif select_mode[2]:
			row.prop(self, 'face_limit_method', expand=True)
			if self.face_limit_method == 'ANGLE':
				col.prop(self, 'edge_angle')
			
		col.separator()

		col.prop(self, 'include_open_edges')
		col.prop(self, 'deselect_after')
		col.separator()

		col.operator('wm.operator_defaults', text='Reset')

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'
	
	def execute(self, context):
		elements_to_mark = []
		for ob in context.objects_in_mode:
			me = ob.data
			self.bm = bmesh.from_edit_mesh(me)

			elements_to_mark = self._get_elements_to_mark(context)

			for edge in self.bm.edges:
				edge.select = False
				
			for element in elements_to_mark:
				element.select = True


		self._mark_elements()

		if self.deselect_after:
			bpy.ops.mesh.select_all(action='DESELECT')

		return {'FINISHED'}
	

	# GET ELEMENTS TO MARK  __________________________________________________

	def _get_elements_to_mark(self, context):
		'''
		This allows the operator to have independent selection filters for edges and faces.
		
		'''

		mode = get_selection_mode(context)

		# THIS PRIORITY IS IMPORTANT (TO ME).
		if mode[1]:
			return self._filter_edges(
				edges=self._get_selection(context),
				limit_method=self.edge_limit_method,
			)
		
		elif mode[2]:
			return self._filter_edges(
				edges=self._get_selection(context),
				limit_method=self.face_limit_method,
			)
		
		elif mode[0]:
			return self._get_selection(context)
		
	def _get_selection(self, context):
		'''
		Returns ALL elements if nothing is selected.
		'''

		mode = get_selection_mode(context)

		if mode[0]:
			return self._get_selected_verts() if any_elements_selected(context) else self.bm.verts
		
		if mode[1] or mode[2]:
			return self._get_selected_edges() if any_elements_selected(context) else self.bm.edges
		
	def _get_selected_verts(self):
		return [v for v in self.bm.verts if v.select]
		
	def _get_selected_edges(self):
		return [e for e in self.bm.edges if e.select]
		

	# FILTER EDGES BY TRAIT  __________________________________________________

	def _filter_edges(self, edges, limit_method) -> list[bmesh.types.BMEdge]:
		'''
		Returns a list of edges that meet the filter criteria.
		'''

		if limit_method == 'NONE':
			filtered_edges = set(edges)
		 
		elif limit_method == 'BORDER':
			filtered_edges = self._get_border_edges(edges)

		elif limit_method == 'ANGLE':
			filtered_edges = self._get_edges_by_angle(edges)
		
		# I prefer having this logic backwards to keep the checkbox disabled by default.
		if not self.include_open_edges:
			filtered_edges -= set(e for e in edges if e.is_boundary)
		
		return list(filtered_edges)
	
	def _get_border_edges(self, edges: list[bmesh.types.BMEdge]) -> set[bmesh.types.BMEdge]:
		'''
		Edges that border the selection + boundary (open) edges.
		'''

		return set(
			e for e in edges 
				if e.is_boundary or not all(f.select for f in e.link_faces)
		)
	
	def _get_edges_by_angle(self, edges: list[bmesh.types.BMEdge]) -> set[bmesh.types.BMEdge]:
		'''
		Edges with 2 selected faces with an average below the specified angle + boundary (open) edges.
		'''
		
		return set(
			e for e in edges 
				if e.is_boundary or (
					len(e.link_faces) == 2 and 
     					math.degrees(e.calc_face_angle()) > self.edge_angle
				)
		)


	# ELEMENT MARKING  __________________________________________________

	def _mark_elements(self):
		'''
		Just run the bpy operators to make things easier.
		'''

		if self.mark_type == 'CREASE':
			bpy.ops.transform.edge_crease(
				value=self.crease_value if self.action == 'MARK' else -1)
			return
		
		if self.mark_type == 'SEAM':
			bpy.ops.mesh.mark_seam(
				'INVOKE_DEFAULT',
				clear=False if self.action == 'MARK' else True)
			return
		
		if self.mark_type == 'SHARP':
			bpy.ops.mesh.mark_sharp(
				clear=False if self.action == 'MARK' else True)
			return
		
		if self.mark_type == 'SHARP_SEAM':
			bpy.ops.mesh.mark_seam(
				clear=False if self.action == 'MARK' else True)
			
			bpy.ops.mesh.mark_sharp(
				clear=False if self.action == 'MARK' else True)
			return
		
		raise ValueError('The selected element <mark_type> does not exist.')


classes = (
	ARMORED_OT_mark_edges,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	
def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)