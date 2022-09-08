# v1.2

import bpy


class OBJECT_OT_armored_subdivision_set(bpy.types.Operator):
	'''Same as the default operator for setting your subdivision level (CTRL+1, etc) but without any Undo History.

armoredColony.com '''

	bl_idname = 'object.armored_subdivision_set'
	bl_label = 'ARMORED Set Subdivision'
	bl_options = {'REGISTER'}

	level: bpy.props.IntProperty(
		name='Level', default=1, min=0, soft_min=0, max=100, soft_max=6)

	fast_subdivision: bpy.props.BoolProperty(
		name='Fast Subdivision', default=True, 
		description='Adds a SUBSURF modifier of the specified subdivision level but with \'use_limit_surface\' option disabled (faster but less accurate)',
		options={'SKIP_SAVE'},
		)

	# @classmethod
	# def poll(cls, context):
	# 	return context.selected_objects
	
	def invoke(self, context, event):
		for self.obj in context.selected_objects:
			self._add_subsurf_modifier()
			
		return {'FINISHED'}


	def _add_subsurf_modifier(self) -> None:
		mod = next((mod for mod in reversed(self.obj.modifiers) if mod.type == 'SUBSURF'), None)

		if mod is None:
			mod = self.obj.modifiers.new(name='Subdivision', type='SUBSURF')

		mod.use_limit_surface = not self.fast_subdivision
		mod.levels = self.level


classes = (
	OBJECT_OT_armored_subdivision_set,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)