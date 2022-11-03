# v2.0

import bpy
import bmesh
import math
from bpy.props import EnumProperty, BoolProperty, FloatProperty


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

	crease_value: FloatProperty(
		name='Value', default=1.0,
		description='Crease value to apply to the selection',
		min=0, max=1,
		step=0.1,
		# options={'HIDDEN'},
		)

	face_limit_method: EnumProperty( 
		name='Limit Method', 
		description='Which edges do you want to affect.', 
		default='BORDER', 
		items=[ ('BORDER', 'Border', 'Only affect border edges'),
			('ANGLE',  'Angle',  'Affect edges based on their angle'), ])
			
	edge_angle: FloatProperty(
		name='Edge Angle', default=30,
		description='Edges over this angle will be creased',
		min=0, max=180,)

	# include_boundary_edges: BoolProperty(
	# 	name='Include Boundary Edges', default=True,
	# 	description='Include the open edges of the mesh',)

	deselect_after: BoolProperty(
		name='Deselect after', default=False,
		description='Deselect after the operation is performed',)
	

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		col = layout.column(align=True)

		col.prop(self, 'crease_value')
		col.separator()

		row = col.row()
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

			mode = context.tool_settings.mesh_select_mode[:]

			if mode[0]:
				crease_layer = bm.verts.layers.crease.verify()
				crease_elements = self._check_for_selected_verts(context, bm.verts)

			elif mode[1] or mode[2]:
				crease_layer = bm.edges.layers.crease.verify()
				crease_elements = self._check_for_selected_edges(context, bm.edges)

				if mode[2]:
					crease_elements = self._filter_edges(context, self.face_limit_method, crease_elements)

			self._crease(crease_layer, crease_elements, self.crease_value)
			bmesh.update_edit_mesh(me)
			
		if self.deselect_after:
			bpy.ops.mesh.select_all(action='DESELECT')

		return {'FINISHED'}	
	

	def _check_for_selected_verts(self, context, verts: list[bmesh.types.BMVert]) -> list[bmesh.types.BMVert]:
		if any_components_selected(context):
			return [v for v in verts if v.select]
		
		return verts

	def _check_for_selected_edges(self, context, edges: list[bmesh.types.BMEdge]) -> list[bmesh.types.BMEdge]:
		if any_components_selected(context):
			return [e for e in edges if e.select]
		
		return edges

	def _filter_edges(self, context, limit_method, edges: list[bmesh.types.BMEdge]) -> list[bmesh.types.BMEdge]:
		if limit_method == 'BORDER':
			return self._get_border_edges(context, edges)

		if limit_method == 'ANGLE':
			return self._get_edges_by_angle(edges)
	
	def _get_border_edges(self, context, edges):
		if any_components_selected(context):
			return [e for e in edges if e.is_boundary or not all(f.select for f in e.link_faces)]
		else:
			return [e for e in edges if e.is_boundary]
	
	def _get_edges_by_angle(self, edges):
		return [e for e in edges if e.is_boundary 
					or (len(e.link_faces) == 2 and e.calc_face_angle() * 180 / math.pi > self.edge_angle)]
	
	def _crease(self, layer, elements, value: float) -> None:
		for e in elements:
			e[layer] = value
	

class ARMORED_OT_fast_uncrease(bpy.types.Operator):
	'''Instantly Uncrease selected edges (will affect the entire mesh if nothing is selected).

armoredColony.com '''
	
	bl_idname = 'mesh.armored_fast_uncrease'
	bl_label = 'ARMORED Uncrease'
	bl_options = {'REGISTER', 'UNDO'}
	
	deselect_after: BoolProperty(
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
		bpy.ops.transform.vert_crease(value=-1)
		bpy.ops.transform.edge_crease(value=-1)

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