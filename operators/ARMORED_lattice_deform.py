version = (4, 5, 0)

import bpy
import bmesh
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
	and treating the active object's rotation as world space.
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

		vertex_coords = []
		for obj in self.selected_objects:
			vertex_coords.extend(
				self.rotation_quaternion.inverted() @ 
				(obj.matrix_world @ mathutils.Vector(point)) for point in obj.bound_box)
		
		return mathutils.Vector(map(min, *vertex_coords)), mathutils.Vector(map(max, *vertex_coords))	# NOT SURE WHY THIS WORKS


class FromIndividualBoundingBoxesEvaluated(FromIndividualBoundingBoxes):
	'''
	Same as FromIndividualBoundingBoxes, but uses evaluated objects to get the bounding box.
	DOES NOT SEEM TO WORK IN BL4.1
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

# ===============
# COMPOSITOR CLASS
# ===============

class LatticeDeformer:
	'''
	Transform a Lattice to encapsulate the selected objects and create the necessary deform modifiers.
	'''

	def __init__(self, context, lattice: bpy.types.Object, bounds_calculator: BoundsCalculator) -> None:
		self.lattice = lattice
		self.context = context
		self.bounds_calculator = bounds_calculator
		self.selected_objects = bounds_calculator.selected_objects

		self.loc, self.rot, self.dim = self.bounds_calculator.calculate_transforms()

		self._set_transforms()
		self._add_modifiers()
	
	@property
	def bl_object(self):
		return self.lattice
	

	# PRIVATE HELPERS

	def _set_transforms(self) -> None:
		self.lattice.location       = self.loc
		self.lattice.rotation_euler = self.rot
		self.lattice.dimensions     = self.dim
	
	def _add_modifiers(self) -> None:
		for obj in self.selected_objects:
			found_subsurf = bool(obj.modifiers and obj.modifiers[-1].type == 'SUBSURF')

			mod = obj.modifiers.new('Lattice', 'LATTICE')
			mod.object = self.lattice

			if found_subsurf:
				with self.context.temp_override(object=obj):
					bpy.ops.object.modifier_move_up(modifier=mod.name)
	

# ===============
# BLENDER OBJECTS
# ===============

def WireCube(context) -> bpy.types.Object:
	'''
	Create a Wireframe Cube (for debugging purposes).
	'''

	data = bpy.data.meshes.new('Cube')
	cube = bpy.data.objects.new('Cube', data)
	context.collection.objects.link(cube)

	bm = bmesh.new()
	bmesh.ops.create_cube(bm, size=2, calc_uvs=False)
	bm.to_mesh(mesh)
	bm.free()

	cube.display_type = 'BOUNDS'

	return cube


def Lattice(context, points_u: int=2, points_v: int=2, points_w: int=2, name='Lattice') -> bpy.types.Object:
	'''
	Create a lattice Object.
	'''

	data = bpy.data.lattices.new('Lattice')
	lattice = bpy.data.objects.new(name, data)
	context.collection.objects.link(lattice)

	data.points_u = points_u
	data.points_v = points_v
	data.points_w = points_w

	return lattice


# ===============
# OPERATOR 1
# ===============

class OBJECT_OT_armored_lattice(bpy.types.Operator):
	'''Creates a lattice that matches your object dimensions and transforms.

	armoredColony.com '''

	bl_idname = 'object.armored_lattice'
	bl_label  = 'ARMORED Lattice'
	bl_options = {'REGISTER', 'UNDO', 'PRESET'}

	orientation: bpy.props.EnumProperty(
		name='Orientation',
		default='LOCAL',
		items=[	('GLOBAL', 'Global', 'Align the lattice axes to world space'),
			('LOCAL',  'Local',  'Align the lattice axes to the selected/active object\'s local space'), ])

	points_u: bpy.props.IntProperty(
		name='U', default=2, min=2, max=24)

	points_v: bpy.props.IntProperty(
		name='V', default=2, min=2, max=24)

	points_w: bpy.props.IntProperty(
		name='W', default=2, min=2, max=24)

	parent: bpy.props.EnumProperty(
		name='Parent', 
		description='Which object is the parent',
		default='NONE',
		items=[	('LATTICE', 'Lattice', 'The Selected Objects are parented to the Lattice'),
			('ACTIVE',  'Active',  'The Lattice is parented to the Active Object'),
			('NONE',     'None',   'There is no parenting between the Lattice or your Selection'), ])

	scale_offset: bpy.props.FloatVectorProperty(
		name='Scale Offset', 
		#step=0.1, 
		description='Makes the lattice larger than the object')

	enter_edit: bpy.props.BoolProperty(
		default=True)
	
	lattice_name: bpy.props.StringProperty()

	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		col = layout.column(align=True)
		col.separator()
		
		row = col.row()
		row.prop(self, 'orientation', expand=True)
		col.separator()

		col.prop(self, 'points_u', text='Resolution U')
		col.prop(self, 'points_v')
		col.prop(self, 'points_w')
		col.separator()

		col.prop(self, 'parent')
		col.separator()

		# col.prop(self, 'scale_offset')
		# col.separator()

		col.operator('wm.operator_defaults', text='Reset')

	@classmethod
	def poll(cls, context):
		return context.selected_objects
	
	def invoke(self, context, event):
		bpy.ops.ed.undo_push()

		return self.execute(context)
	
	
	def execute(self, context):
		self.selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
		self.active_object    = self._get_active(context)	# Can return None.
		
		self.rotation_quaternion = self._get_rotation_quaternion(context)

		self.lattice = Lattice(context, self.points_u, self.points_v, self.points_w)

		if bpy.app.version >= (4, 1, 0):
			bounds_calculator = FromIndividualBoundingBoxes(self.selected_objects, self.rotation_quaternion)
		else:
			bounds_calculator = FromIndividualBoundingBoxesEvaluated(context, self.selected_objects, self.rotation_quaternion)

		# self.draw_individual_bounds(context)		# TEST
		self.lattice = LatticeDeformer(context, self.lattice, bounds_calculator).bl_object

		self._offset_lattice_scale()	# MUST REMAIN ABOVE THE SCENE UPDATE?
		self._set_parent()
		self._select_lattice(context)

		if self.enter_edit:
			bpy.ops.object.mode_set(mode='EDIT')
		
		return {'FINISHED'}


	# PRIVATE HELPERS >>
	
	def _get_active(self, context):	# sourcery skip: assign-if-exp, reintroduce-else
		if context.active_object not in self.selected_objects:
			return None

		return context.active_object
	
	def _get_rotation_quaternion(self, context) -> mathutils.Quaternion:
		'''
		Get the rotation for the lattice based on the specified selection/operator properties.
		'''

		if self.orientation == 'GLOBAL':
			return mathutils.Quaternion()
		
		active = self.active_object

		if active is None:	# Temporary adjustment, no need to change the real active object.
			active = self._get_largest_object()

		if active.rotation_mode == 'QUATERNION':
			return active.rotation_quaternion

		if active.rotation_mode == 'AXIS_ANGLE':
			return mathutils.Quaternion(mathutils.Vector(active.rotation_axis_angle).yzw, active.rotation_axis_angle[0])

		return active.rotation_euler.to_quaternion()
	
	def _get_largest_object(self) -> bpy.types.Object:
		return max(self.selected_objects, key=lambda obj: obj.dimensions.x * obj.dimensions.y * obj.dimensions.z)

	def _offset_lattice_scale(self) -> None:
		self.lattice.scale *= mathutils.Vector((1, 1, 1)) + mathutils.Vector(self.scale_offset)
	
	def _set_parent(self) -> None:
		self.lattice.matrix_world = self.lattice.matrix_basis 	# Update the matrix to save us a scene update.
		
		if self.parent == 'LATTICE':
			self._parent_objects(parent=self.lattice, children=self.selected_objects)

		elif self.parent == 'ACTIVE':
			self._parent_objects(parent=self.active_object, children=[self.lattice])

	def _parent_objects(self, parent, children) -> None:
		for obj in children:
			obj.parent = parent
			obj.matrix_parent_inverse = parent.matrix_world.inverted()
	
	def _select_lattice(self, context) -> None:
		for obj in self.selected_objects:
			obj.select_set(False)

		self.lattice.select_set(True)

		context.view_layer.objects.active = self.lattice


	# TESTS >>
	
	def draw_individual_bounds(self, context) -> None:
		for obj in self.selected_objects:
			bbox = WireCube(context)
			loc, rot, dim = FromIndividualBoundingBoxes([obj], self.rotation_quaternion).calculate_transforms()
			bbox.location = loc
			bbox.rotation_euler = rot
			bbox.dimensions = dim
			

# ===============
# OPERATOR 2
# ===============

class OBJECT_OT_armored_muscle_rig(bpy.types.Operator):
	'''Creates a lattice and hooks the control points to 3 Empties aligned vertically. Made to be used with vertical cyber muscle kitbash.

	armoredColony.com '''

	bl_idname = 'object.armored_muscle_rig'
	bl_label = 'ARMORED Muscle Rig'
	bl_options = {'REGISTER', 'UNDO'}

	points_u: bpy.props.IntProperty(
		name='U', default=2, min=2, max=24)

	points_v: bpy.props.IntProperty(
		name='V', default=2, min=2, max=24)

	points_w: bpy.props.IntProperty(
		name='W', default=3, min=2, max=24)
		
	group_controllers: bpy.props.BoolProperty(
		name='Group Controllers', default=True,
		description='Group the controllers in their own separate Collection',)

	hide_lattice: bpy.props.BoolProperty(
		name='Hide Lattice', default=True,)
	
	# parent: bpy.props.EnumProperty(
	# 	name='Parent', default='LARGEST', 
	# 	description='Set the ideal parent for your selection',
	# 	items=[ ('LARGEST', 'Largest', ''),
	# 		('ACTIVE',  'Active', ''), ])

	# hooks_in_editmode: BoolProperty(
	# 	name='Hook in Edit Mode', default=False,)
	
	empty_display_type: bpy.props.EnumProperty(
		name='Display As', default='PLAIN_AXES', 
		description='Viewport display style for the controllers',
		items=[ ('PLAIN_AXES', 'Plain Axes', ''),
			('CUBE',       'Cube',       ''),
			('SPHERE',     'Sphere',     ''), ])
	

	# @classmethod
	# def poll(cls, context):
	# 	return context.active_object is not None
	
	# def invoke(self, context, event):
	# 	bpy.ops.ed.undo_push()

	# 	return self.execute(context)

	def execute(self, context):
		self.selected_objects = self._get_selected_mesh_objects(context)
		self.active_object    = self._get_active_object(context)

		self.lattice     = self._create_lattice_object(context)
		self.controllers = self._create_empty_objects()

		self._reposition_empties()
		self._scale_empties()
		self._create_hooks()
		self._edit_hook_mod_settings()
		self._parent_original_selection_to_active_object()
		self._parent_empties_to_active_object()
		self._parent_lattice_to_active_object()	# MUST BE DONE AT THE END TO AVOID DEPENDENCY CYCLES?

		if self.group_controllers:
			self._move_controllers_to_collection()

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')

		context.view_layer.objects.active = self.active_object
		self.active_object.select_set(True)
		return {'FINISHED'}

	def _get_active_object(self, context) -> bpy.types.Object:
		'''
		Returns the object with the largest dimensions if the active is not part of the selection.
		'''

		if context.active_object not in context.selected_objects:
			return self._get_largest_object(context.selected_objects)
		
		return context.active_object
	
	def _get_selected_mesh_objects(self, context) -> list[bpy.types.Object]:
		return [obj for obj in context.selected_objects if obj.type == 'MESH']

	def _get_largest_object(self, objects: list[bpy.types.Object]) -> bpy.types.Object:
		return max(objects, key=lambda obj: obj.dimensions.x * obj.dimensions.y * obj.dimensions.z)

	def _create_lattice_object(self, context) -> bpy.types.Object:
		bpy.ops.object.armored_lattice(
			points_u=self.points_u, 
			points_v=self.points_v, 
			points_w=self.points_w, 
			parent='NONE'	# KEEP AT NONE AND DO PARENTING LATER
			)

		lattice = context.active_object
		lattice.name = f'{self.active_object.name}_Lattice'
		lattice.hide_set(self.hide_lattice)

		return lattice

	def _create_empty_objects(self) -> list[bpy.types.Object]:
		
		def _create_empty_object(name='Empty') -> bpy.types.Object:
			empty = bpy.data.objects.new(name, None)
			bpy.context.collection.objects.link(empty)

			empty.show_in_front = True
			empty.empty_display_type = self.empty_display_type

			return empty

		return [_create_empty_object(name=f'C{i}') for i in range(self.lattice.data.points_w)]
		
	def _reposition_empties(self) -> None:
		data = self.lattice.data
		points = data.points
		point_count = data.points_u * data.points_v
		matrix_world = self.lattice.matrix_world

		for i, obj in enumerate(self.controllers):
			start = i * point_count
			end = start + point_count
			obj.location = matrix_world @ (sum((p.co_deform for p in points[start:end]),  mathutils.Vector()) / point_count)	# MATRIX WORLD MULT MUST BE LAST
			obj.rotation_euler = self.lattice.rotation_euler

	def _scale_empties(self) -> None:
		scale = self.lattice.scale
		average_scale = (scale.x + scale.y) / 2 / 2 # NOT A TYPO

		for obj in self.controllers:
			obj.scale = [average_scale] * 3

	def _create_hooks(self) -> None:
		data = self.lattice.data
		points = data.points
		point_count = data.points_u * data.points_v

		for i, obj in enumerate(self.controllers):
			
			start = i * point_count
			end = start + point_count

			for j in range(start, end):
				points[j].select = True
			
			obj.select_set(True)
			bpy.ops.object.hook_add_selob(use_bone=False)
			obj.select_set(False)

			for j in range(start, end):
				points[j].select = False
			
	
	def _edit_hook_mod_settings(self) -> None:
		hook_modifiers = [mod for mod in self.lattice.modifiers if mod.type == 'HOOK']
		for mod in hook_modifiers:
			# mod.show_in_editmode = self.hooks_in_editmode
			mod.show_in_editmode = True
	
	def _parent_objects(self, objects: list[bpy.types.Object], parent: bpy.types.Object) -> None:
		for obj in objects:
			obj.parent = parent
			obj.matrix_parent_inverse = parent.matrix_world.inverted()
	
	def _parent_empties_to_active_object(self) -> None:
		self._parent_objects(objects=self.controllers, parent=self.active_object)
	
	def _parent_original_selection_to_active_object(self):
		selection_minus_active = self.selected_objects[:]
		selection_minus_active.remove(self.active_object)

		self._parent_objects(objects=selection_minus_active, parent=self.active_object)
	
	def _parent_lattice_to_active_object(self) -> None:
		self._parent_objects(objects=[self.lattice], parent=self.active_object)
	
	def _create_collection(self, name='Collection') -> bpy.types.Collection:
		collection = bpy.context.blend_data.collections.new(name=name)
		bpy.context.collection.children.link(collection)
		
		return collection

	def _move_controllers_to_collection(self) -> None:
		controller_collection = self._create_collection(name=f'{self.active_object.name} Controls')

		controllers = [self.lattice, *self.controllers]
		for obj in controllers:
			controller_collection.objects.link(obj)
			bpy.context.collection.objects.unlink(obj)


classes = (
	OBJECT_OT_armored_lattice,
	OBJECT_OT_armored_muscle_rig,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
