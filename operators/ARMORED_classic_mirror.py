# v1.1

import bpy


class MESH_OT_armored_classic_mirror(bpy.types.Operator):
	'''Creates a mirror modifier with my usual settings. If one already exists, it duplicates and applies it.

armoredColony.com '''

	bl_idname = 'mesh.armored_classic_mirror'
	bl_label = 'ARMORED Classic Mirror'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		active = context.active_object
		return (
			active is not None and
			active.type == 'MESH' and
			context.mode in {'OBJECT', 'EDIT_MESH'} 
			)

	def execute(self, context):
		active = context.active_object

		last_mode = context.mode
		if last_mode == 'EDIT_MESH':
			bpy.ops.object.mode_set(mode='OBJECT')

		mod = active.modifiers.get('Mirror')

		if mod is None:
			mod = active.modifiers.new(type='MIRROR', name='Mirror')

			mod.use_axis             = True,  False, False
			mod.use_bisect_axis      = True,  True,  True
			mod.use_bisect_flip_axis = False, True,  False

			mod.use_clip = True

			mod.merge_threshold = .0001
			mod.bisect_threshold = .0001
		
		else:
			bpy.ops.object.modifier_copy(modifier='Mirror')
			bpy.ops.object.modifier_apply(modifier='Mirror.001')
		
		if last_mode == 'EDIT_MESH':
			bpy.ops.object.mode_set(mode='EDIT')

		return {'FINISHED'}


classes = (
	MESH_OT_armored_classic_mirror,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)