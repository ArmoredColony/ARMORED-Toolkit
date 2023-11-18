version = (3, 3, 0)

import bpy
import blf
import gpu

import mathutils
import bpy_extras
import gpu_extras

import math
import dataclasses
import itertools

	
class IntConcatenator:
	'''
	Concatenates numeric key inputs into a single integer (made to be used with keyboard events).
	EXAMPLE: Keypressing 1 and then 2 creates the int 12. Can set up the BACKSPACE event to remove the last digit and go back to 1.
	'''

	def __init__(self, empty_default: int=0, element_cap: int=3) -> None:
		self.empty_default = empty_default
		self.element_cap = element_cap
		self.list_of_integers = []
	
	@property
	def result(self):
		if not self.list_of_integers:
			return self.empty_default
			
		return int(''.join(map(str, self.list_of_integers)))
	
	def append(self, value):
		if len(self.list_of_integers) >= self.element_cap:
			return self.result
			
		self.list_of_integers.append(value)

		return self.result
	
	# @property
	def pop(self):
		if self.list_of_integers:
			self.list_of_integers.pop()
			
		return self.result


class EVENTS:

	PASS_THROUGH = {'MIDDLEMOUSE', 'NUMPAD_PERIOD', 'F'}
	INCREASE     = {'WHEELUPMOUSE',   'NUMPAD_PLUS',  'PAGE_UP',   'UP_ARROW'}
	DECREASE     = {'WHEELDOWNMOUSE', 'NUMPAD_MINUS', 'PAGE_DOWN', 'DOWN_ARROW'}
	SCALE        = {'S'}
	ROTATE       = {'R'}
	CANCEL       = {'RIGHTMOUSE', 'ESC'}
	FINISH       = {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER', 'SPACE', 'TAB'}

	BACK_SPACE   = {'BACK_SPACE'}

	ALT          = {'LEFT_ALT',   'RIGHT_ALT'}
	SHIFT        = {'LEFT_SHIFT', 'RIGHT_SHIFT'}
	CTRL         = {'LEFT_CTRL',  'RIGHT_CTRL'}

	NUMBER = {
		'ONE'   : 1,
		'TWO'   : 2,
		'THREE' : 3,
		'FOUR'  : 4,
		'FIVE'  : 5,
		'SIX'   : 6,
		'SEVEN' : 7,
		'EIGHT' : 8,
		'NINE'  : 9,
		'ZERO'  : 0,

		'NUMPAD_1' : 1,
		'NUMPAD_2' : 2,
		'NUMPAD_3' : 3,
		'NUMPAD_4' : 4,
		'NUMPAD_5' : 5,
		'NUMPAD_6' : 6,
		'NUMPAD_7' : 7,
		'NUMPAD_8' : 8,
		'NUMPAD_9' : 9,
		'NUMPAD_0' : 0,
	}


@dataclasses.dataclass(frozen=False)
class InputData:
	'''
	Info about the Node and inputs we wish to tweak with modal events.
	'''

	node_name: str
	input_indexes: tuple[int]
	prop_name: str

	offset: int = 0		# The offset required for the user-controlled property to match the 
				# `input.default_value` of whatever node was used to create the geometry.
				# EXAMPLE: the user creates a plane by specifying how many Cuts. 
				# 1 Cut requires 3 vertices in the MeshGrid node, so the offset should be 2

	node: bpy.types.GeometryNode          = NotImplemented
	inputs: list[bpy.types.NodeSocketInt] = NotImplemented


@dataclasses.dataclass(frozen=False)
class NodeData:
	'''
	<bpy.types.GeometryNode> with extra information.
	'''

	name: str
	type: str
	
	defaults: dict = None	# NOTE: USER-CONTROLLED PROPERTIES SHOULD BE DEFINED BY OPERATOR PROPERTIES.
				# This is used to change any default node values we don't like (EXAMPLE: the starting dimensions of a plane).

class GeometryData:
	
	NODE_DATA  = NotImplemented	# List of NodeData.
	LINK_DATA  = NotImplemented	# List of tuple(node_name, output_index, node_name, input_index).
	INPUT_DATA = NotImplemented	# Dict of bool: InputData.


class VERTEX_DATA(GeometryData):
	
	NODE_DATA = [
			NodeData(name='Mesh Line', type='GeometryNodeMeshLine'),
		]

	LINK_DATA = [
			('Mesh Line', 0, 'Group Output', 0),
		]
	
	INPUT_DATA = {
			False: InputData(prop_name='points', node_name='Mesh Line', input_indexes=(0,)),
		}
	

class CIRCLE_DATA(GeometryData):
	
	NODE_DATA = [
			NodeData(name='Mesh Circle', type='GeometryNodeMeshCircle', defaults={1: 2}),	# Radius of 2.
			NodeData(name='Transform', type='GeometryNodeTransform'),
		]

	LINK_DATA = [
			('Mesh Circle', 0, 'Transform', 0),
			('Transform', 0, 'Group Output', 0),
		]
	
	INPUT_DATA = {
			False: InputData(prop_name='sides', node_name='Mesh Circle', input_indexes=(0,), offset=0),
		}


class PLANE_DATA(GeometryData):
	
	NODE_DATA = [
			NodeData(name='Plane', type='GeometryNodeMeshGrid', defaults={0: 2, 1: 2}),
			NodeData(name='Transform', type='GeometryNodeTransform'),
		]

	LINK_DATA = [
			('Plane', 0, 'Transform', 0),
			('Transform', 0, 'Group Output', 0),
		]
	
	INPUT_DATA = {
			False: InputData(prop_name='cuts', node_name='Plane', input_indexes=(2, 3), offset=2),
		}


class CUBE_DATA(GeometryData):
	
	NODE_DATA = [
			NodeData(name='Cube', type='GeometryNodeMeshCube', defaults={0: mathutils.Vector((2, 2, 2))}),
			NodeData(name='Transform', type='GeometryNodeTransform'),
		]

	LINK_DATA = [
			('Cube', 0, 'Transform', 0),
			('Transform', 0, 'Group Output', 0),
		]
	
	INPUT_DATA = {
			False: InputData(prop_name='cuts', node_name='Cube', input_indexes=(1, 2, 3), offset=2),
		}


class CYLINDER_DATA(GeometryData):
	
	NODE_DATA = [
			NodeData(name='Cylinder', type='GeometryNodeMeshCylinder'),
			NodeData(name='Transform', type='GeometryNodeTransform'),
		]

	LINK_DATA = [
			('Cylinder', 0, 'Transform', 0),
			('Transform', 0, 'Group Output', 0),
		]
	
	INPUT_DATA = {
			False: InputData(prop_name='sides', node_name='Cylinder', input_indexes=(0,)),
			True:  InputData(prop_name='cuts', node_name='Cylinder', input_indexes=(1,), offset=1),
		}


class QUADSPHERE_DATA(GeometryData):
	
	NODE_DATA = [
			NodeData(name='Cube', type='GeometryNodeMeshCube', defaults={0: mathutils.Vector((2, 2, 2))}),
			NodeData(name='SubD', type='GeometryNodeSubdivisionSurface'),
			NodeData(name='Transform', type='GeometryNodeTransform'),
		]

	LINK_DATA = [
			('Cube', 0, 'SubD', 0),
			('SubD', 0, 'Transform', 0),
			('Transform', 0, 'Group Output', 0),
		]
	
	INPUT_DATA = {
			False: InputData(prop_name='subdivisions', node_name='SubD', input_indexes=[1]),
		}


def fill_missing_data(input_data, nodes: list[bpy.types.GeometryNode]):
	'''
	Fill out missing <node> and <inputs> properties in the input_data: dataclass by using 
	<node_name> and <input_indexes> as keys on the <node_tree.nodes>.
	'''

	for _input_data in input_data.values():
		_input_data.node = nodes.get(_input_data.node_name)
		_input_data.inputs = [_input_data.node.inputs[i] for i in _input_data.input_indexes]
	
	return input_data


class EventManager:
	'''
	ABSTRACT CLASS: Run methods based on modal events.
	'''
	
	def event(self, event):
		self.any(event)

		if event.type == 'MOUSEMOVE':
			self.mousemove(event)
			
		if event.type in EVENTS.PASS_THROUGH:
			return {'PASS_THROUGH'}

		if event.type in EVENTS.SCALE and event.value == 'PRESS':
			self.scale(event)

		if event.type in EVENTS.INCREASE and event.value == 'PRESS':
			self.increase(event)
		
		if event.type in EVENTS.DECREASE and event.value == 'PRESS':
			self.decrease(event)
		
		if event.type in EVENTS.NUMBER and event.value == 'PRESS':
			self.number(event, EVENTS.NUMBER.get(event.type))
		
		if event.type in EVENTS.BACK_SPACE and event.value == 'PRESS':
			self.backspace(event)
		
		if event.type in EVENTS.ROTATE and event.value == 'PRESS':
			self.rotate(event)
		
		if event.type in EVENTS.CANCEL:
			self.reset(event)
			self.cancel(event)
			return {'CANCELLED'}

		if event.type in EVENTS.FINISH:
			self.finish(event)
			return {'FINISHED'}
		
		return {'RUNNING_MODAL'}


	# COMMON EVENTS

	def any(self, event):
		pass
	
	def mousemove(self, event):
		pass

	def increase(self, event):
		pass
	
	def decrease(self, event):
		pass
	
	def number(self, event, number):
		pass
	
	def backspace(self, event):
		pass
	
	def reset(self, event):
		pass
	

	# TRANSFORMS

	def scale(self, event):
		pass

	def rotate(self, event):
		pass


	# OPERATOR CONTROL

	def cancel(self, event):
		pass

	def finish(self, event):
		pass


#####################
# GENERATORS
#####################

class GeometryGenerator(EventManager):
	'''
	Some way of generating Blender Meshes in the scene.
	'''

	pass


class NodeGeometry(GeometryGenerator):
	'''
	ABSTRACT CLASS: Create Geometry using Nodes.
	'''

	def __init__(self, operator, context, node_data, link_data):
		self.operator = operator
		self.context = context
		self.node_data = node_data
		self.link_data = link_data

		self.node_container = self._create_node_container_object()
		self.node_container.show_wire = True

		self.location = self.node_container.location

		self.mod_name      = f'NodeGeometry_{hash("NodeGeometry")}'
		self.node_modifier = self._create_geometry_nodes_modifier()
		self.node_tree     = self.node_modifier.node_group
		self.nodes         = self.node_tree.nodes

		self.align_to_cursor = itertools.cycle((True, False))

		self._create_nodes()
		self._link_nodes()
		self.rotate(event=None)



	def _create_node_container_object(self):
		bpy.ops.mesh.primitive_cube_add()

		return self.context.active_object
	
	def _create_geometry_nodes_modifier(self) -> bpy.types.Modifier:
		mod = self.node_container.modifiers.new(name=self.mod_name, type='NODES')

		if mod.node_group is None:
			bpy.ops.node.new_geometry_node_group_assign()	# because 3.2 does NOT assign a blank node group by default
		
		return mod
	
	def _create_nodes(self):

		for node_data in self.node_data:
			node = self.node_tree.nodes.new(node_data.type)
			node.name = node_data.name

			# This will not really affect user-controlled inputs, 
			# because those will be overriden by the NodeEditor class immediately after.
			if node_data.defaults is None:
				continue

			for key, val in node_data.defaults.items():
				node.inputs[key].default_value = val

		
	def _link_nodes(self):
		
		for male_node_name, output_index, female_node_name, input_index in self.link_data:
			male_node   = self.node_tree.nodes.get(male_node_name)
			female_node = self.node_tree.nodes.get(female_node_name)

			if male_node is None or female_node is None:
				raise ValueError(f'You cannot link node {male_node} to node {female_node}')

			self.node_tree.links.new(male_node.outputs[output_index], female_node.inputs[input_index])


	# TRANSFORMS

	def rotate(self, event):
		# We do the initial rotation on the Node Container bl_object instead of the Transform node in the Node Editor Class
		# because we want to keep the rotation after the geometry nodes modifier is applied.

		if next(self.align_to_cursor):
			self.node_container.rotation_euler = self.context.scene.cursor.rotation_euler
		else:
			self.node_container.rotation_euler = (0, 0, 0)


	# OPERATOR CONTROL

	# def tab(self, event):
	# 	self.finish(event)
	
	def cancel(self, event):
		self._cleanup()

	def finish(self, event):
		self._cleanup()
		
		if event.type == 'TAB':
			bpy.ops.object.mode_set(mode='EDIT')
		
		self.operator.post_function(self.context) # EMPTY FUNCTION. OVERRIDE IN OPERATOR SUBCLASS.
	
	def _cleanup(self):
		bpy.ops.object.modifier_apply(modifier=self.mod_name)
		self.node_container.show_wire = False
		bpy.data.node_groups.remove(self.node_tree)
		# bpy.ops.object.mode_set(mode='EDIT')
	

#####################
# EDITORS
#####################

class GeometryEditor(EventManager):
	'''
	Some way to edit geometry in the scene.
	'''
	
	pass


class NodeEditor(GeometryEditor):
	'''
	ABSTRACT CLASS: Edit GeometryNode Inputs.
	'''
	
	def __init__(self, operator, context, geometry_origin: mathutils.Vector, nodes: list[bpy.types.GeometryNode], input_data) -> None:
		self.operator = operator
		self.context = context
		self.geometry_origin = geometry_origin
		self.nodes = nodes
		self.input_data = fill_missing_data(input_data, self.nodes)

		self._set_node_input_defaults()

		self.scaling = False

		self.property_value = IntConcatenator(0)

	def _set_node_input_defaults(self):  # sourcery skip: assign-if-exp
		for input_data in self.input_data.values():
			val = getattr(self.operator, input_data.prop_name)

			for node_input in input_data.inputs:
				if isinstance(node_input.default_value, mathutils.Vector):
					node_input.default_value = mathutils.Vector.Fill(len(node_input.default_value), val)
				else:
					node_input.default_value = val
		
		transform_node = self.nodes.get('Transform')
		if transform_node is None:
			return
		
		scale_amount = getattr(self.operator, 'scale', None)
		if scale_amount is None:
			return
		
		scale_input = transform_node.inputs[3]
		scale_amount = scale_amount
		scale_input.default_value = scale_amount
	
	def _scroll(self, event, increment: int):
		input_data = self.input_data.get(event.alt)
		if input_data is None:
			return
			
		setattr(self.operator, input_data.prop_name, getattr(self.operator, input_data.prop_name) + increment)
		for input in input_data.inputs:
			input.default_value = getattr(self.operator, input_data.prop_name)
	
	def increase(self, event):
		self._scroll(event, increment=1)

	def decrease(self, event):
		self._scroll(event, increment=-1)

	def number(self, event, number: int):
		input_data = self.input_data.get(event.alt)
		if input_data is None:
			return
		
		self.property_value.append(number)

		setattr(self.operator, input_data.prop_name, self.property_value.result + input_data.offset)
		for input in input_data.inputs:
			input.default_value = getattr(self.operator, input_data.prop_name)
	
	def backspace(self, event):
		input_data = self.input_data.get(event.alt)
		if input_data is None:
			return

		self.property_value.pop()

		setattr(self.operator, input_data.prop_name, self.property_value.result + input_data.offset)
		for input in input_data.inputs:
			input.default_value = getattr(self.operator, input_data.prop_name)
	

	# TRANSFORMS

	def mousemove(self, event):
		self.mouse_position = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
		self.geometry_origin_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(
				self.context.region, self.context.space_data.region_3d, self.geometry_origin)

		if not self.scaling:
			return
		
		transform_node = self.nodes.get('Transform')
		if transform_node is None:
			return

		scale_amount = getattr(self.operator, 'scale', None)
		if scale_amount is None:
			return

		scale_input = transform_node.inputs[3]
		scale_amount = self.start_scale * (self.geometry_origin_2d - self.mouse_position).length / self.scale_multiplier

		# We set the operator property before we retrieve it again in case it has any defined min/max limits.
		setattr(self.operator, 'scale', scale_amount)
		scale_input.default_value = getattr(self.operator, 'scale')


	def scale(self, event):
		transform_node = self.nodes.get('Transform')
		if transform_node is None:
			return
			
		self.scaling = not self.scaling
		self.start_position = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))

		# This value allows imitating Blender's scale behavior (scale faster the closer you are to the object origin).
		self.scale_multiplier = (self.geometry_origin_2d - self.start_position).length

		scale_input = transform_node.inputs[3]
		self.start_scale = scale_input.default_value.copy()
	
	def rotate(self, event):
		return
	

#####################
# USER INTERFACES
#####################

class UserInterface(EventManager):
	
	context = NotImplemented

	def event(self, event):
		self.context.area.tag_redraw()

		return super().event(event)


class HeadsUpDisplay(UserInterface):
	'''
	Heads Up Display for the active property being tweaked and it's value.
	'''

	def __init__(self, context, geometry_origin: mathutils.Vector, nodes: list[bpy.types.GeometryNode], input_data, event) -> None:
		self.context = context
		self.geometry_origin = geometry_origin
		self.nodes = nodes
		self.input_data = fill_missing_data(input_data, self.nodes)

		self.property_name = ''
		self.property_value = ''

		self.context.window.cursor_modal_set('CROSSHAIR')

		# Event parameter is only used here.
		self.mouse_position = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
		self.geometry_origin_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(self.context.region, self.context.space_data.region_3d, self.geometry_origin)
	
		self._props_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_props, (), 'WINDOW', 'POST_PIXEL')
		self._scale_handle = None

	def draw_callback_props(self):
		offset_x = 30
		self.draw_text(f'{self.property_name}: {str(self.property_value)}', offset_x=offset_x)
		if self._scale_handle is not None:
			self.draw_text('[Scaling]', offset_x=offset_x, offset_y=-20)

	def draw_callback_scale_line(self):
		start = self.geometry_origin_2d 
		end = self.mouse_position
		coords=[start, end]
		self.draw_line_2d(coords, color=(1, 1, 1, .5))

	def draw_text(self, text, color=(1, 1, 1, 1), font_size=11, offset_x=0, offset_y=0, rotation_radians=0):
		x = self.mouse_position.x + offset_x
		y = self.mouse_position.y + offset_y
		
		dpi   = self.context.preferences.system.dpi
		ui_scale = self.context.preferences.system.ui_scale

		font_id = 1
		# blf.size(font_id, font_size*ui_scale, dpi)		# WILL NOT WORK ANYMORE.
		blf.size(font_id, font_size * ui_scale * dpi / 72)	# The Blender 4.0 way.
		blf.color(font_id, *color)
		blf.position(font_id, x, y, 0)

		if rotation_radians != 0:
			blf.enable(font_id, blf.ROTATION)
			blf.rotation(font_id, rotation_radians + math.radians(90))
		
		blf.enable(font_id, blf.SHADOW)

		# Text with shadow 1
		blf.shadow(font_id, 5, 0, 0, 0, 1)
		blf.shadow_offset(font_id, 1, -1)
		blf.draw(font_id, text)
		
		# Same text with shadow 2
		blf.shadow(font_id, 0, 0, 0, 0, 1)
		blf.shadow_offset(font_id, 1, -1)
		blf.draw(font_id, text)

		blf.disable(font_id, blf.SHADOW)

		if rotation_radians != 0:
			blf.disable(font_id, blf.ROTATION)
	
	def draw_line_2d(self, coords, color=(1, 1, 1, 1)):
		shader = gpu.shader.from_builtin('UNIFORM_COLOR')
		gpu.state.blend_set('ALPHA')
		# gpu.state.line_width_set(2.0)
		batch = gpu_extras.batch.batch_for_shader(shader, 'LINE_STRIP', {'pos': coords})
		shader.uniform_float("color", color)
		batch.draw(shader)

		# RESTORE OPENGL DEFAULTS.
		# gpu.state.line_width_set(1.0)
		gpu.state.blend_set('NONE')
	
	def any(self, event):
		self.update_hud(event)
	
	def mousemove(self, event):
		'''
		Update the required 2d coordinate for the HUD.
		'''

		self.mouse_position = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
		self.geometry_origin_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(
				self.context.region, self.context.space_data.region_3d, self.geometry_origin)

	def increase(self, event):
		self.update_hud(event)

	def decrease(self, event):
		self.update_hud(event)

	def number(self, event, number: int):
		self.update_hud(event)
	
	def update_hud(self, event):
		iNode = self.input_data.get(event.alt)
		if iNode is None:
			return

		self.property_value = iNode.inputs[0].default_value - iNode.offset
		self.property_name = iNode.prop_name.title()
	

	def scale(self, event):
		if self._scale_handle is None:
			self._scale_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_scale_line, (), 'WINDOW', 'POST_PIXEL')
		else:
			bpy.types.SpaceView3D.draw_handler_remove(self._scale_handle, 'WINDOW')
			self._scale_handle = None


	# OPERATOR CONTROL

	def cancel(self, event):
		self._cleanup()

	def finish(self, event):
		self._cleanup()
	
	def _cleanup(self):
		bpy.types.SpaceView3D.draw_handler_remove(self._props_handle, 'WINDOW')

		if self._scale_handle is not None:
			bpy.types.SpaceView3D.draw_handler_remove(self._scale_handle, 'WINDOW')

		self.context.window.cursor_modal_restore()
	

#####################
# COMPOSITOR
#####################

class ModalGeometry:
	'''
	Creates a geometry object in the scene that can be adjusted with a modal (ex. scroll to add sides to cylinder)
	and a UI to visuallize the editable properties.
	'''

	def __init__(self, geometry_generator: GeometryGenerator, geometry_editor: GeometryEditor, user_interface: UserInterface) -> None:
		self.geometry_generator = geometry_generator
		self.geometry_editor    = geometry_editor
		self.user_interface     = user_interface
	
	def event(self, event) -> set[str]:
		self.geometry_editor.event(event)
		self.user_interface.event(event)

		return self.geometry_generator.event(event)


#####################
# BLENDER OPERATORS
#####################


class OperatorBase:

	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode in {'OBJECT'}
	
	def invoke(self, context, event):
		raise NotImplementedError
	
	def post_function(self, context):
		'''
		Optional commands to run after the Operator finishes (this is executed by 
		a finisher event sent to the GeometryGenerator in the Compositor Class).
		
		EXAMPLE: enter Edit Mode and select something.
		'''

		pass


class NonModalOperator(OperatorBase):


	def invoke(self, context, event):
		geometry_generator = NodeGeometry(self, context, self.DATA.NODE_DATA, self.DATA.LINK_DATA)
		geometry_editor    = NodeEditor(self, context, geometry_generator.location, geometry_generator.nodes, self.DATA.INPUT_DATA)	# The editor initializes stuff, even if we don't use it again after this.
		user_interface     = HeadsUpDisplay(context, geometry_generator.location, geometry_generator.nodes, self.DATA.INPUT_DATA, event)

		geometry_generator.finish(event)
		user_interface.finish(event)

		return {'FINISHED'}


class ModalOperator(OperatorBase):

	def invoke(self, context, event):
		geometry_generator = NodeGeometry(self, context, self.DATA.NODE_DATA, self.DATA.LINK_DATA)
		geometry_editor    = NodeEditor(self, context, geometry_generator.location, geometry_generator.nodes, self.DATA.INPUT_DATA)
		user_interface     = HeadsUpDisplay(context, geometry_generator.location, geometry_generator.nodes, self.DATA.INPUT_DATA, event)

		self.modal_geometry = ModalGeometry(
			geometry_generator, geometry_editor, user_interface)

		context.window_manager.modal_handler_add(self)

		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		return self.modal_geometry.event(event)


class MESH_OT_armored_circle(bpy.types.Operator, ModalOperator):
	'''Modal Circle primitive.

	armoredColony.com '''

	bl_idname = 'mesh.armored_circle'
	bl_label  = 'ARMORED Circle'
	DATA = CIRCLE_DATA

	sides: bpy.props.IntProperty(default=32, min=3, max=1024)
	scale: bpy.props.FloatVectorProperty(default=(1, 1, 1))


class MESH_OT_armored_plane(bpy.types.Operator, ModalOperator):
	'''Modal Plane primitive.

	armoredColony.com '''

	bl_idname = 'mesh.armored_plane'
	bl_label  = 'ARMORED Plane'
	DATA = PLANE_DATA

	cuts: bpy.props.IntProperty(default=2, min=2, max=102)
	scale: bpy.props.FloatVectorProperty(default=(1, 1, 1))


class MESH_OT_armored_cube(bpy.types.Operator, ModalOperator):
	'''Modal Cube primitive.

	armoredColony.com '''

	bl_idname = 'mesh.armored_cube'
	bl_label  = 'ARMORED Cube'
	DATA = CUBE_DATA
	
	cuts: bpy.props.IntProperty(default=2, min=2, max=102)
	scale: bpy.props.FloatVectorProperty(default=(1, 1, 1))
	

class MESH_OT_armored_cylinder(bpy.types.Operator, ModalOperator):
	'''Modal Cylinder primitive.

	armoredColony.com '''

	bl_idname = 'mesh.armored_cylinder'
	bl_label  = 'ARMORED Cylinder'
	DATA = CYLINDER_DATA

	sides: bpy.props.IntProperty(default=8, min=3, max=128)
	cuts:  bpy.props.IntProperty(default=1, min=1, max=129)
	scale: bpy.props.FloatVectorProperty(default=(1, 1, 1))


class MESH_OT_armored_quadsphere(bpy.types.Operator, ModalOperator):
	'''Modal Quadsphere primitive.

	armoredColony.com '''

	bl_idname = 'mesh.armored_quadsphere'
	bl_label  = 'ARMORED Quadsphere'
	DATA = QUADSPHERE_DATA

	subdivisions: bpy.props.IntProperty(default=1, min=1, max=8)
	scale: bpy.props.FloatVectorProperty(default=(1, 1, 1))



class MESH_OT_armored_vertex(bpy.types.Operator, NonModalOperator):
	'''Add a single vertex and enter edit mode.

	armoredColony.com '''

	bl_idname = 'mesh.armored_vertex'
	bl_label  = 'ARMORED Vertex'
	DATA = VERTEX_DATA

	points: bpy.props.IntProperty(default=1, min=1, max=1)

	def post_function(self, context):
		context.view_layer.objects.active = context.active_object
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_mode(type='VERT')
		bpy.ops.mesh.select_all(action='SELECT')


def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    
    layout.operator(MESH_OT_armored_plane.bl_idname,	  text='Plane (modal)',      icon='MESH_PLANE')
    layout.operator(MESH_OT_armored_cube.bl_idname,	  text='Cube (modal)',       icon='MESH_CUBE')
    layout.operator(MESH_OT_armored_circle.bl_idname,	  text='Circle (modal)',     icon='MESH_CIRCLE')
    layout.operator(MESH_OT_armored_cylinder.bl_idname,   text='Cylinder (modal)',   icon='MESH_CYLINDER')
    layout.operator(MESH_OT_armored_quadsphere.bl_idname, text='Quadsphere (modal)', icon='MESH_UVSPHERE')
    layout.operator(MESH_OT_armored_vertex.bl_idname,     text='Single Vert',        icon='DOT')


classes = (
	MESH_OT_armored_plane,
	MESH_OT_armored_cube,
	MESH_OT_armored_circle,
	MESH_OT_armored_cylinder,
	MESH_OT_armored_quadsphere,
	MESH_OT_armored_vertex,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.VIEW3D_MT_mesh_add.append(draw_menu)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	bpy.types.VIEW3D_MT_mesh_add.remove(draw_menu)