version = (1, 0, 0)

import bpy


class ARMORED_OT_paint_select(bpy.types.Operator):
	'''Paint Select like Modo (bind it to a single key, like "Q") (Experimental)

	armoredColony.com '''

	bl_idname = 'view3d.armored_paint_select'
	bl_label = 'ARMORED Paint Select'
	bl_options = {'REGISTER', 'UNDO'}

	def invoke(self, context, event):
		self.painted = False
		self.selecting = False
		self.deselecting = False
		self.first_key_pressed = event.type

		context.window_manager.modal_handler_add(self)
		
		return {'RUNNING_MODAL'}

	def modal(self, context, event):

		if event.type == 'LEFTMOUSE':

			if event.value == 'PRESS':
				self.selecting = True
				self.painted = True
			else:
				self.selecting = False


		elif event.type == 'RIGHTMOUSE':
				self.deselecting = True if event.value == 'PRESS' else False


		elif event.type == self.first_key_pressed and event.value == 'RELEASE':  

			if not self.painted:
				bpy.ops.wm.tool_set_by_id(name='builtin.select_box', cycle=False)

			return {'FINISHED'}

		elif event.type in {'ESC'}:
			return {'CANCELLED'}
	
		if self.selecting:
			bpy.ops.view3d.select('INVOKE_DEFAULT', extend=True, deselect=False)

		if self.deselecting:
			bpy.ops.view3d.select('INVOKE_DEFAULT', extend=False, deselect=True)

		return {'RUNNING_MODAL'}


classes = (
	ARMORED_OT_paint_select,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)    


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
