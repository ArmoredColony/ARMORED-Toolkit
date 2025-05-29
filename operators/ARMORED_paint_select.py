version = (2, 0, 0)

import bpy


class EVENTS:
	FINISH = {'ESC', 'SPACE'}


class ARMORED_OT_paint_select(bpy.types.Operator):
	'''Tap to activate Rectangle Select, hold and mousemove for Circle Select (bind to a single key like 'Q').

	armoredColony.com '''

	bl_idname = 'view3d.armored_paint_select'
	bl_label = 'ARMORED Paint Select'
	bl_options = {'REGISTER', 'UNDO'}

	def invoke(self, context, event):
		self.first_key_pressed = event.type

		context.window_manager.modal_handler_add(self)
		# bpy.ops.wm.tool_set_by_id(name='builtin.select_circle', cycle=False)
		
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		# context.area.tag_redraw()	# I think bpy.ops calls already do this.

		if event.type == self.first_key_pressed and event.value == 'RELEASE': 
			bpy.ops.wm.tool_set_by_id(name='builtin.select_box', cycle=False)

			return {'FINISHED'}
		
		if event.type == 'MOUSEMOVE':
			bpy.ops.wm.tool_set_by_id(name='builtin.select_circle', cycle=False)

			return {'RUNNING_MODAL'}
		
		if event.type in EVENTS.FINISH:
			return {'FINISHED'}
		
		return {'PASS_THROUGH'}


classes = (
	ARMORED_OT_paint_select,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)    


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
