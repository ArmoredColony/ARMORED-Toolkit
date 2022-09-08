# v1.2

import bpy
from bpy.props import EnumProperty, BoolProperty, FloatProperty


class ARMORED_OT_fast_crease(bpy.types.Operator):
	'''Fully Crease/Uncrease selected edges (uncrease will apply to all edges if nothing is selected).

(www.armoredColony.com)'''
	
	bl_idname = 'mesh.armored_fast_crease'
	bl_label = 'ARMORED Crease'
	bl_options = {'REGISTER', 'UNDO'}

	crease_mode: EnumProperty( 
		name='Action', 
		description='Crease mode.', 
		default='CREASE', 
		items=[ ('CREASE',   'Crease',   'Selection crease level to 1'),
			('UNCREASE', 'Uncrease', 'Selection crease level to 0'), ])

	# value: FloatProperty(
	# 	name='Value', default=1.0,
	# 	description='Crease value to apply to the selection',)

	deselect_after: BoolProperty(
		name='Deselect after', default=False,
		description='Deselect after the operation is performed',)


	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		row = layout.row(align=True)
		row.prop(self, 'crease_mode', expand=True)
		layout.separator()

		layout.prop(self, 'deselect_after')

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'

	def execute(self, context):
		self.mode = context.tool_settings.mesh_select_mode[:]

		if self.mode[2]:
			bpy.ops.mesh.region_to_loop()

		if self.crease_mode == 'CREASE':
			self.crease_selected()
		elif self._any_components_selected(context):
			self.uncrease_selected()
		else:
			print('Nothing Selected -> Uncrease ALL')
			self.uncrease_all()

		if self.deselect_after:
			bpy.ops.mesh.select_all(action='DESELECT')
			
		return {'FINISHED'}
	
	
	def _set_crease_value(self, value: int) -> None:
		if self.mode[0]:  ## Vertex Mode.
			bpy.ops.transform.vert_crease(value=value)
		else:
			bpy.ops.transform.edge_crease(value=value)
	
	def crease_selected(self) -> None:
		self._set_crease_value(1)

	def uncrease_selected(self) -> None:
		self._set_crease_value(-1)
	
	def uncrease_all(self) -> None:
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.transform.vert_crease(value=-1)
		bpy.ops.transform.edge_crease(value=-1)
		bpy.ops.mesh.select_all(action='DESELECT')

	def _any_components_selected(self, context) -> bool:
		objects = context.objects_in_mode
		selection = sum(obj.data.total_vert_sel for obj in objects)
		print('total vert sel', selection)

		return bool(selection)
	


class ARMORED_MT_fast_crease(bpy.types.Menu):
	bl_label = 'Fast Crease'
	bl_idname = 'ARMORED_MT_fast_crease'

	def draw(self, context):
		layout = self.layout
		layout.operator(ARMORED_OT_fast_crease.bl_idname, text='ARMORED Crease').crease_mode = 'CREASE'
		layout.operator(ARMORED_OT_fast_crease.bl_idname, text='ARMORED Uncrease').crease_mode = 'UNCREASE'


def draw_menu(self, context):
	self.layout.separator()
	self.layout.menu(ARMORED_MT_fast_crease.bl_idname, icon='FAKE_USER_OFF')


classes = (
	ARMORED_OT_fast_crease,
	ARMORED_MT_fast_crease,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.VIEW3D_MT_edit_mesh_edges.append(draw_menu)
	
	
def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	bpy.types.VIEW3D_MT_edit_mesh_edges.remove(draw_menu)