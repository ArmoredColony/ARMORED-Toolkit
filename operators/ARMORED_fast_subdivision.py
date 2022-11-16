# v2.0

import bpy


class FastSubdivision:
	'''
	Abstract Fast Subdivision class.
	'''

	bl_options = {'REGISTER'}
	bl_description = 'Add a Subsurf Modifier with limit_surface quality set to 1 (faster but less accurate) \n\narmoredColony.com '
	poll_mode = NotImplemented

	level: bpy.props.IntProperty(
		name='Level', default=1, min=0, soft_min=0, max=100, soft_max=6)

	use_limit_surface: bpy.props.BoolProperty(
		name='Use Limit Surface', default=True, 
		description='Disabled is faster for low SubD levels (1 or 2), but enabled is faster for higher levels (using my typical mesh resolution as an example)',
		options={'SKIP_SAVE'},
		)
	
	@classmethod
	def poll(cls, context):
		return context.mode == cls.poll_mode

	def execute(self, context):
		if self._nothing_selected(context):
			return {'CANCELLED'}

		valid_objects = [obj for obj in context.selected_objects if obj.type in {'MESH'}]

		for self.obj in valid_objects:
			self._add_subsurf_modifier()
			
		return {'FINISHED'}


	def _add_subsurf_modifier(self) -> None:
		mod = next((mod for mod in reversed(self.obj.modifiers) if mod.type == 'SUBSURF'), None)

		if mod is None:
			mod = self.obj.modifiers.new(name='Subdivision', type='SUBSURF')

		mod.use_limit_surface = self.use_limit_surface
		mod.quality = 1
		mod.levels = self.level
	
	def _nothing_selected(self, context):
		return not context.selected_objects
		

class OBJECT_OT_armored_fast_subdivision(bpy.types.Operator, FastSubdivision):

	bl_idname = 'object.armored_fast_subdivision'
	bl_label = 'ARMORED Fast Subdivision'
	poll_mode = 'OBJECT'


class MESH_OT_armored_fast_subdivision(bpy.types.Operator, FastSubdivision):

	bl_idname = 'mesh.armored_fast_subdivision'
	bl_label = 'ARMORED Fast Subdivision'
	poll_mode = 'EDIT_MESH'
	



classes = (
	OBJECT_OT_armored_fast_subdivision,
	MESH_OT_armored_fast_subdivision,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)