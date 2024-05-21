version = (1, 5, 0)

import bpy


class MESH_OT_armored_classic_mirror(bpy.types.Operator):
	'''Creates a mirror modifier with my usual settings. If one already exists, it duplicates and applies it.

	armoredColony.com '''

	bl_idname = 'mesh.armored_classic_mirror'
	bl_label = 'ARMORED Classic Mirror'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.type == 'MESH'

	def execute(self, context):
		active_object = context.active_object

		last_mode = context.mode
		if last_mode == 'EDIT_MESH':
			bpy.ops.object.mode_set(mode='OBJECT')

		mod = active_object.modifiers.get('Mirror')

		if mod is None:
			self._add_mirror_modifier(context, active_object)

		elif active_object.data.users > 1:
			self.report({'WARNING'}, 'Cannot apply modifiers to multi-user data.')

			return {'CANCELLED'}

		else:
			bpy.ops.object.modifier_copy(modifier='Mirror')
			bpy.ops.object.modifier_apply(modifier='Mirror.001')

		if last_mode == 'EDIT_MESH':
			bpy.ops.object.mode_set(mode='EDIT')

		return {'FINISHED'}
	

	def _add_mirror_modifier(self, context, active_object) -> bpy.types.Modifier:
		found_subsurf = bool(active_object.modifiers and active_object.modifiers[-1].type == 'SUBSURF')

		mod = active_object.modifiers.new(type='MIRROR', name='Mirror')

		mod.use_axis             = True,  False, False
		mod.use_bisect_axis      = True,  True,  True
		mod.use_bisect_flip_axis = False, True,  False

		mod.use_clip = True

		if found_subsurf:
			self._move_modifier_up(context, object=active_object, modifier_name=mod.name)

		return mod
	
	def _move_modifier_up(self, context, object: bpy.types.Object, modifier_name: str):
		
		# Required for Blender 4.0 and later.
		with context.temp_override(object=object):
			bpy.ops.object.modifier_move_up(modifier=modifier_name)


classes = (
	MESH_OT_armored_classic_mirror,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)