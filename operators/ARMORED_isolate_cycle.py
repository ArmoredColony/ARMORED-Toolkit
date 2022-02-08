# v1.1

import bpy
from bpy.types import Collection


class OUTLINER_OT_armored_isolate_cycle(bpy.types.Operator):
	'''Based on your outliner selections, isolate 1 object and cycle to the next/previous one using the SCROll wheel. Cancel with RMB. Also works with entire collections.

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
	# Whatever
	def invoke(self, context, event):
		self.objects = context.selected_ids
		self.original_state = {}
		for ob in self.objects:
			if ob.type == 'COLLECTION':
				self.original_state[ob] = not context.view_layer.layer_collection.children[ob.name].hide_viewport
			else:
				self.original_state[ob] = ob.visible_get()
			
		if self.not_enough_objects():
			self.report({'ERROR'}, f'ARM-TK: Select at least 2 objects cl: {len(self.objects)} < 2')
			return {'FINISHED'}
		
		self.report({'INFO'}, 'SCROLL to cycle and isolate each object')
		context.window.cursor_set('SCROLL_Y')

		self.iter_objects = Cycle(self.objects)
		self.hide_all_objects(context)

		self.current_ob = next(self.iter_objects)
		self.set_visibility(context, self.current_ob, True)

		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type in self.next_events and event.value == 'PRESS':
			self.isolate_next_object(context)

		elif event.type in self.previous_events and event.value == 'PRESS':
			self.isolate_previous_object(context)

		elif event.type in self.pass_through_events and event.value == 'PRESS':
			return {'PASS_THROUGH'}

		elif event.type in self.finished_events and event.value == 'PRESS':
			self.report({'INFO'}, 'FINISHED')
			context.window.cursor_set('DEFAULT')
			return {'FINISHED'}
		
		# CANCEL OPERATOR
		elif event.type in self.canceled_events and event.value == 'PRESS':
			self.report({'INFO'}, 'CANCELLED')
			self.set_original_object_visibility(context)
			context.window.cursor_set('DEFAULT')
			return {'FINISHED'}

		return {'RUNNING_MODAL'}

	def not_enough_objects(self):
		return len(self.objects) < 2

	def hide_all_objects(self, context):
		for ob in self.objects:
			self.set_visibility(context, ob, False)
	
	def set_original_object_visibility(self, context):
		for ob, visible in self.original_state.items():
			self.set_visibility(context, ob, visible)
	
	def isolate_next_object(self, context):
		self.set_visibility(context, self.current_ob, False)
		self.current_ob = next(self.iter_objects)
		self.set_visibility(context, self.current_ob, True)

	def isolate_previous_object(self, context):
		self.set_visibility(context, self.current_ob, False)
		self.current_ob = self.iter_objects.previous()
		self.set_visibility(context, self.current_ob, True)
	
	def set_visibility(self, context, ob, visible):
		if ob.type == 'COLLECTION':
			context.view_layer.layer_collection.children[ob.name].hide_viewport = not visible
		else:
			ob.hide_set(not visible)


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

	if bpy.app.version < (3, 1, 0):
		print('ARM-TK: created "COLLECTION" type')
		bpy.types.Collection.type = bpy.props.StringProperty(name='Type', get=get_collection_type)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	for menu in menus:
		exec(f'bpy.types.{menu}.remove(menu_draw)')

	if bpy.app.version < (3, 1, 0):
		print('ARM-TK: removed "COLLECTION" type')
		del bpy.types.Collection.type