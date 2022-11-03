# v1.1

import bpy


pass_through_events = {'MIDDLEMOUSE', 'V', 'NUMPAD_PERIOD', 'F'}
next_events = {'DOWN_ARROW', 'RIGHT_ARROW', 'WHEELDOWNMOUSE'}
previous_events = {'UP_ARROW', 'LEFT_ARROW', 'WHEELUPMOUSE'}
finish_events = {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER', 'SPACE'}
cancel_events = {'RIGHTMOUSE', 'ESC'}
	

class OUTLINER_OT_armored_compare(bpy.types.Operator):
	'''Based on your outliner selections, isolate 1 item at a time. Useful for comparing changes between similar objects. NOTE: also works with collections.

armoredColony.com'''
	
	bl_idname = 'outliner.armored_compare'
	bl_label = 'ARMORED Compare'
	bl_options = {'REGISTER','UNDO'}

	@classmethod
	def poll(cls, context):
		if not hasattr(context, 'selected_ids'):
			return False
		return len(context.selected_ids) >= 2

	def execute(self, context):
		return self.invoke(context, event=None) 
	
	def invoke(self, context, event):
		self.scene_collections = self.get_view_layer_collections(context)
		self.selected_elements = context.selected_ids[:]
		self.store_original_visibility(context)
		
		self.report({'INFO'}, 'SCROLL to isolate one item at a time')
		context.window.cursor_set('SCROLL_Y')

		self.iter_elements = Cycle(self.selected_elements)
		self.hide_all_elements(context)

		self.current_element = next(self.iter_elements)
		self.set_visibility(context, self.current_element, True)

		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		if event.type in next_events and event.value == 'PRESS':
			self.isolate_next_element(context)

		elif event.type in previous_events and event.value == 'PRESS':
			self.isolate_previous_element(context)

		elif event.type in pass_through_events and event.value == 'PRESS':
			return {'PASS_THROUGH'}

		elif event.type in finish_events and event.value == 'PRESS':
			self.report({'INFO'}, 'FINISHED')
			context.window.cursor_set('DEFAULT')
			return {'FINISHED'}
		
		# CANCEL OPERATOR
		elif event.type in cancel_events and event.value == 'PRESS':
			self.report({'INFO'}, 'CANCELLED')
			self.restore_original_visibility(context)
			context.window.cursor_set('DEFAULT')
			return {'FINISHED'}

		return {'RUNNING_MODAL'}
	

	def get_view_layer_collections(self, context):
		'''Stupid as it may seem, this is the fastest technique for our needs.'''

		return {c.name : c for c in self.traverse_tree(context.view_layer.layer_collection) if c.name != 'Scene Collection'}
	
	def hide_all_elements(self, context):
		'''Hide all selected'''
		for item in self.selected_elements:
			self.set_visibility(context, item, False)

	def store_original_visibility(self, context):
		self.original_visibility = {}
		for item in self.selected_elements:
			if item.bl_rna.identifier == 'Collection':
			# if item.type == 'COLLECTION':
				self.original_visibility[item] = not self.scene_collections[item.name].hide_viewport
			else:
				self.original_visibility[item] = item.visible_get()
	
	def restore_original_visibility(self, context):
		for item, visible in self.original_visibility.items():
			self.set_visibility(context, item, visible)
	
	def isolate_next_element(self, context):
		self.set_visibility(context, self.current_element, False)
		self.current_element = next(self.iter_elements)
		self.set_visibility(context, self.current_element, True)

	def isolate_previous_element(self, context):
		self.set_visibility(context, self.current_element, False)
		self.current_element = self.iter_elements.previous()
		self.set_visibility(context, self.current_element, True)
	

	def set_visibility(self, context, item, visible):
		if item.bl_rna.identifier == 'Collection':
		# if item.type == 'COLLECTION':
			self.scene_collections[item.name].hide_viewport = not visible
		else:
			item.hide_set(not visible)
	
	def traverse_tree(self, tree):
		yield tree
		for child in tree.children:
			yield from self.traverse_tree(child)


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
	self.layout.operator(OUTLINER_OT_armored_compare.bl_idname, text='Compare')
	self.layout.separator()


classes = (
	# VIEW3D_OT_armored_compare_scenes,
	OUTLINER_OT_armored_compare,
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

	# if not hasattr(bpy.types.Collection, 'type'):
	# 	print('ARMORED-Toolkit: <outliner.armored_compare> created <COLLECTION> type')
	# 	bpy.types.Collection.type = bpy.props.StringProperty(name='Type', get=get_collection_type)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	for menu in menus:
		exec(f'bpy.types.{menu}.remove(menu_draw)')