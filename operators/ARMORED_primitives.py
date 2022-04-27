import bpy
from bpy.props import IntProperty, FloatProperty
from bpy.types import Operator
from bl_ui.space_statusbar import STATUSBAR_HT_header
import blf


from typing import TypeVar
Node = TypeVar('Node')

pass_through_events = {'MIDDLEMOUSE', 'NUMPAD_PERIOD', 'F'}
increase_events = {'WHEELUPMOUSE', 'NUMPAD_PLUS', 'PAGE_UP', 'UP_ARROW'}
decrease_events = {'WHEELDOWNMOUSE', 'NUMPAD_MINUS', 'PAGE_DOWN', 'DOWN_ARROW'}
reset_events = {'R'}
scale_events = {'S'}
finish_events = {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER', 'SPACE', 'TAB'}
cancel_events = {'RIGHTMOUSE', 'ESC'}

number_events = {
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




def draw_callback_px(self, context):
	def draw_text(self, text, offset_x=0, offset_y=-35):
		x = self.mouse_x + offset_x
		y = self.mouse_y + offset_y
		
		dpi = context.preferences.system.dpi
		scale = context.preferences.system.ui_scale
		font_size = 11

		font_id = 1
		blf.size(font_id, font_size*scale, dpi)
		blf.color(font_id, 1, 1, 1, 1.0)
		blf.position(font_id, x, y, 0)
		
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

	draw_text(self, self.text)


class StatusBar:
	def update_status_bar(self):
		self.save_status_bar()
		self.set_status_bar()

	def save_status_bar(self):
		self.status_bar = STATUSBAR_HT_header.draw

	def restore_status_bar(self):
		STATUSBAR_HT_header.draw = self.status_bar

	def set_active_property(self, name: str):
		self.active_prop_name = name

	def set_status_bar(self):
		STATUSBAR_HT_header.draw = self.draw_status_bar(self.active_prop_name)
	

	def draw_status_bar(self, active_prop_name):
		def draw(self, context):
			def key(icon, label, separation=2):
				row.label(text='', icon=icon)
				row.label(text=label)
				row.separator(factor=separation)

			layout = self.layout
			row = layout.row(align=True)
			
			row.label(text='Cube (modal)')
			row.separator(factor=6)
			
			key('MOUSE_LMB', 'Finish', 2)
			key('MOUSE_MMB', active_prop_name, 2)
			key('MOUSE_RMB', 'Cancel', 6)

			key('EVENT_R', 'Reset', 2)
			key('EVENT_TAB', 'Edit Mode', 2)
		return draw


class ModalPrimitive(StatusBar):
	scale : FloatProperty(name='Scale', default=1)
	start_scale = 0
	scaling = False

	@classmethod
	def poll(cls, context):
		return context.mode in {'OBJECT'}
	
	def invoke(self, context, event):
		self.alt_is_pressed = False
		# self.set_active_property('Cuts')

		self._set_text()
		self.update_status_bar()
		self._set_mouse_positions(event)
		self._set_cursor_display(context)
		
		self._create_node_container(context)
		self._show_wireframe()

		self._create_geometry_nodes_modifier()
		self._set_node_tree()
		self._set_output_node()
		self._create_primitive_node()
		self._link_nodes()
		self._set_primitive_node_inputs()

		args = (self, context)
		self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}
	
	def _pressing_alt(self, context, event):
		if self.alt_is_pressed:
			return
		self.alt_is_pressed = True
		self.scaling = True
		self.start_scale = event.mouse_region_x
		print('pressed alt')

	def _not_pressing_alt(self, context, event):
		if not self.alt_is_pressed:
			return
		self.alt_is_pressed = False
		self.scaling = False
		print('released alt')

	def modal(self, context, event):
		# context.area.tag_redraw()

		if event.alt:
			self._pressing_alt(context, event)
		else:
			self._not_pressing_alt(context, event)
		

		if event.type == 'MOUSEMOVE':
			self._set_mouse_positions(event)
			if self.scaling:
				self._scale(event)
		
		elif event.type in pass_through_events:
			return {'PASS_THROUGH'}

		elif event.type in increase_events and event.value == 'PRESS':
			self._increase_method(event)
		
		elif event.type in decrease_events and event.value == 'PRESS':
			self._decrease_method(event)
		
		elif event.type in number_events and event.value == 'PRESS':
			self._number_method(event)
		
		elif event.type in reset_events and event.value == 'PRESS':
			self._reset_method()

		# elif event.type in scale_events and event.value == 'PRESS':
			# self._scale()
		
		elif event.type in cancel_events and event.value == 'PRESS':
			self._reset_method()
			self._cleanup(context, 'CANCELLED')
			return {'FINISHED'}

		elif event.type in finish_events and event.value == 'PRESS':
			self._cleanup(context, 'FINISHED')
			if event.type == 'TAB':
				self.enter_edit_mode(context)
			return {'FINISHED'}

		self._set_text()
		context.area.tag_redraw()
		return {'RUNNING_MODAL'}

	
	def _set_mouse_positions(self, event):
		self.mouse_x = event.mouse_region_x
		self.mouse_y = event.mouse_region_y

	def _set_cursor_display(self, context):
		context.window.cursor_set('SCROLL_Y')

	def _reset_cursor_display(self, context):
		context.window.cursor_set('DEFAULT')

	def _create_node_container(self, context):
		bpy.ops.mesh.primitive_cube_add(align='CURSOR')
		self.node_container = context.active_object
	
	def _create_geometry_nodes_modifier(self):
		self.mod_name = f'Cube_{hash("cube")}'
		self.mod = self.node_container.modifiers.new(name=self.mod_name, type='NODES')
	
	def _set_node_tree(self):
		self.node_tree = self.mod.node_group
	
	def _get_node(self, name: str) -> Node:
		return self.node_tree.nodes.get(name)

	def _set_output_node(self):
		self.output_node = self._get_node('Group Output')
	
	def _set_primitive_node_inputs(self):
		self.inputs = self.primitive_node.inputs
	
	def _link_nodes(self):
		self.node_tree.links.new(self.primitive_node.outputs[0], self.output_node.inputs[0])
	
	def _apply_modifier(self, context):
		if context.mode != 'EDIT':
			bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.modifier_apply(modifier=self.mod_name)
	
	def _delete_node_tree(self):
		bpy.data.node_groups.remove(self.node_tree)

	def enter_edit_mode(self, context):
		bpy.ops.object.mode_set(mode='EDIT')
		context.tool_settings.mesh_select_mode = (False, False, True)
	
	def _show_wireframe(self):
		self.node_container.show_wire = True

	def _hide_wireframe(self):
		self.node_container.show_wire = False
	
	def _cleanup(self, context, report: str):
		self._apply_modifier(context)
		self._hide_wireframe()
		self._delete_node_tree()
		self._reset_cursor_display(context)
		bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
		# restore_status_bar(self)
		self.restore_status_bar()
		self.report({'INFO'}, report)
	

	def _set_text(self):
		raise NotImplementedError

	def _create_primitive_node(self):
		raise NotImplementedError
	
	def _reset_method(self):
		raise NotImplementedError

	def _increase_method(self, event):
		raise NotImplementedError

	def _decrease_method(self, event):
		raise NotImplementedError
	
	def _number_method(self, event):
		raise NotImplementedError
	
	def _scale(self, event):
		raise NotImplementedError


class MESH_OT_armored_cube(Operator, ModalPrimitive):
	'''Modal Cube primitive.

armoredColony.com '''

	bl_idname = 'mesh.armored_cube'
	bl_label = 'ARMORED Cube'
	bl_options = {'REGISTER', 'UNDO'}

	cuts : IntProperty(name='Cuts', default=0, min=0, max=100)
	CUT_OFFSET = 2

	def _set_text(self):
		self.text = f'Cuts: {self.cuts}'
		self.set_active_property('Cuts')

	def _create_primitive_node(self):
		self.primitive_node = self.node_tree.nodes.new(type='GeometryNodeMeshCube')
		inputs = self.primitive_node.inputs
		inputs[0].default_value = (2, 2, 2)
		for input in inputs[1:4]:
			input.default_value = self.cuts + self.CUT_OFFSET
	
	def _set_values(self):
		for input in self.inputs[1:4]:
			input.default_value = self.cuts + self.CUT_OFFSET
	
	def _increase_method(self, event):
		self.cuts += 1
		self._set_values()

	def _decrease_method(self, event):
		self.cuts -= 1
		self._set_values()
	
	def _number_method(self, event):
		self.cuts = number_events[event.type]
		self._set_values()
	
	def _reset_method(self):
		self.cuts = 0
		self._set_values()
	
	def _scale(self, event):
		self.scale = (event.mouse_region_x - self.start_scale) / 100
		print(self.scale)
		self.inputs[0].default_value = ([self.scale]*3)

# class MESH_OT_armored_plane(MESH_OT_armored_cube, Operator):
# 	'''Modal Plane primitive.

# armoredColony.com '''

# 	bl_idname = 'mesh.armored_plane'
# 	bl_label = 'ARMORED Plane'
# 	bl_options = {'REGISTER', 'UNDO'}

# 	cuts : IntProperty(name='Cuts', default=0, min=0, max=100)
# 	CUT_OFFSET = 2

# 	# def _set_text(self):
# 	# 	self.text = f'Cuts: {self.cuts}'

# 	def _create_primitive_node(self):
# 		self.primitive_node = self.node_tree.nodes.new(type='GeometryNodeMeshGrid')
# 		inputs = self.primitive_node.inputs

# 		for input in inputs[:2]:
# 			input.default_value = 3
# 		for input in inputs[2:4]:
# 			input.default_value = self.cuts + self.CUT_OFFSET
	
# 	def _set_values(self):
# 		for input in self.inputs[2:5]:
# 			input.default_value = self.cuts + self.CUT_OFFSET
	
	# def _increase_method(self, event):
	# 	self.cuts += 1
	# 	self._set_values()

	# def _decrease_method(self, event):
	# 	self.cuts -= 1
	# 	self._set_values()
	
	# def _number_method(self, event):
	# 	self.cuts = number_events[event.type]
	# 	self._set_values()
	
	# def _reset_method(self):
	# 	self.cuts = 0
	# 	self._set_values()	


class MESH_OT_armored_cylinder(Operator, ModalPrimitive):
	'''Modal Cylinder primitive.

armoredColony.com '''

	bl_idname = 'mesh.armored_cylinder'
	bl_label = 'ARMORED Cylinder'
	bl_options = {'REGISTER', 'UNDO'}
	
	sides         : IntProperty(name='Sides',         default=8, min=3, max=128)
	vertical_cuts : IntProperty(name='Vertical Cuts', default=0, min=0, max=100)

	VERTICAL_CUTS_OFFSET = 1

	def _set_text(self):
		self.text = f'Sides {self.sides}'
		self.set_active_property('Sides')

	def _set_alt_text(self):
		self.text = f'Vertical Cuts {self.vertical_cuts}'

	def _create_primitive_node(self):
		self.primitive_node = self.node_tree.nodes.new(type='GeometryNodeMeshCylinder')
		self.primitive_node.inputs[0].default_value = self.sides
		self.primitive_node.inputs[1].default_value = self.vertical_cuts + 1
	
	def _set_values(self):
		self.inputs[1].default_value = self.vertical_cuts + self.VERTICAL_CUTS_OFFSET
		self.inputs[0].default_value = self.sides

	def _increase_method(self, event):
		if event.shift:
			self.vertical_cuts += 1
		else:
			self.sides += 1
		self._set_values()

	def _decrease_method(self, event):
		if event.shift:
			self.vertical_cuts -= 1
		else:
			self.sides -= 1
		self._set_values()
	
	def _number_method(self, event):
		self.sides = number_events[event.type]
		self._set_values()
	
	def _reset_method(self):
		self.sides = 8
		self.vertical_cuts = 0
		self._set_values()


class MESH_OT_armored_quadsphere(Operator, ModalPrimitive):
	'''Modal Quadsphere primitive.

armoredColony.com '''

	bl_idname = 'mesh.armored_quadspheree'
	bl_label = 'ARMORED Quadsphere'
	bl_options = {'REGISTER', 'UNDO'}

	subdivisions : IntProperty(name='Subdivisions', default=1, min=1, max=7)

	def _set_text(self):
		self.text = f'Subdivisions: {self.subdivisions}'
		self.set_active_property('Subdivisions')

	def _create_primitive_node(self):
		self.primitive_node = self.node_tree.nodes.new(type='GeometryNodeSubdivisionSurface')
		inputs = self.primitive_node.inputs
		inputs[1].default_value = self.subdivisions

	def _link_nodes(self):
		super()._link_nodes()
		self.node_tree.links.new(self._get_node('Group Input').outputs[0], self.primitive_node.inputs[0])
	
	def _set_values(self):
		self.inputs[1].default_value = self.subdivisions
	
	def _increase_method(self, event):
		self.subdivisions += 1
		self._set_values()

	def _decrease_method(self, event):
		self.subdivisions -= 1
		self._set_values()
	
	def _number_method(self, event):
		self.subdivisions = number_events[event.type]
		self._set_values()
	
	def _reset_method(self):
		self.subdivisions = 0
		self._set_values()
	
	def _cleanup(self, context, report):
		super()._cleanup(context, report)

		# Select components and cast to sphere.
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.transform.tosphere(value=1)
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='OBJECT')


class MESH_OT_armored_vertex(Operator):
	'''Add a single vertex and enter edit mode.

armoredColony.com '''

	bl_idname = 'mesh.armored_vertex'
	bl_label = 'ARMORED Vertex'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode in {'OBJECT', 'EDIT_MESH'}

	def execute(self, context):
		mesh = bpy.data.meshes.new('Vert')
		mesh.vertices.add(1)

		from bpy_extras import object_utils
		object_utils.object_data_add(context, mesh)
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.context.tool_settings.mesh_select_mode = (True, False, False)

		return {'FINISHED'}
	

def draw_menu(self, context):
    layout = self.layout
    layout.separator()
#     layout.operator(MESH_OT_armored_plane.bl_idname,	  text='Plane (modal)',      icon='MESH_PLANE')
    layout.operator(MESH_OT_armored_cube.bl_idname,	  text='Cube (modal)',       icon='MESH_CUBE')
    layout.operator(MESH_OT_armored_cylinder.bl_idname,   text='Cylinder (modal)',   icon='MESH_CYLINDER')
    layout.operator(MESH_OT_armored_quadsphere.bl_idname, text='Quadsphere (modal)', icon='MESH_UVSPHERE')
    layout.operator(MESH_OT_armored_vertex.bl_idname,     text='Single Vert',        icon='DOT')


classes = (
	MESH_OT_armored_cube,
	# MESH_OT_armored_plane,
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