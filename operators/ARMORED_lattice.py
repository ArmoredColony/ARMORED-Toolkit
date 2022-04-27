# v2.0

import bpy
from bpy.props import IntProperty, BoolProperty, EnumProperty

from mathutils import Vector


class ARMORED_OT_lattice(bpy.types.Operator):
	'''Creates a lattice that matches your object dimensions and transforms.

armoredColony.com '''

	bl_idname = 'object.armored_lattice'
	bl_label  = 'ARMORED Lattice'
	bl_options = {'REGISTER', 'UNDO'}

	resolution: IntProperty(
		name='Resolution', default=3, min=2)

	lattice_center: EnumProperty(
		name='Center', default='BOUNDS', 
		description='Where to use as the lattice center point',
		items=[ ('BOUNDS', 'Bounds', 'Object Bounding Box'),
			('ORIGIN', 'Origin', 'Object Origin'), ])
	
	zero_mesh_transforms: BoolProperty(
		name='Zero Mesh Transforms', default=False, 
		description='Clear all mesh transforms and transfer them to the lattice instead')
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		col = layout.column()
		col.prop(self, 'resolution')
		row = col.row()
		row.prop(self, 'lattice_center', expand=True)
		col.prop(self, 'zero_mesh_transforms')
		col.separator()
		col.operator('wm.operator_defaults', text='Reset')

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

		# This alternate poll return prevents operator for working correctly?!
		# active = context.active_object
		# return context.active_object is not None and context.active_object.type == 'MESH'
	
	def execute(self, context):
		self.target = context.active_object

		if context.mode != 'OBJECT':
			bpy.ops.object.mode_set(mode='OBJECT')
		
		if self.zero_mesh_transforms:
			self._save_mesh_transforms()
			self._zero_mesh_transforms()

		self._create_lattice(context)
		self._set_lattice_resolution()
		self._set_lattice_transforms()

		# Don't ask me why but we need something to trigger a scene update 
		# or parent matrix inversion will not apply.
		bpy.ops.object.select_all(action='DESELECT')

		self._parent_mesh_to_lattice()
		self._add_lattice_modifier()

		if self.zero_mesh_transforms:
			self._set_lattice_transforms_from_saved()

		self._select_lattice(context)
		bpy.ops.object.mode_set(mode='EDIT')
		return {'FINISHED'}
	
	
	def _save_mesh_transforms(self):
		self.saved_location = self.target.location.copy()
		self.saved_rotation_euler = self.target.rotation_euler.copy()
		self.saved_dimensions = self.target.dimensions.copy()
		self.saved_bounds_center = self._get_bounding_box_center(obj=self.target).copy()

	def _zero_mesh_transforms(self):
		bpy.ops.object.location_clear(clear_delta=False)
		bpy.ops.object.rotation_clear(clear_delta=False)
		bpy.ops.object.scale_clear(clear_delta=False)

	def _create_lattice(self, context):
		bpy.ops.object.add(type='LATTICE')
		self.lattice = context.active_object

	def _set_lattice_resolution(self):
		data = self.lattice.data
		data.points_u = self.resolution
		data.points_v = self.resolution
		data.points_w = self.resolution
	
	def _set_lattice_transforms(self):
		self.lattice.location = self.target.location
		self.lattice.rotation_euler = self.target.rotation_euler
		self.lattice.dimensions = self.target.dimensions

		if self.lattice_center == 'BOUNDS':
			self.lattice.location = self._get_bounding_box_center(obj=self.target)

	def _set_lattice_transforms_from_saved(self):
		self.lattice.location = self.saved_location
		self.lattice.rotation_euler = self.saved_rotation_euler
		self.lattice.dimensions = self.saved_dimensions

		if self.lattice_center == 'BOUNDS':
			self.lattice.location = self.saved_bounds_center
	
	def _parent_mesh_to_lattice(self):
		self.target.parent = self.lattice
		self.target.matrix_parent_inverse = self.lattice.matrix_world.inverted()
		
	def _add_lattice_modifier(self):
		mod = self.target.modifiers.new('Lattice', 'LATTICE')
		mod.object = self.lattice

	def _select_lattice(self, context):
		context.view_layer.objects.active = self.lattice
		self.lattice.select_set(True)
	
	def _get_bounding_box_center(self, obj) -> Vector:
		local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
		return obj.matrix_world @ local_bbox_center # global bbox center


classes = (
	ARMORED_OT_lattice,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
