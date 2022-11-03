# v4.0

import bpy
import bmesh

from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatVectorProperty, StringProperty
from mathutils import Vector, Quaternion

from abc import ABC, abstractmethod


class BoundsCalculator(ABC):
	'''
	Abstract Base Class for calculating the location, rotation and dimensions of a bounding box.
	'''

	@abstractmethod
	def calculate_location(self):
		pass

	@abstractmethod
	def calculate_rotation(self):
		pass

	@abstractmethod
	def calculate_dimensions(self):
		pass

	def calculate_transforms(self) -> tuple[Vector, Vector, Vector]:
		loc = self.calculate_location()
		rot = self.calculate_rotation()
		dim = self.calculate_dimensions()

		return loc, rot, dim


class FromIndividualBoundingBoxes(BoundsCalculator):
	'''
	Calculate the transforms of a bounding box around the selected objects, based on their individual bounding boxes  
	and the active object's rotation as world space.
	'''

	def __init__(self, selected_objects: list[bpy.types.Object], active_object: bpy.types.Object=None) -> None:
		self.selected_objects = selected_objects
		self.active_object = active_object

		self.rotation_quaternion = self._get_quaternion_from_active()
		self.bounds_min, self.bounds_max = self._get_min_max_vectors_from_bounds()
		
	def calculate_location(self) -> Vector:
		return self.rotation_quaternion @ ((self.bounds_min + self.bounds_max) / 2)

	def calculate_rotation(self) -> Vector:
		if self.active_object is None:
			return Vector((0, 0, 0))

		return self.active_object.rotation_euler

	def calculate_dimensions(self) -> Vector:
		return self._get_dimensions_from_min_max_bounds()
	

	# PRIVATE HELPERS >>

	def _get_quaternion_from_active(self) -> Quaternion:
		if self.active_object is None:
			return Quaternion()

		old_mode = self.active_object.rotation_mode
		self.active_object.rotation_mode = 'QUATERNION'		# SWITCHING TO QUAT ROTATION MODE AND BACK SEEMS ENOUGH 
		self.active_object.rotation_mode = old_mode		# TO TRIGGER THE QUATERNION CALCULATION IN BLENDER
		
		return self.active_object.rotation_quaternion
	
	def _get_dimensions_from_min_max_bounds(self) -> Vector:
		'''
		Returns (x, y, z): Vector dimensions of a bounding box based on 2 opposite corners.
		'''

		return Vector((
			abs(self.bounds_min.x - self.bounds_max.x), 
			abs(self.bounds_min.y - self.bounds_max.y), 
			abs(self.bounds_min.z - self.bounds_max.z)
			))
	
	def _get_min_max_vectors_from_bounds(self) -> tuple[Vector, Vector]:

		'''
		Returns (min: Vector, max: Vector) corners of a bounding box around the selected objects.
		'''

		vertex_coords = []
		for obj in self.selected_objects:
			vertex_coords.extend(
				self.rotation_quaternion.inverted() @ 
				(obj.matrix_world @ Vector(point)) for point in obj.bound_box)
		
		return Vector(map(min, *vertex_coords)), Vector(map(max, *vertex_coords))	# NOT SURE WHY THIS WORKS


class FromIndividualBoundingBoxesDepsgraph(FromIndividualBoundingBoxes):
	'''
	Calculate the transforms of a bounding box around the selected objects, based on their individual bounding boxes  
	and the active object's rotation as world space (uses Evaluated Depsgraph).
	'''

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
				self.rotation_quaternion.inverted() @ 
				(obj.matrix_world @ Vector(point)) for point in obj.bound_box)
		
		return Vector(map(min, *vertex_coords)), Vector(map(max, *vertex_coords))	# NOT SURE WHY THIS WORKS


# ===============
# COMPOSITOR CLASS
# ===============

class LatticeDeformer:
	'''
	Transform a Lattice to encapsulate the selected objects and create the necessary deform modifiers.
	'''

	def __init__(self, lattice: bpy.types.Object, bounds_calculator: BoundsCalculator) -> None:
		self.lattice = lattice
		self.bounds_calculator = bounds_calculator
		self.selected_objects = bounds_calculator.selected_objects

		self.loc, self.rot, self.dim = self.bounds_calculator.calculate_transforms()

	def new(self) -> bpy.types.Object:
		self._set_transforms()
		self._add_modifiers()

		return self.lattice
	

	# PRIVATE HELPERS

	def _set_transforms(self) -> None:
		self.lattice.location       = self.loc
		self.lattice.rotation_euler = self.rot
		self.lattice.dimensions     = self.dim
	
	def _add_modifiers(self) -> None:
		for obj in self.selected_objects:
			mod = obj.modifiers.new(name='Lattice', type='LATTICE')
			mod.object = self.lattice


# ===============
# BLENDER OBJECTS
# ===============

def WireCube() -> bpy.types.Object:
	'''
	Create a Wireframe Cube.
	'''

	mesh = bpy.data.meshes.new('Cube')
	cube = bpy.data.objects.new('Cube', mesh)
	bpy.context.collection.objects.link(cube)

	bm = bmesh.new()
	bmesh.ops.create_cube(bm, size=2, calc_uvs=False)
	bm.to_mesh(mesh)
	bm.free()

	cube.display_type = 'BOUNDS'

	return cube


def Lattice(points_u: int=2, points_v: int=2, points_w: int=2, name='Lattice') -> bpy.types.Object:
	'''
	Create a lattice Object.
	'''

	data = bpy.data.lattices.new('Lattice')
	lattice = bpy.data.objects.new(name, data)
	bpy.context.collection.objects.link(lattice)

	data.points_u = points_u
	data.points_v = points_v
	data.points_w = points_w

	return lattice


# ===============
# DYNAMIC ENUM
# ===============
	
def get_items(self, context):
	items = [ 
			('LATTICE',  'Lattice',  'The Selected Objects are parented to the Lattice'),
			('ACTIVE',   'Active',   'The Lattice is parented to the Active Object'),
			('NONE',      'None',    'There is no parenting between the Lattice or your Selection'),
		]
	
	if not self.show_rotation_property:
		del items[1]

	return items


# ===============
# OPERATOR 1
# ===============

class ARMORED_OT_lattice(bpy.types.Operator):
	'''Creates a lattice that matches your object dimensions and transforms.

armoredColony.com '''

	bl_idname = 'object.armored_lattice'
	bl_label  = 'ARMORED Lattice'
	bl_options = {'REGISTER', 'UNDO', 'PRESET'}

	points_u: IntProperty(
		name='U', default=2, min=2, max=24)

	points_v: IntProperty(
		name='V', default=2, min=2, max=24)

	points_w: IntProperty(
		name='W', default=3, min=2, max=24)

	scale_offset: FloatVectorProperty(
		name='Scale Offset', 
		#step=0.1, 
		description='Makes the lattice larger than the object')
	
	rotate_to_active: BoolProperty(
		name='Rotate to Active', default=True, 
		description='Rotate the Lattice to match the Active Object')
	
	parent: EnumProperty(
		name='Parent', 
		# default= 	# I do not know how to set a default when items come from function.
		description='Which object is the parent',
		items=get_items)

	enter_edit: BoolProperty(
		default=True)
	
	# Controls the visibility of the 'rotate_to_active' property in the Redo Panel.
	show_rotation_property: BoolProperty(
		default=True, options={'SKIP_SAVE', 'HIDDEN'})
	
	warning: StringProperty(
		default='', options={'SKIP_SAVE', 'HIDDEN'})

	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		col = layout.column(align=True)
		col.separator()

		if self.warning:
			col.label(text=self.warning)
			col.separator()

		col.prop(self, 'points_u', text='Resolution U')
		col.prop(self, 'points_v')
		col.prop(self, 'points_w')
		col.separator()

		col.prop(self, 'parent')
		col.separator()

		if self.show_rotation_property:
			col.prop(self, 'rotate_to_active')
			col.separator()

		col.prop(self, 'scale_offset')
		col.separator()

		col.operator('wm.operator_defaults', text='Reset')

	@classmethod
	def poll(cls, context):
		return context.selected_objects
	
	def invoke(self, context, event):
		bpy.ops.ed.undo_push()

		return self.execute(context)
	
	def execute(self, context):
		self.selected_objects = context.selected_objects
		self.active_object    = self._get_active(context)	# Can return None.

		if self._selected_objects_have_modifiers():
			self._set_warning_message()

		if context.mode != 'OBJECT':
			bpy.ops.object.mode_set(mode='OBJECT')

		lattice_object = Lattice(self.points_u, self.points_v, self.points_w)
		bounds_calculator = FromIndividualBoundingBoxesDepsgraph(self.selected_objects, self.active_object)

		# self.draw_individual_bounds()		# TEST
		self.lattice = LatticeDeformer(lattice_object, bounds_calculator).new()

		self._offset_lattice_scale()	# MUST REMAIN ABOVE THE SCENE UPDATE?
		self._set_parent()
		self._select_lattice(context)

		if self.enter_edit:
			bpy.ops.object.mode_set(mode='EDIT')
		
		return {'FINISHED'}


	# PRIVATE HELPERS >>

	def _selected_objects_have_modifiers(self) -> bool:
		return any(obj.modifiers for obj in self.selected_objects)
	
	def _set_warning_message(self):
		self.warning = 'Heavy modifiers can slow this script!'
	
	def _get_active(self, context):
		if context.active_object not in context.selected_objects:
			self.show_rotation_property = False
			return None

		if not self.rotate_to_active:
			return None
		
		return context.active_object

	def _offset_lattice_scale(self):
		self.lattice.scale *= Vector((1, 1, 1)) + Vector(self.scale_offset)
	
	def _set_parent(self):
		self.lattice.matrix_world = self.lattice.matrix_basis 	# Update the matrix to save us a scene update.

		if self.parent == 'LATTICE':
			self._parent_objects(parent=self.lattice, children=self.selected_objects)

		elif self.parent == 'ACTIVE':
			self._parent_objects(parent=self.active_object, children=[self.lattice])

	def _parent_objects(self, parent, children):
		for obj in children:
			obj.parent = parent
			obj.matrix_parent_inverse = parent.matrix_world.inverted()
	
	def _select_lattice(self, context):
		for obj in self.selected_objects:
			obj.select_set(False)

		self.lattice.select_set(True)
		context.view_layer.objects.active = self.lattice

	# TESTS >>
	
	def draw_individual_bounds(self) -> None:
		for obj in self.selected_objects:
			bbox = WireCube()
			loc, rot, dim = FromIndividualBoundingBoxes([obj], self.active_object).calculate_transforms()
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

	points_u: IntProperty(
		name='U', default=2, min=2, max=24)

	points_v: IntProperty(
		name='V', default=2, min=2, max=24)

	points_w: IntProperty(
		name='W', default=3, min=2, max=24)
		
	group_controllers: BoolProperty(
		name='Group Controllers', default=True,
		description='Group the controllers in their own separate Collection',)

	hide_lattice: BoolProperty(
		name='Hide Lattice', default=True,)

	# hooks_in_editmode: BoolProperty(
	# 	name='Hook in Edit Mode', default=False,)
	
	empty_display_type: EnumProperty(
		name='Display As', default='PLAIN_AXES', 
		description='Viewport display style for the controllers',
		items=[ ('PLAIN_AXES', 'Plain Axes', ''),
			('CUBE',       'Cube',       ''),
			('SPHERE',     'Sphere',     ''), ])
	

	# @classmethod
	# def poll(cls, context):
	# 	return context.active_object is not None
	
	def invoke(self, context, event):
		bpy.ops.ed.undo_push()

		return self.execute(context)

	def execute(self, context):
		self.target = context.active_object
		self.lattice = self._create_lattice(context)
		self.controllers = self._create_empties()

		self._reposition_empties()
		self._scale_empties()
		self._create_hooks()
		# self._edit_hook_mod_settings()
		self._parent_empties_to_mesh()
		self._parent_lattice_to_mesh()	# MUST BE DONE AT THE END TO AVOID DEPENDENCY CYCLES?

		if self.group_controllers:
			self._move_controllers_to_collection()

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')

		context.view_layer.objects.active = self.target
		self.target.select_set(True)
		return {'FINISHED'}
	

	def _create_lattice(self, context) -> bpy.types.Lattice:
		bpy.ops.object.armored_lattice(
			points_u=self.points_u, 
			points_v=self.points_v, 
			points_w=self.points_w, 
			parent='NONE'	# KEEP AT NONE AND DO PARENTING LATER
			)

		lattice = context.active_object
		lattice.name = f'{self.target.name}_Lattice'
		lattice.hide_set(self.hide_lattice)

		return lattice

	def _create_empties(self) -> list[bpy.types.Object]:
		
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
			obj.location = matrix_world @ sum((p.co_deform for p in points[start:end]),  Vector()) / point_count
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
			mod.show_in_editmode = self.hooks_in_editmode
	
	def _parent_empties_to_mesh(self) -> None:
		for controller in self.controllers:
			controller.parent = self.target
			controller.matrix_parent_inverse = self.target.matrix_world.inverted()
	
	def _parent_lattice_to_mesh(self) -> None:
		self.lattice.parent = self.target
		self.lattice.matrix_parent_inverse = self.target.matrix_world.inverted()
	
	def _create_collection(self, name='Collection') -> bpy.types.Collection:
		collection = bpy.context.blend_data.collections.new(name=name)
		bpy.context.collection.children.link(collection)
		
		return collection

	def _move_controllers_to_collection(self) -> None:
		controller_collection = self._create_collection(name=f'{self.target.name} Controls')

		controllers = [self.lattice, *self.controllers]
		for obj in controllers:
			controller_collection.objects.link(obj)
			bpy.context.collection.objects.unlink(obj)



classes = (
	ARMORED_OT_lattice,
	OBJECT_OT_armored_muscle_rig,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
