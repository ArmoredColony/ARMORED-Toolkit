version = (0, 1, 0)

import bpy
import abc
import mathutils


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
	and the active object's rotation as world space.
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


# class Curve:

# 	def __init__(self, context, point_count=3, curve_type='BEZIER') -> None:
# 		self.context = context
# 		self.point_count = point_count
# 		self.curve_type = curve_type

# 		data = bpy.data.curves.new('Curve', 'CURVE')
# 		data.dimensions = '3D'

# 		spline = data.splines.new(type=curve_type)

# 		if curve_type == 'BEZIER':
# 			spline.bezier_points.add(point_count-1)
			
# 			for p in spline.bezier_points:
# 				p.handle_left_type = 'AUTO' 
# 				p.handle_right_type = 'AUTO'
# 		else:
# 			spline.points.add(point_count-1)

# 			# NURBS weight starts at 0 for some reason.
# 			for point in spline.points:
# 				point.co.w = 1.0

# 			# Not sure why but apparently we also need this.
# 			spline.use_endpoint_u = True

# 		self.curve = bpy.data.objects.new('Curve', data)
# 		self.curve.show_in_front = True

# 		context.scene.collection.objects.link(self.curve)
	
# 	@property
# 	def bl_object(self):
# 		return self.curve

# 	@property
# 	def points(self):
# 		if self.curve_type == 'BEZIER':
# 			return self.curve.data.splines[0].bezier_points
# 		else:
# 			return self.curve.data.splines[0].points


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
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		
		col = layout.column()

		row = col.row()
		row.prop(self, 'curve_type', expand=True)

		col.prop(self, 'point_count')

	def execute(self, context):
		# bpy.ops.ed.undo_push()
		self.selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
		self.active_object = self._get_active(context)

		self.rotation_quaternion = self._get_rotation_quaternion(context)
		bounds_calculator = FromIndividualBoundsEvaluated(context, self.selected_objects, mathutils.Quaternion())
		loc, rot, dim = bounds_calculator.calculate_transforms()

		# curve = Curve(context, self.point_count, self.curve_type)

		if self.curve_type == 'BEZIER':
			curve = BezierCurve(context, self.point_count)

		elif self.curve_type == 'NURBS':
			curve = NURBSCurve(context, self.point_count)
		
		# curve.bl_object.rotation_euler = context.active_object.rotation_euler
		
		step = dim.z / (self.point_count -1)
		for i, point in enumerate(curve.points):
			point.co.z = (i * step) # -dim.z / 2
			# point.co = self.rotation_quaternion @ point.co

		curve.bl_object.location.z = -dim.z / 2

		# curve.bl_object.location       = loc
		# curve.bl_object.rotation_euler = rot
		# curve.bl_object.dimensions     = dim




		# curve.bl_object.show_in_front = True

		# self.set_curve_origin(curve)
		# context.scene.cursor.location = curve.points[0].co
		# bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

		# bpy.ops.object.parent_set(type='CURVE', keep_transform=False)

		# THIS MAKES PARENTING WORK WITHOUT NEEDING A FULL SCENE UPDATE:
		curve.bl_object.matrix_world = curve.bl_object.matrix_basis

		for obj in context.selected_objects:
			# obj.location.z += dim.z / 2
			parent = curve.bl_object
			obj.parent = parent
			obj.matrix_parent_inverse = parent.matrix_world.inverted()
			obj.select_set(False)

		for obj in self.selected_objects:
			mod = obj.modifiers.new(name='Curve', type='CURVE')
			mod.deform_axis = 'POS_Z'
			mod.object = curve.bl_object
			
		curve.bl_object.select_set(True)
		context.view_layer.objects.active = curve.bl_object

		bpy.ops.object.mode_set(mode='EDIT')
		
		return {'FINISHED'}
	

	def _get_active(self, context):	# sourcery skip: assign-if-exp, reintroduce-else
		if context.active_object not in self.selected_objects:
			return None

		return context.active_object
	
	def _get_rotation_quaternion(self, context) -> mathutils.Quaternion:
		'''
		Get the rotation for the lattice based on the specified selection/operator properties.
		'''

		# if self.orientation == 'GLOBAL':
		# 	return mathutils.Quaternion()
		
		
		active = self.active_object

		if active is None:
			average = sum((mathutils.Vector(obj.rotation_euler) for obj in self.selected_objects), mathutils.Vector()) / len(self.selected_objects)
			return mathutils.Euler(average, 'XYZ').to_quaternion()

		if active.rotation_mode == 'QUATERNION':
			return active.rotation_quaternion

		if active.rotation_mode == 'AXIS_ANGLE':
			return mathutils.Quaternion(mathutils.Vector(active.rotation_axis_angle).yzw, active.rotation_axis_angle[0])

		return active.rotation_euler.to_quaternion()
	
	# def set_curve_origin(self, curve):
	# 	obj = curve.bl_object
	# 	matrix_world = obj.matrix_world
	# 	origin = mathutils.Vector(curve.points[0].co[:3])	# Just in case we're using NURBS

	# 	T = Matrix.Translation(-origin)
	# 	obj.data.transform(T)
	# 	matrix_world.translation = matrix_world @ origin

	# 	obj.location = origin

classes = (
	OBJECT_OT_armored_curve_deform,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)