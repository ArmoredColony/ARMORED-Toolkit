import bpy

from mathutils import Vector


class OBJECT_OT_armored_clear_location(bpy.types.Operator):
	'''Similar to Blender's clear location (ALT G), but this version can optionally keep the relative locations between the selected objects and move them as a group to world zero.

armoredColony.com '''

	bl_idname = 'object.armored_clear_location'
	bl_label = 'ARMORED Clear Location'
	bl_options = {'REGISTER', 'UNDO'}

	keep_relative: bpy.props.BoolProperty(
		name='Keep Relative', default=True,
		description='With multiple objects selected, keep their relative positions and move them as a group.')

	center: bpy.props.EnumProperty(
		name='Group Center',
		default='ACTIVE',
		description='Choose the group center',
		items = [ 
			('ACTIVE',  'Active',  'The active object\'s origin will end at world zero'),
			('BOUNDS',  'Bounds',  'The bounding box center of your selection will end at world zero'),
			]
		)

	# @classmethod
	# def poll(cls, context):
	# 	return context.mode == 'OBJECT'

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		layout.prop(self, 'keep_relative')
		layout.separator()

		row = layout.row()
		row.prop(self, 'center', expand=True)

		if not self.keep_relative or self._get_active(context) is None:
			row.enabled = False

	def execute(self, context):
		if not self.keep_relative:
			bpy.ops.object.location_clear()

			return {'FINISHED'}
		
		if self._get_active(context) is None:
			self.center = 'BOUNDS'

		self.selected_objects = context.selected_objects

		if self.center == 'ACTIVE':
			group_center = context.active_object.matrix_world.translation.copy()

		elif self.center == 'BOUNDS':
			bounds_min, bounds_max = self._get_min_max_vectors_from_bounds()
			group_center = (bounds_min + bounds_max) / 2

		self._clear_location_of_selected(group_center)

		return {'FINISHED'}
	

	# PRIVATE HELPERS

	def _get_active(self, context):
		if context.active_object not in context.selected_objects:
			return None
		
		return context.active_object
	
	def _clear_location_of_selected(self, group_center: Vector) -> None:
		for obj in self.selected_objects:
			obj.matrix_world.translation -= group_center
	
	def _get_min_max_vectors_from_bounds(self) -> tuple[Vector, Vector]:
		'''
		Returns (min: Vector, max: Vector) corners of a bounding box around the selected objects (uses evaluated depsgraph).
		'''

		depsgraph = bpy.context.evaluated_depsgraph_get()

		vertex_coords = []
		for obj in self.selected_objects:
			if obj.modifiers:
				obj = obj.evaluated_get(depsgraph)

			vertex_coords.extend(
				(obj.matrix_world @ Vector(point)) for point in obj.bound_box)
		
		return Vector(map(min, *vertex_coords)), Vector(map(max, *vertex_coords))


classes = (
	OBJECT_OT_armored_clear_location,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)