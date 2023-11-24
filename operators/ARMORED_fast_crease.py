version = (2, 2, 0)

import bpy
import bmesh
import math
import contextlib


def any_components_selected(context) -> bool:
	objects = context.objects_in_mode
	selection = sum(obj.data.total_vert_sel for obj in objects)

	return bool(selection)


class ARMORED_OT_fast_crease(bpy.types.Operator):
	'''Instantly Crease selected edges (will affect the entire mesh if nothing is selected).

armoredColony.com '''
	
	bl_idname = 'mesh.armored_fast_crease'
	bl_label = 'ARMORED Crease'
	bl_options = {'REGISTER', 'UNDO'}

	crease_value: bpy.props.FloatProperty(
		name='Value', default=1.0,
		description='Crease value to apply to the selection',
		min=0, max=1,
		step=0.1,
		# options={'HIDDEN'},
		)

	edge_limit_method: bpy.props.EnumProperty( 
		name='Limit Method', 
		description='Which edges do you want to affect.', 
		default='NONE', 
		items=[ ('NONE',   'None',   'Crease normally'),
			('BORDER', 'Border', 'Crease the border edges of the selection'),
			('ANGLE',  'Angle',  'Crease the edges over a certain angle'), ])
	
	face_limit_method: bpy.props.EnumProperty( 
		name='Limit Method', 
		description='Which edges do you want to affect.', 
		default='BORDER', 
		items=[ ('NONE',   'None',   'Crease normally'),
			('BORDER', 'Border', 'Crease the border edges of the selection'),
			('ANGLE',  'Angle',  'Crease the edges over a certain angle'), ])
			
	edge_angle: bpy.props.FloatProperty(
		name='Edge Angle', default=30,
		description='Edges over this angle will be creased',
		min=0, max=180,)

	# include_boundary_edges: BoolProperty(
	# 	name='Include Boundary Edges', default=True,
	# 	description='Include the open edges of the mesh',)

	deselect_after: bpy.props.BoolProperty(
		name='Deselect after', default=False,
		description='Deselect after the operation is performed',)
	

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		select_mode = context.tool_settings.mesh_select_mode[:]

		col = layout.column(align=True)

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

		col.prop(self, 'deselect_after')
		col.separator()

		col.operator('wm.operator_defaults', text='Reset')

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'
	
	def execute(self, context):
		for ob in context.objects_in_mode:
			me = ob.data
			bm = bmesh.from_edit_mesh(me)

			crease_layer = self._get_crease_layer(context, bm)
			elements_to_crease = self._get_elements_to_crease(context, bm)

			self._crease(crease_layer, elements_to_crease, self.crease_value)
			bmesh.update_edit_mesh(me)
			
		if self.deselect_after:
			bpy.ops.mesh.select_all(action='DESELECT')

		return {'FINISHED'}
	

	# GET ELEMENTS TO CREASE >>

	def _get_elements_to_crease(self, context, bm):
		select_mode = context.tool_settings.mesh_select_mode[:]

		# THIS PRIORITY IS IMPORTANT (TO ME).
		if select_mode[1]:
			return self._filter_edges(context, self.edge_limit_method, self._check_for_selected_edges(context, bm.edges))
		
		if select_mode[2]:
			return self._filter_edges(context, self.face_limit_method, self._check_for_selected_edges(context, bm.edges))
		
		if select_mode[0]:
			return self._check_for_selected_verts(context, bm.verts)
		

	def _check_for_selected_verts(self, context, verts: list[bmesh.types.BMVert]) -> list[bmesh.types.BMVert]:
		'''
		Return ALL Verts if nothing is selected.
		'''

		if any_components_selected(context):
			return [v for v in verts if v.select]
		
		return verts

	def _check_for_selected_edges(self, context, edges: list[bmesh.types.BMEdge]) -> list[bmesh.types.BMEdge]:
		'''
		Return ALL Edges if nothing is selected.
		'''

		if any_components_selected(context):
			return [e for e in edges if e.select]
		
		return edges


	# FILTER EDGES BY TRAIT >>

	def _filter_edges(self, context, limit_method, edges: list[bmesh.types.BMEdge]) -> list[bmesh.types.BMEdge]:
		if limit_method == 'NONE':
			return edges
		 
		if limit_method == 'BORDER':
			return self._get_border_edges(context, edges)

		if limit_method == 'ANGLE':
			return self._get_edges_by_angle(edges)
	
	def _get_border_edges(self, context, edges: list[bmesh.types.BMEdge]) -> list[bmesh.types.BMEdge]:
		if any_components_selected(context):
			return [e for e in edges if e.is_boundary or not all(f.select for f in e.link_faces)]

		return [e for e in edges if e.is_boundary]
	
	def _get_edges_by_angle(self, edges: list[bmesh.types.BMEdge]) -> list[bmesh.types.BMEdge]:
		return [e for e in edges if e.is_boundary 
					or (len(e.link_faces) == 2 and math.degrees(e.calc_face_angle()) > self.edge_angle)]


	# GET CREASE LAYERS >>

	def _get_crease_layer(self, context, bm):
		'''
		Return a single crease layer based on the selection mode
		'''

		select_mode = context.tool_settings.mesh_select_mode[:]

		# THIS PRIORITY IS IMPORTANT (TO ME).
		if select_mode[1] or select_mode[2]:
			return self._get_edge_crease_layer(bm)
		
		return self._get_vertex_crease_layer(bm)

	def _get_edge_crease_layer(self, bm):
		'''
		Return the existing layer or create a new one.
		'''

		if bpy.app.version < (4, 0, 0):
			return bm.edges.layers.crease.verify()
		
		return bm.edges.layers.float.get('crease_edge', bm.edges.layers.float.new('crease_edge'))
		

	def _get_vertex_crease_layer(self, bm):
		'''
		Return the existing layer or create a new one.
		'''

		if bpy.app.version < (4, 0, 0):
			return bm.verts.layers.crease.verify()

		return bm.verts.layers.float.get('crease_vert', bm.verts.layers.float.new('crease_vert'))
		

	# CREASE >>

	def _crease(self, layer, elements, value: float) -> None:
		for e in elements:
			e[layer] = value
	

class ARMORED_OT_fast_uncrease(bpy.types.Operator):
	'''Instantly Uncrease selected edges (will affect the entire mesh if nothing is selected).

armoredColony.com '''
	
	bl_idname = 'mesh.armored_fast_uncrease'
	bl_label = 'ARMORED Uncrease'
	bl_options = {'REGISTER', 'UNDO'}
	
	deselect_after: bpy.props.BoolProperty(
		name='Deselect after', default=False,
		description='Deselect after the operation is performed',)

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'

	def execute(self, context):
		if any_components_selected(context):
			self._uncrease_selected()
		else:
			self._uncrease_all()

		if self.deselect_after:
			bpy.ops.mesh.select_all(action='DESELECT')

		return {'FINISHED'}	
	

	def _uncrease_selected(self) -> None:
		bpy.ops.transform.edge_crease(value=-1)
		with contextlib.suppress(AttributeError):	# Older versions have no vertex creasing.
			bpy.ops.transform.vert_crease(value=-1)

	def _uncrease_all(self) -> None:
		bpy.ops.mesh.select_all(action='SELECT')
		self._uncrease_selected()
		bpy.ops.mesh.select_all(action='DESELECT')


# def draw_menu(self, context):
# 	layout = self.layout
# 	layout.separator()
# 	layout.operator(ARMORED_OT_fast_crease.bl_idname, text='Fast Crease')
# 	layout.operator(ARMORED_OT_fast_uncrease.bl_idname, text='Fast Uncrease')


classes = (
	ARMORED_OT_fast_crease,
	ARMORED_OT_fast_uncrease,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	# bpy.types.VIEW3D_MT_edit_mesh_edges.append(draw_menu)
	
	
def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	# bpy.types.VIEW3D_MT_edit_mesh_edges.remove(draw_menu)