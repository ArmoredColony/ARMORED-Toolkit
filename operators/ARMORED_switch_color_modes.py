import bpy
from bpy.props import EnumProperty


class VIEW3D_OT_armored_switch_color_modes(bpy.types.Operator):
	'''Switch back and forth between two viewport color modes.

armoredColony.com '''

	bl_idname = 'view3d.armored_switch_color_modes'
	bl_label = 'ARMORED Switch Color Modes'
	bl_options = {'REGISTER'}

	items = [
		('MATERIAL', 'Material', 'Show material color'),
                ('OBJECT',   'Object',   'Show object color'), 
                ('VERTEX',   'Vertex',   'Show active vertex color'), 
                ('SINGLE',   'Single',   'Show scene in a single color'), 
                ('RANDOM',   'Random',   'Show random object color'), 
                ('TEXTURE',  'Texture',  'Show texture'), 
		]
        
	mode_1 : EnumProperty(name='Mode 1', default='MATERIAL', items=items)
	mode_2 : EnumProperty(name='Mode 2', default='SINGLE', items=items)

	@classmethod
	def poll(cls, context):
		return context.area.type == 'VIEW3D' and context.space_data.shading.type == 'SOLID'


	def invoke(self, context, event):
		shading = context.space_data.shading

		if shading.color_type == self.mode_1:
			shading.color_type = self.mode_2
		else:
			shading.color_type = self.mode_1

		self.report({'INFO'}, f'Color Mode: {shading.color_type}')
		return {'FINISHED'}


classes = (
	VIEW3D_OT_armored_switch_color_modes,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)