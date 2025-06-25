version = (3, 1, 0)

import bpy
import bmesh
import math


def any_elements_selected(context) -> bool:
	objects = context.objects_in_mode
	selection = sum(obj.data.total_vert_sel for obj in objects)

	return bool(selection)


def get_selection_mode(context):
	return context.tool_settings.mesh_select_mode[:]


def get_selected_verts(bm: bmesh.types.BMesh):
	return [v for v in bm.verts if v.select]
	

def get_selected_edges(bm: bmesh.types.BMesh):
	return [e for e in bm.edges if e.select]


class ARMORED_OT_mark_edges(bpy.types.Operator):
	'''Instantly Mark selected edges (will affect the entire mesh if nothing is selected).

	armoredColony.com '''
	
	bl_idname = 'mesh.armored_mark_edges'
	bl_label = 'ARMORED Mark Edges'
	bl_options = {'REGISTER', 'UNDO', 'PRESET'}


	action: bpy.props.EnumProperty(
		name='Action', 
		default='MARK',
		items=[
			('MARK',  'Mark',  'Mark the selection'),
			('CLEAR', 'Clear', 'Clear the specified mark'), 
		]
	)

	mark_type: bpy.props.EnumProperty(
		name='Mark as', 
		default='CREASE',
		items=[
			('CREASE',	 'Crease',	  'Set a Crease value'),
			('SHARP',	 'Sharp',	  'Mark as Sharp (shading)'), 
			('SEAM',	 'UV Seam',	  'Mark as UV Seam'),
			('SHARP_SEAM',	 'Sharp UV Seam', 'Mark as UV Seam and Sharp'), 
			('BEVEL_WEIGHT', 'Bevel Weight',  'Set a Bevel Weight value'),
		]
	)

	crease_value: bpy.props.FloatProperty(
		name='Value', 
		default=1.0,
		description='Crease value to apply to the selection',
		min=0, max=1,
		# step=5,
	)

	bevel_weight_value: bpy.props.FloatProperty(
		name='Value', 
		description='Bevel Weight value to apply to the selection',
		default=1.0,
		min=0, max=1,
		# step=5,
	)


	shared_items = [ 
			('NONE',	'None',		 'All Edges'),
			('BORDER',	'Border',	 'The borders of the selection'),
			('INNER',	'Inner',	 'Selected Edges without the border'),
			('ANGLE',	'Angle',	 'Edges by angle'),
			('ANGLE_INNER',	'Angle + Inner', 'Edges by angle without the border'),
		]

	edge_limit_method: bpy.props.EnumProperty( 
		name='Limit Method', 	
		description='Apply a filter to your selection', 
		default='NONE', 
		items=shared_items
	)
	
	face_limit_method: bpy.props.EnumProperty( 
		name='Limit Method', 
		description='Apply a filter to your selection', 
		default='BORDER', 
		items=shared_items
	)


	edge_angle: bpy.props.FloatProperty(
		name='Edge Angle', 
		description='Edges over this angle will be marked',
		default=30,
		min=0, max=180,
	)

	include_open_edges: bpy.props.BoolProperty(
		name='Include Open Edges', 
		description='Include any Open Edges in the calculation (these edges can still be deselected by the limit method)',
		default=False,
	)

	deselect_after: bpy.props.BoolProperty(
		name='Deselect after', 
		description='Deselect everything after the operation is finished',
		default=False,
	)


	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.separator()

		_, edge_mode, face_mode = get_selection_mode(context)

		col = layout.column(align=True)

		row = col.row()
		row.prop(self, 'action', expand=True)
		col.separator()

		col.prop(self, 'mark_type', expand=True)
		col.separator()

		if self.mark_type == 'CREASE':
			col.prop(self, 'crease_value')
			col.separator(type='LINE', factor=2)

		elif self.mark_type == 'BEVEL_WEIGHT':
			col.prop(self, 'bevel_weight_value')
			col.separator(type='LINE', factor=2)

		_limit_method = None

		if edge_mode:
			col.prop(self, 'edge_limit_method', expand=True)
			_limit_method = self.edge_limit_method

		elif face_mode:
			col.prop(self, 'face_limit_method', expand=True)
			_limit_method = self.face_limit_method

		if _limit_method in {'ANGLE', 'ANGLE_INNER'}:
			col.separator()
			col.prop(self, 'edge_angle')
			
		col.separator(type='LINE', factor=2)

		col.prop(self, 'include_open_edges')
		col.prop(self, 'deselect_after')
		col.separator()

		col.operator('wm.operator_defaults', text='Reset')

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'
	
	def execute(self, context):

		# Only select the desired elements.
		for ob in context.objects_in_mode:
			mesh = ob.data
			bm = bmesh.from_edit_mesh(mesh)

			target_elements   = self._find_elements(context, bm)
			filtered_elements = self._filter_elements(context, target_elements)
			
			bpy.ops.mesh.select_all(action='DESELECT')
			
			for element in filtered_elements:
				element.select = True
			
			bm.select_flush_mode()
			bmesh.update_edit_mesh(mesh)

		# Tag everything selected at once with bpy.ops
		self._mark_selected_elements(context)

		if self.deselect_after:
			bpy.ops.mesh.select_all(action='DESELECT')

		return {'FINISHED'}
	

	def _find_elements(self, context, bm: bmesh.types.BMesh):
		'''
		Returns the selected elements or ALL if nothing is selected.
		'''

		vert_mode, edge_mode, face_mode = get_selection_mode(context)

		if vert_mode:
			return get_selected_verts(bm) if any_elements_selected(context) else bm.verts
		
		if edge_mode or face_mode:
			return get_selected_edges(bm) if any_elements_selected(context) else bm.edges
		

	# FILTER ELEMENTS BY TRAIT  __________________________________________________

	def _filter_elements(self, context, target_elements):
		'''
		Some selection modes have independent filters/limit_methods.
		
		'''

		vert_mode, edge_mode, face_mode = get_selection_mode(context)

		# THIS PRIORITY IS IMPORTANT (TO ME).
		if edge_mode:
			return self._filter_edges(
				edges=target_elements,
				limit_method=self.edge_limit_method,
			)
		
		elif face_mode:
			return self._filter_edges(
				edges=target_elements,
				limit_method=self.face_limit_method,
			)
		
		elif vert_mode:
			return target_elements

	def _filter_edges(self, edges, limit_method) -> list[bmesh.types.BMEdge]:
		'''
		Returns a list of edges that meet the filter criteria.
		'''

		if limit_method == 'NONE':
			filtered_edges = set(edges)
		 
		elif limit_method == 'BORDER':
			filtered_edges = self._get_border_edges(edges)

		elif limit_method == 'INNER':
			filtered_edges = self._get_inner_edges(edges)

		elif limit_method == 'ANGLE':
			filtered_edges = self._get_edges_by_angle(edges)

		elif limit_method == 'ANGLE_INNER':
			inner_edges = self._get_inner_edges(edges)
			filtered_edges = self._get_edges_by_angle(inner_edges)
		
		
		# I prefer having this logic backwards to keep the checkbox disabled by default.
		if not self.include_open_edges:
			filtered_edges -= set(e for e in edges if e.is_boundary)
		
		return list(filtered_edges)
	
	def _get_border_edges(self, edges: list[bmesh.types.BMEdge]) -> set[bmesh.types.BMEdge]:
		'''
		Border edges + boundary (open) edges.
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
	
	def _get_inner_edges(self, edges: list[bmesh.types.BMEdge]) -> set[bmesh.types.BMEdge]:
		'''
		All edges minus the border.
		'''
		
		return	set(
			e for e in edges
				if not e.is_boundary and all(f.select for f in e.link_faces)
			)


	# ELEMENT MARKING  __________________________________________________

	def _mark_selected_elements(self, context):
		'''
		Just run the bpy operators to make things easier.
		'''

		clear = self.action == 'CLEAR'

		vert_mode, _, _ = get_selection_mode(context)

		if self.mark_type == 'CREASE':
			value = -1 if clear else self.crease_value

			if vert_mode:
				bpy.ops.transform.vert_crease(value=value)
			else:
				bpy.ops.transform.edge_crease(value=value)
			
			return
		
		if self.mark_type == 'SEAM':
			bpy.ops.mesh.mark_seam('INVOKE_DEFAULT', clear=clear)
			
			return
		
		if self.mark_type == 'SHARP':
			bpy.ops.mesh.mark_sharp(clear=clear)
			
			return
		
		if self.mark_type == 'SHARP_SEAM':
			bpy.ops.mesh.mark_seam(clear=clear)
			bpy.ops.mesh.mark_sharp(clear=clear)
			
			return
		
		if self.mark_type == 'BEVEL_WEIGHT':
			value = -1 if clear else self.bevel_weight_value
			if vert_mode:
				pass
				# The operator does not exist yet.
			else:
				bpy.ops.transform.edge_bevelweight(value=value, snap=False)
			
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