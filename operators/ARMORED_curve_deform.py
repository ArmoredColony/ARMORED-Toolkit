version = (1, 1, 0)

import bpy
import abc
import mathutils
import math


def get_active(active_object, selected_objects):	# sourcery skip: assign-if-exp, reintroduce-else
	if active_object not in selected_objects:
		return None

	return active_object

def get_rotation_quaternion(active_object, selected_objects, orientation='GLOBAL') -> mathutils.Quaternion:
	'''
	Return a quaternion rotatoin based on the selection/operator properties.
	'''

	if orientation == 'GLOBAL':
		return mathutils.Quaternion()
	
	active = active_object

	if active is None:
		average_rotation = sum((mathutils.Vector(obj.rotation_euler) for obj in selected_objects), mathutils.Vector()) / len(selected_objects)
		return mathutils.Euler(average_rotation, 'XYZ').to_quaternion()

	if active.rotation_mode == 'QUATERNION':
		return active.rotation_quaternion

	if active.rotation_mode == 'AXIS_ANGLE':
		return mathutils.Quaternion(mathutils.Vector(active.rotation_axis_angle).yzw, active.rotation_axis_angle[0])

	return active.rotation_euler.to_quaternion()


class BoundsCalculator(abc.ABC):
	'''
	Abstract Base Class for calculating the location, rotation and dimensions of a bounding box.
	'''

	@abc.abstractmethod
	def calculate_location(self):
		pass

	@abc.abstractmethod
	def calculate_rotation(self):
		pass

	@abc.abstractmethod
	def calculate_dimensions(self):
		pass

	def calculate_transforms(self) -> tuple[mathutils.Vector, mathutils.Vector, mathutils.Vector]:
		loc = self.calculate_location()
		rot = self.calculate_rotation()
		dim = self.calculate_dimensions()

		return loc, rot, dim


class FromIndividualBoundingBoxes(BoundsCalculator):
	'''
	Calculate the transforms of a bounding box around the selected objects, based on their individual bounding boxes  
	and a quaternion rotation that defines the world space.
	'''

	def __init__(self, selected_objects: list[bpy.types.Object], rotation_quaternion: mathutils.Quaternion=None) -> None:
		self.selected_objects = selected_objects

		self.rotation_quaternion = mathutils.Quaternion() if rotation_quaternion is None else rotation_quaternion
		self.bounds_min, self.bounds_max = self._get_min_max_vectors_from_bounds()
		
	def calculate_location(self) -> mathutils.Vector:
		return self.rotation_quaternion @ ((self.bounds_min + self.bounds_max) / 2)

	def calculate_rotation(self) -> mathutils.Vector:
		return self.rotation_quaternion.to_euler()

	def calculate_dimensions(self) -> mathutils.Vector:
		return self._get_dimensions_from_min_max_bounds()
	

	# PRIVATE HELPERS >>

	def _get_dimensions_from_min_max_bounds(self) -> mathutils.Vector:
		'''
		Returns (x, y, z): mathutils.Vector dimensions of a bounding box based on 2 opposite corners.
		'''

		return mathutils.Vector((
			abs(self.bounds_min.x - self.bounds_max.x), 
			abs(self.bounds_min.y - self.bounds_max.y), 
			abs(self.bounds_min.z - self.bounds_max.z)
			))
	
	def _get_min_max_vectors_from_bounds(self) -> tuple[mathutils.Vector, mathutils.Vector]:

		'''
		Returns (min: mathutils.Vector, max: mathutils.Vector) corners of a bounding box around the selected objects.
		'''

		print(f'class selected {self.selected_objects}')
		vertex_coords = []
		for obj in self.selected_objects:
			vertex_coords.extend(
				self.rotation_quaternion.inverted() @ 
				(obj.matrix_world @ mathutils.Vector(point)) for point in obj.bound_box)
		
		return mathutils.Vector(map(min, *vertex_coords)), mathutils.Vector(map(max, *vertex_coords))	# NOT SURE WHY THIS WORKS


class FromIndividualBoundsEvaluated(FromIndividualBoundingBoxes):
	'''
	Same as FromIndividualBoundingBoxes, but uses evaluated objects to get the bounding box.
	'''

	def __init__(self, context, selected_objects: list[bpy.types.Object], rotation_quaternion: mathutils.Quaternion) -> None:
		self.context = context
		super().__init__(selected_objects, rotation_quaternion)

	def _get_min_max_vectors_from_bounds(self) -> tuple[mathutils.Vector, mathutils.Vector]:
		'''
		Returns (min: mathutils.Vector, max: mathutils.Vector) corners of a bounding box around the selected objects.
		'''

		depsgraph = self.context.evaluated_depsgraph_get()

		vertex_coords = []
		for obj in self.selected_objects:
			if obj.modifiers:
				obj = obj.evaluated_get(depsgraph)
				
			vertex_coords.extend(
				self.rotation_quaternion.inverted() @ 
					(obj.matrix_world @ mathutils.Vector(point)) for point in obj.bound_box)
		
		return mathutils.Vector(map(min, *vertex_coords)), mathutils.Vector(map(max, *vertex_coords))	# NOT SURE WHY THIS WORKS


class BezierCurve:

	def __init__(self, context, point_count=3) -> None:
		self.context = context
		self.point_count = point_count

		data = bpy.data.curves.new('Curve', 'CURVE')
		data.dimensions = '3D'

		spline = data.splines.new(type='BEZIER')
		spline.bezier_points.add(point_count-1)

		for p in spline.bezier_points:
			p.handle_left_type = 'AUTO' 
			p.handle_right_type = 'AUTO'

		self.curve = bpy.data.objects.new('Curve', data)
		self.curve.show_in_front = True

		context.scene.collection.objects.link(self.curve)
	
	@property
	def bl_object(self):
		return self.curve

	@property
	def points(self):
		return self.curve.data.splines[0].bezier_points


class NURBSCurve:

	def __init__(self, context, point_count=3) -> None:
		self.context = context
		self.point_count = point_count

		data = bpy.data.curves.new('Curve', 'CURVE')
		data.dimensions = '3D'

		spline = data.splines.new(type='NURBS')
		spline.points.add(point_count-1)

		# NURBS weight starts at 0 for some reason.
		for point in spline.points:
			point.co.w = 1.0

		# Not sure why but apparently we also need this.
		spline.use_endpoint_u = True

		self.curve = bpy.data.objects.new('Curve', data)
		self.curve.show_in_front = True

		context.scene.collection.objects.link(self.curve)
		
	
	@property
	def bl_object(self):
		return self.curve

	@property
	def points(self):
		return self.curve.data.splines[0].points



class OBJECT_OT_armored_curve_deform(bpy.types.Operator):
	'''Create a curve deformer for the selected objects with the correct size and orientation.

armoredColony.com '''

	bl_idname = 'object.armored_curve_deform'
	bl_label = 'ARMORED Curve Deform'
	bl_options = {'REGISTER', 'UNDO'}

	curve_type: bpy.props.EnumProperty(
		name='Type', default='NURBS',
		items=[	('BEZIER', 'Bezier', 'Use a Bezier curve for the deformer'),
			('NURBS',  'NURBS',  'Use a NURBS curve for the deformer'), ])
	
	point_count: bpy.props.IntProperty(
		name='Point Count', default=3, min=3,)
	
	# parent_to_curve: bpy.props.BoolProperty(
	# 	name='Parent to Curve', default=False,)
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		
		col = layout.column()

		row = col.row()
		row.prop(self, 'curve_type', expand=True)

		col.prop(self, 'point_count')
		col.separator()

		# col.prop(self, 'parent_to_curve')

	def execute(self, context):
		self.selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
		
		if not self.selected_objects:
			return {'CANCELLED'}
			
		self.active_object = get_active(context.active_object, self.selected_objects)

		self.rotation_quaternion = get_rotation_quaternion(self.active_object, self.selected_objects)
		bounds_calculator = FromIndividualBoundsEvaluated(context, self.selected_objects, mathutils.Quaternion())
		bounds_loc, bounds_rot, bounds_dim = bounds_calculator.calculate_transforms()

		if self.curve_type == 'BEZIER':
			curve = BezierCurve(context, self.point_count)

		elif self.curve_type == 'NURBS':
			curve = NURBSCurve(context, self.point_count)
		
		# Dimensions
		step = bounds_dim.z / (self.point_count -1)
		for i, point in enumerate(curve.points):
			point.co.z = (i * step) # -bounds_dim.z / 2
			# point.co = self.rotation_quaternion @ point.co

		curve.bl_object.location = bounds_loc
		curve.bl_object.location.z -= bounds_dim.z / 2
		curve.bl_object.rotation_euler = bounds_rot

		# THIS MAKES PARENTING WORK WITHOUT NEEDING A FULL SCENE UPDATE:
		curve.bl_object.matrix_world = curve.bl_object.matrix_basis

		# if self.parent_to_curve:
		# 	for obj in context.selected_objects:
		# 		parent = curve.bl_object
		# 		obj.parent = parent
		# 		obj.matrix_parent_inverse = parent.matrix_world.inverted()
		# 		obj.select_set(False)

		for obj in self.selected_objects:
			found_subsurf = bool(obj.modifiers and obj.modifiers[-1].type == 'SUBSURF')

			mod = obj.modifiers.new(name='Curve', type='CURVE')

			mod.deform_axis = 'POS_Z'
			mod.object = curve.bl_object

			if found_subsurf:
				bpy.ops.object.modifier_move_up({'object': obj}, modifier=mod.name)
		
		bpy.ops.object.select_all(action='DESELECT')
		curve.bl_object.select_set(True)
		context.view_layer.objects.active = curve.bl_object

		bpy.ops.object.mode_set(mode='EDIT')
		
		return {'FINISHED'}


class OBJECT_OT_armored_circle_deform(bpy.types.Operator):
	'''Create a curve deformer for the selected objects with the correct size and orientation.

armoredColony.com '''

	bl_idname = 'object.armored_circle_deform'
	bl_label = 'ARMORED Circle Deform'
	bl_options = {'REGISTER', 'UNDO'}

	bend_direction: bpy.props.EnumProperty(
		name='Bend Direction', default='CONCAVE',
		items=[	('CONCAVE', 'Concave', 'Bend the selected objects backwards'),
			('CONVEX', 'Convex',  'Bend the selected objects forwards'), ])
	
	rotation: bpy.props.FloatProperty(
		name='Rotation', default=0, 
		min=-360, max=360, unit='ROTATION', subtype='ANGLE',)
	
	scale_multiplier: bpy.props.FloatProperty(
		name='Scale', default=1, min=0,)
	
	# parent_to_curve: bpy.props.BoolProperty(
	# 	name='Parent to Curve', default=False,)
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		
		col = layout.column()

		row = col.row()
		row.prop(self, 'bend_direction', expand=True)

		col.prop(self, 'rotation')
		col.prop(self, 'scale_multiplier')

	def execute(self, context):
		self.selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

		if not self.selected_objects:
			return {'CANCELLED'}

		self.active_object = get_active(context.active_object, self.selected_objects)

		self.rotation_quaternion = get_rotation_quaternion(self.active_object, self.selected_objects)
		bounds_calculator = FromIndividualBoundsEvaluated(context, self.selected_objects, mathutils.Quaternion())
		bounds_loc, bounds_rot, bounds_dim = bounds_calculator.calculate_transforms()

		context.scene.tool_settings.use_transform_pivot_point_align = False

		bpy.ops.curve.primitive_bezier_circle_add(radius=1, location=bounds_loc, align='WORLD', enter_editmode=False, scale=(1, 1, 1))
		bpy.ops.transform.rotate(value=-math.pi / 2, orient_axis='Y')
		bpy.ops.object.transform_apply(rotation=True)
		curve = context.active_object
		curve.data.resolution_u = 128

		points = curve.data.splines[0].bezier_points
		for p in points:
			p.tilt = self.rotation + math.pi

		origin_location = curve.matrix_world @ points[3].co
		context.scene.cursor.location = origin_location
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
		curve.location = bounds_loc

		for obj in self.selected_objects:
			obj.select_set(True)

		# bpy.ops.object.parent_set(type='CURVE')
		# bpy.ops.transform.rotate(value=math.pi, orient_axis='Y')
		# bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

		for obj in self.selected_objects:
			found_subsurf = bool(obj.modifiers and obj.modifiers[-1].type == 'SUBSURF')

			mod = obj.modifiers.new(name='Curve', type='CURVE')

			mod.object = curve
			mod.deform_axis = 'POS_Z'

			if found_subsurf:
				bpy.ops.object.modifier_move_up({'object': obj}, modifier=mod.name)

		for obj in self.selected_objects:
			obj.select_set(False)

		scale = mathutils.Vector.Fill(3, bounds_dim.z / 2)	# Arbitrary Scale.
		if self.bend_direction == 'CONCAVE':
			curve.scale = scale * self.scale_multiplier
		elif self.bend_direction == 'CONVEX':
			curve.scale = scale * self.scale_multiplier * -1
		else:
			raise ValueError(f'{self.bend_direction} is not a valid bend direction.')
		
		return {'FINISHED'}


classes = (
	OBJECT_OT_armored_curve_deform,
	OBJECT_OT_armored_circle_deform,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)