version = (3, 1, 1)


import bpy
from bpy.props import StringProperty


class ARMORED_OT_toggle_tool(bpy.types.Operator):
	'''Toggles the specified tool.

	armoredColony.com '''
 
	bl_idname = 'view3d.armored_toggle_tool'
	bl_label = 'ARMORED Toggle Tool'
	bl_options = {'REGISTER'}
	
	name:          StringProperty(name='Tool to toggle', default='builtin.move')
	previous_tool: StringProperty(name='Previous Tool',  default='builtin.select_box')
	fallback_tool: StringProperty(name='Fallback Tool',  default='builtin.select_box')
	

	def execute(self, context):
		current_tool = context.workspace.tools.from_space_view3d_mode(context.mode, create=False).idname

		if current_tool != self.name:
			self.previous_tool = current_tool
			bpy.ops.wm.tool_set_by_id(name=self.name, cycle=False)

		else:
			bpy.ops.wm.tool_set_by_id(name=self.previous_tool, cycle=False)
		
		if self.fallback_tool:
			bpy.ops.wm.tool_set_by_id(name=self.fallback_tool, as_fallback=True)

		return {'FINISHED'}


classes = (
	ARMORED_OT_toggle_tool,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)