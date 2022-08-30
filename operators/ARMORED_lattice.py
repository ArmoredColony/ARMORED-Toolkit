# v3.0

import bpy
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatVectorProperty

from mathutils import Vector


def get_items(self, context):
	items = [ 
		('LATTICE',  'Lattice',  'The Selected objects are parented to the Lattice'),
		('ACTIVE',   'Active',   'The Lattice is Parented to the Active Object'),
		('NONE',      'None',    'The lattice is not parented with your selection in any way'),
	]
	
	if self.active_is_none:
		del items[1]

	return items


class ARMORED_OT_lattice(bpy.types.Operator):
	'''Creates a lattice that matches your object dimensions and transforms.

armoredColony.com '''

	bl_idname = 'object.armored_lattice'
	bl_label  = 'ARMORED Lattice'
	bl_options = {'REGISTER', 'UNDO'}

	resolution: IntProperty(
		name='Resolution', default=3, min=2)

	vertical_only: BoolProperty(
		name='Vertical Only', default=True, 
		description='Only increase the lattice resolution vertically')

	scale_offset: FloatVectorProperty(
		name='Scale Offset', 
		min=0, #step=0.1, 
		description='Makes the lattice larger than the object')
	
	zero_mesh_transforms: BoolProperty(
		name='Zero Mesh Transforms', default=False, 
		description='Clear all mesh transforms and transfer them to the lattice instead')
	
	parent: EnumProperty(
		name='Parent', #default='LATTICE', # Can't use this default since items come from a function?
		description='Which object is the parent',
		items=get_items)
	
	select_lattice: BoolProperty(
		default=True)

	enter_edit: BoolProperty(
		default=True)
	
	active_is_none: BoolProperty(
		default=False, options={'SKIP_SAVE', 'HIDDEN'})

	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		col = layout.column()
		col.prop(self, 'resolution')
		col.prop(self, 'vertical_only')
		col.separator()

		col.prop(self, 'scale_offset')
		col.separator()

		col.prop(self, 'parent')
		col.separator()

		col.operator('wm.operator_defaults', text='Reset')

	@classmethod
	def poll(cls, context):
		return context.selected_objects
	
	def execute(self, context):
		self.targets = context.selected_objects
		self.active = context.active_object

		if self.active not in self.targets:
			self.active_is_none = True

		if context.mode != 'OBJECT':
			bpy.ops.object.mode_set(mode='OBJECT')

		self.lattice = self._create_lattice()
		self._set_lattice_resolution()
		self._set_lattice_transforms()

		# Don't ask me why but we need something to trigger a scene update 
		# or parent matrix inversion will not apply.
		bpy.ops.object.select_all(action='DESELECT')

		self._set_parenting()
		self._add_lattice_modifier()

		if self.select_lattice:
			self._select_lattice(context)
			if self.enter_edit:
				bpy.ops.object.mode_set(mode='EDIT')

		return {'FINISHED'}
	

	def _create_lattice(self) -> bpy.types.Lattice:
		data = bpy.data.lattices.new('Lattice')
		lattice = bpy.data.objects.new('Lattice', data)
		bpy.context.collection.objects.link(lattice)

		return lattice

	def _set_lattice_resolution(self):
		data = self.lattice.data
		data.points_w = self.resolution

		if not self.vertical_only:
			data.points_u = self.resolution
			data.points_v = self.resolution
	
	def _set_lattice_transforms(self):
		bb_min, bb_max = self._selection_min_max_bounds()

		self.lattice.location = self._centroid([bb_min, bb_max])
		self.lattice.dimensions = self._vector_to_dimensions(vec1=bb_min, vec2=bb_max) + Vector(self.scale_offset)
		# self.lattice.rotation_euler = self.active.rotation_euler	# Does NOT work well with multiple selections.

	def _set_parenting(self):
		if self.parent == 'LATTICE':
			self._parent_selected_to_lattice()

		elif self.parent in {'ACTIVE', 'SELECTED'}:
			self._parent_lattice_to_active()

	def _parent_lattice_to_active(self):
		self.lattice.parent = self.active
		self.lattice.matrix_parent_inverse = self.active.matrix_world.inverted()
	
	def _parent_selected_to_lattice(self):
		for obj in self.targets:
			print(f'parenting {obj.name} to lattice')
			obj.parent = self.lattice
			obj.matrix_parent_inverse = self.lattice.matrix_world.inverted()

	def _add_lattice_modifier(self):
		for obj in self.targets:
			mod = obj.modifiers.new('Lattice', 'LATTICE')
			mod.object = self.lattice

	def _select_lattice(self, context):
		context.view_layer.objects.active = self.lattice
		self.lattice.select_set(True)

	def _centroid(self, coords: list[Vector]) -> Vector:
		'''Return the average of a list of coordinates.'''
		
		return sum((Vector(vec) for vec in coords), Vector()) / len(coords)
	
	def _vector_to_dimensions(self, vec1: Vector, vec2: Vector) -> Vector:
		'''Returns the world x, y, z dimensions of an imaginary bounding box formed by two 3d coordinates'''

		return Vector((abs(vec1.x - vec2.x), abs(vec1.y - vec2.y), abs(vec1.z - vec2.z)))

	def _selection_min_max_bounds(self) -> tuple[Vector, Vector]:
		'''Returns the Min and Max Vector corners of the imaginary bounding box surrounding the group of selected objects.'''

		bbox_coords = [obj.matrix_world @ Vector(point) for obj in bpy.context.selected_objects for point in obj.bound_box]

		return Vector(map(min, *bbox_coords)), Vector(map(max, *bbox_coords))
	


class OBJECT_OT_armored_muscle_rig(bpy.types.Operator):
	'''Creates a lattice and hooks the control points to 3 Empties aligned vertically. Made to be used with vertical cyber muscle kitbash.

armoredColony.com '''

	bl_idname = 'object.armored_muscle_rig'
	bl_label = 'ARMORED Muscle Rig'
	bl_options = {'REGISTER', 'UNDO'}
		
	group_controllers: BoolProperty(
		name='Group Controllers', default=False,
		description='Group the controllers in their own separate Collection',)

	hide_lattice: BoolProperty(
		name='Hide Lattice', default=False,)

	hooks_in_editmode: BoolProperty(
		name='Hook in Edit Mode', default=False,)
	
	empty_display_type: EnumProperty(
		name='Display As', default='PLAIN_AXES', 
		description='Viewport display style for the controllers',
		items=[ ('PLAIN_AXES', 'Plain Axes', ''),
			('CUBE',       'Cube',       ''),
			('SPHERE',     'Sphere',     ''), ])
	

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		self.target = context.active_object

		self.bot, self.mid, self.top = self._create_empties()

		context.view_layer.objects.active = self.target
		self.lattice = self._create_lattice()

		self._reposition_empties()
		self._scale_empties()
		self._create_hooks()
		self._edit_hook_mod_settings()
		self._parent_empties_to_mesh()
		self._parent_lattice_to_mesh()	# MUST BE DONE AT THE END TO AVOID DEPENDENCY CYCLES?

		if self.group_controllers:
			self._move_controllers_to_collection()

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')

		context.view_layer.objects.active = self.target
		self.target.select_set(True)
		return {'FINISHED'}
	

	def _create_lattice(self) -> bpy.types.Lattice:
		bpy.ops.object.armored_lattice(parent='NONE')	# KEEP AT NONE AND DO PARENTING SOMEWHERE ELSE
		lattice = bpy.context.active_object
		lattice.name = self.target.name + '_Lattice'
		lattice.hide_set(self.hide_lattice)	# This does NOT work correctly with the Redo Panel

		return lattice

	def _create_empties(self) -> tuple[bpy.types.Object]:
		
		def _create_empty_object(name='Empty') -> bpy.types.Object:
			empty = bpy.data.objects.new(name, None)
			bpy.context.collection.objects.link(empty)

			empty.show_in_front = True
			empty.empty_display_type = self.empty_display_type

			return empty
		
		top = _create_empty_object(name='Control Top')
		mid = _create_empty_object(name='Control Mid')
		bot = _create_empty_object(name='Control Bot')

		return bot, mid, top
	
	def _reposition_empties(self) -> None:
		points = self.lattice.data.points
		matrix_world = self.lattice.matrix_world
		# x = ((()))
		self.bot.location = matrix_world @ (sum((p.co_deform for p in points[ :4]),  Vector()) / 4)
		self.mid.location = matrix_world @ (sum((p.co_deform for p in points[4:8]),  Vector()) / 4)
		self.top.location = matrix_world @ (sum((p.co_deform for p in points[8:12]), Vector()) / 4)
	
	def _scale_empties(self) -> None:
		scale = self.lattice.scale
		average_scale = (scale.x + scale.y) / 2 / 2 # NOT A TYPO

		for obj in (self.bot, self.mid, self.top):
			obj.scale = [average_scale] * 3
	
	def _create_hooks(self) -> None:

		def _select_lattice_points(start: int, end: int, state: bool) -> None:
			for i in range(start, end+1):
				self.lattice.data.points[i].select = state
		
		def _clear_selected_lattice_points() -> None:
			for p in self.lattice.data.points:
				p.select = False
		
		def _hook_to_object(obj: bpy.types.Object) -> None:
			obj.select_set(True)
			bpy.ops.object.hook_add_selob(use_bone=False)

		_select_lattice_points(0, 3, True)
		_hook_to_object(self.bot)
		_clear_selected_lattice_points()

		_select_lattice_points(4, 7, True)
		_hook_to_object(self.mid)
		_clear_selected_lattice_points()

		_select_lattice_points(8, 11, True)
		_hook_to_object(self.top)
		_clear_selected_lattice_points()
	
	def _edit_hook_mod_settings(self) -> None:
		hook_modifiers = [mod for mod in self.lattice.modifiers if mod.type == 'HOOK']
		for mod in hook_modifiers:
			mod.show_in_editmode = self.hooks_in_editmode
	
	def _parent_empties_to_mesh(self) -> None:
		for empty in (self.bot, self.mid, self.top):
			empty.parent = self.target
			empty.matrix_parent_inverse = self.target.matrix_world.inverted()
	
	def _parent_lattice_to_mesh(self) -> None:
		self.lattice.parent = self.target
		self.lattice.matrix_parent_inverse = self.target.matrix_world.inverted()
	
	def _create_collection(self, name='Collection') -> bpy.types.Collection:
		collection = bpy.context.blend_data.collections.new(name=name)
		bpy.context.collection.children.link(collection)
		
		return collection

	def _move_controllers_to_collection(self):
		controller_collection = self._create_collection(name=self.target.name)
		controllers = [self.lattice, self.bot, self.mid, self.top]
		for element in controllers:
			controller_collection.objects.link(element)
			bpy.context.collection.objects.unlink(element)



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
