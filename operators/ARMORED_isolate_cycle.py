# v1.0

import bpy


class OUTLINER_OT_armored_isolate_cycle(bpy.types.Operator):
	'''Based on your outliner selections, isolate 1 element/collection and cycle to the next/previous one using the SCROll wheel. Cancel with RMB. Also works with entire collections.

	armoredColony.com'''
	
	bl_idname = 'outliner.armored_isolate_cycle'
	bl_label = 'ARMORED Cycle'
	bl_options = {'REGISTER','UNDO'}

	pass_through_events = {'MIDDLEMOUSE', 'V'}
	next_events = {'DOWN_ARROW', 'RIGHT_ARROW', 'WHEELDOWNMOUSE'}
	previous_events = {'UP_ARROW', 'LEFT_ARROW', 'WHEELUPMOUSE'}
	finished_events = {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER', 'SPACE'}
	canceled_events = {'RIGHTMOUSE', 'ESC'}

	@classmethod
	def poll(cls, context):
		if not hasattr(context, 'selected_ids'):
			return False
		return len(context.selected_ids) >= 2

	def execute(self, context):
		return self.invoke(context, event=None) 
	
	def invoke(self, context, event):
		self.selected_elements = context.selected_ids
		self.save_original_visibility(context)
		
		self.report({'INFO'}, 'SCROLL to cycle and isolate each element/collection')
		context.window.cursor_set('SCROLL_Y')

		self.iter_elements = Cycle(self.selected_elements)
		self.hide_all_elements(context)

		self.current_element = next(self.iter_elements)
		self.set_visibility(context, self.current_element, True)

		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type in self.next_events and event.value == 'PRESS':
			self.isolate_next_element(context)

		elif event.type in self.previous_events and event.value == 'PRESS':
			self.isolate_previous_element(context)

		elif event.type in self.pass_through_events and event.value == 'PRESS':
			return {'PASS_THROUGH'}

		elif event.type in self.finished_events and event.value == 'PRESS':
			self.report({'INFO'}, 'FINISHED')
			context.window.cursor_set('DEFAULT')
			return {'FINISHED'}
		
		# CANCEL OPERATOR
		elif event.type in self.canceled_events and event.value == 'PRESS':
			self.report({'INFO'}, 'CANCELLED')
			self.restore_original_visibility(context)
			context.window.cursor_set('DEFAULT')
			return {'FINISHED'}

		return {'RUNNING_MODAL'}

	
	def hide_all_elements(self, context):
		for element in self.selected_elements:
			self.set_visibility(context, element, False)

	def save_original_visibility(self, context):
		self.original_visibility = {}
		for element in self.selected_elements:
			if element.type == 'COLLECTION':
				self.original_visibility[element] = not context.view_layer.layer_collection.children[element.name].hide_viewport
			else:
				self.original_visibility[element] = element.visible_get()
	
	def restore_original_visibility(self, context):
		for element, visible in self.original_visibility.items():
			self.set_visibility(context, element, visible)
	
	def isolate_next_element(self, context):
		self.set_visibility(context, self.current_element, False)
		self.current_element = next(self.iter_elements)
		self.set_visibility(context, self.current_element, True)

	def isolate_previous_element(self, context):
		self.set_visibility(context, self.current_element, False)
		self.current_element = self.iter_elements.previous()
		self.set_visibility(context, self.current_element, True)
	

	def set_visibility(self, context, element, visible):
		if element.type == 'COLLECTION':
			# This command imitates the user clicking in the outliner.
			context.view_layer.layer_collection.children[element.name].hide_viewport = not visible

			# Do not use this for collections (users cannot alter this state through the outliner):
			# element.hide_viewport = not visible
		else:
			element.hide_set(not visible)


class Cycle():
	def __init__(self, c):
		self._c = c
		self._index = -1

	def __next__(self):
		self._index += 1
		if self._index >= len(self._c):
			self._index = 0
		return self._c[self._index]

	def previous(self):
		self._index -= 1
		if self._index < 0:
			self._index = len(self._c)-1
		return self._c[self._index]


def get_collection_type(self):
	return 'COLLECTION'


def menu_draw(self, context):
	self.layout.operator(OUTLINER_OT_armored_isolate_cycle.bl_idname, text='Isolate Cycle')
	self.layout.separator()


classes = (
	OUTLINER_OT_armored_isolate_cycle,
)

menus = (
	'OUTLINER_MT_object',
	'OUTLINER_MT_context_menu',
	'OUTLINER_MT_collection',
	'OUTLINER_MT_collection_new',
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	for menu in menus:
		exec(f'bpy.types.{menu}.prepend(menu_draw)')

	if not hasattr(bpy.types.Collection, 'type'):
		print('ARMORED-Toolkit: created "COLLECTION" type')
		bpy.types.Collection.type = bpy.props.StringProperty(name='Type', get=get_collection_type)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	for menu in menus:
		exec(f'bpy.types.{menu}.remove(menu_draw)')