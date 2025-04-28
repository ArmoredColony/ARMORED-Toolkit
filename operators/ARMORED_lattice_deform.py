version = (5, 0, 0)

import bpy
import mathutils


# UTILS  __________________________________________________

def evaluate_objects(depsgraph:bpy.types.Depsgraph, objects: list[bpy.types.Object]) -> list[bpy.types.Object]:
	'''
	Returns a new list of depsgraph evaluated objects.
	'''

	evaluated_objects = []
	for obj in objects:
		if obj.modifiers:
			evaluated_objects.append(obj.evaluated_get(depsgraph))
		else:
			evaluated_objects.append(obj)

	return evaluated_objects


def find_largest_object(objects: list[bpy.types.Object]) -> bpy.types.Object:
	'''
	Returns the object with the largest volume (determined by dimensions).
	'''

	if not objects:
		return None
	
	return max(objects, key=lambda obj: obj.dimensions.x * obj.dimensions.y * obj.dimensions.z)


def calculate_object_bounds(
		objects: list[bpy.types.Object], 
		rotation: mathutils.Quaternion | mathutils.Matrix,
	) -> tuple[mathutils.Vector, mathutils.Vector]:
	'''
	Returns the minimum and maximum corners (vectors) of a bounding box that contains all input objects. 
	Uses each object's `bound_box` property for efficiency.
	'''
	
	vertex_coords = []
	for obj in objects:
		vertex_coords.extend(
			rotation.inverted() @ 
			(obj.matrix_world @ mathutils.Vector(point)) for point in obj.bound_box)
	
	return (
		mathutils.Vector(map(min, *vertex_coords)), # unpacking will give us the min of each individual axis.
		mathutils.Vector(map(max, *vertex_coords))
	)


def add_lattice_modifier(objects: list[bpy.types.Object], lattice: bpy.types.Object) -> None:
	'''
	Adds a lattice modifier to each object in the list.
	'''

	for obj in objects:
		mod = obj.modifiers.new(name='Lattice', type='LATTICE')
		mod.object = lattice


# BLENDER OBJECTS  __________________________________________________

def create_lattice_object(context, points_u: int=2, points_v: int=2, points_w: int=2, name='Lattice') -> bpy.types.Object:
	'''
	Create a lattice Object.
	'''

	data = bpy.data.lattices.new(name)
	lattice = bpy.data.objects.new(name, data)
	context.collection.objects.link(lattice)

	data.points_u = points_u
	data.points_v = points_v
	data.points_w = points_w

	return lattice
	

# LATTICE DEFORM OPERATOR __________________________________________________

class OBJECT_OT_armored_lattice(bpy.types.Operator):
	'''Creates a lattice that matches your object dimensions and transforms.

	armoredColony.com '''

	bl_idname = 'object.armored_lattice'
	bl_label  = 'ARMORED Lattice'
	bl_options = {'REGISTER', 'UNDO', 'PRESET'}

	orientation: bpy.props.EnumProperty(
		name='Orientation',
		default='LOCAL',
		items=[	
			('GLOBAL', 'Global', 'Align the lattice axes to world space'),
			('LOCAL',  'Local',  'Align the lattice axes to the selected/active object\'s local space'), 
		]
	)

	points_u: bpy.props.IntProperty(
		name='U', default=2, min=1, max=24)

	points_v: bpy.props.IntProperty(
		name='V', default=2, min=1, max=24)

	points_w: bpy.props.IntProperty(
		name='W', default=2, min=1, max=24)
	
	parent_to_lattice: bpy.props.BoolProperty(
		name='Parent to Lattice', default=False)

	offset_transforms: bpy.props.BoolProperty(
		name='Offset Transforms', default=False,
		description='Use offsets to adjust the lattice transforms.'
	)

	scale_offset: bpy.props.FloatVectorProperty(
		name='Scale Offset', 
		description='Makes the lattice bigger or smaller'
	)

	enter_edit: bpy.props.BoolProperty(
		default=True)
	
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

		col.prop(self, 'offset_transforms', text='Use Offset')
		if self.offset_transforms:
			col.prop(self, 'scale_offset')
			col.separator()

		col.prop(self, 'parent_to_lattice')
		col.separator()

		col.prop(self, 'enter_edit', text='Enter Edit Mode')
		col.separator()

		col.operator('wm.operator_defaults', text='Reset')
	
	@classmethod
	def poll(cls, context):
		return context.selected_objects
	
	def execute(self, context):
		selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
		active_object = self._get_active(context, selected_objects)
		
		evaluated_objects = evaluate_objects(
			depsgraph = context.evaluated_depsgraph_get(), 
			objects   = selected_objects,
		)

		rotation_quaternion = self._get_rotation_quaternion(
			active_object     = active_object, 
			evaluated_objects = evaluated_objects
		)

		bounds_min, bounds_max = calculate_object_bounds(
			objects  = evaluated_objects,
			rotation = rotation_quaternion,
		)
		
		lattice = create_lattice_object(context, self.points_u, self.points_v, self.points_w)
		lattice.location       = rotation_quaternion @ (bounds_min + bounds_max) / 2	 # No need for abs since max is always greater.
		lattice.rotation_euler = rotation_quaternion.to_euler()
		lattice.dimensions     = bounds_max - bounds_min

		# Optional scale offset defined by the user.
		lattice.scale *= mathutils.Vector(self.scale_offset) + mathutils.Vector((1, 1, 1))

		add_lattice_modifier(objects=selected_objects, lattice=lattice)

		if self.parent_to_lattice:
			self._parent_to_lattice(objects=selected_objects, lattice=lattice)
			
		self._select_lattice(context, deselect_objects=selected_objects, lattice=lattice)

		if self.enter_edit:
			bpy.ops.object.mode_set(mode='EDIT')
		
		return {'FINISHED'}


	# PRIVATE HELPERS >>
	
	def _get_active(self, context, selected_objects: list[bpy.types.Object]) -> bpy.types.Object:
		if context.active_object not in selected_objects:
			return None

		return context.active_object
	
	def _get_rotation_quaternion(self, active_object, evaluated_objects) -> mathutils.Quaternion:
		'''
		Return the quaternion rotation of the active object when in LOCAL space,
		and fallback to the largest object's rotation when the active is not available.
		'''

		if self.orientation == 'GLOBAL':
			return mathutils.Quaternion()
			
		# LOCAL OPTIONS  __________________________________________________

		if active_object is None:
			active_object = find_largest_object(evaluated_objects)

		if active_object.rotation_mode == 'QUATERNION':
			return active_object.rotation_quaternion

		elif active_object.rotation_mode == 'AXIS_ANGLE':
			return mathutils.Quaternion(
				mathutils.Vector(active_object.rotation_axis_angle).yzw, active_object.rotation_axis_angle[0])
			
		return active_object.rotation_euler.to_quaternion()
	
	def _parent_to_lattice(self, objects, lattice) -> None:
		lattice.matrix_world = lattice.matrix_basis 	# Update the matrix to save us a scene update.

		for obj in objects:
			obj.parent = lattice
			obj.matrix_parent_inverse = lattice.matrix_world.inverted()

	def _select_lattice(self, context, deselect_objects, lattice) -> None:
		'''
		Deselect the specified objects and select the lattice and make it active.
		'''
		
		for obj in deselect_objects:
			obj.select_set(False)

		lattice.select_set(True)

		context.view_layer.objects.active = lattice


# MUSCLE RIG OPERATOR  __________________________________________________

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
			parent_to_lattice=False,
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
