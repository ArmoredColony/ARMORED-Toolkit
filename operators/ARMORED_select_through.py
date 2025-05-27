version = (2, 2, 0)

import bpy


class MESH_OT_armored_select_through(bpy.types.Operator):
	'''Automatically switch to xray mode activating a selection tool.

	armoredColony.com '''

	bl_idname = 'mesh.armored_select_through'
	bl_label = 'ARMORED Select Through'
	bl_options = {'REGISTER', 'UNDO'}

	select_mode: bpy.props.EnumProperty( 
		name='Mode', 
		description='Selection Mode', 
		default='SET', 
		items=[ ('SET', 'Set',      'Create a new selecton'),
			('ADD', 'Add',      'Add to the current selection'),
			('SUB', 'Subtract', 'Subtract from the curent selection'), ]
		)


	def invoke(self, context, event):
		context.space_data.shading.show_xray = True
		context.window_manager.modal_handler_add(self)
		bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.select_mode)

		return {'RUNNING_MODAL'}
	
	def modal(self, context, event):
		context.space_data.shading.show_xray = False
		return {'FINISHED'}

classes = (
	MESH_OT_armored_select_through,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)