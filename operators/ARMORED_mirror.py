version = (1, 7, 0)

import bpy


def move_modifier_up(context, obj: bpy.types.Object, modifier_name: str) -> None:
	with context.temp_override(object=obj):
		bpy.ops.object.modifier_move_up(modifier=modifier_name)


class MESH_OT_armored_mirror(bpy.types.Operator):
	'''Creates a mirror modifier with my favorite settings. If one already exists, it will apply the modifier without deleting it.

	armoredColony.com '''

	bl_idname = 'mesh.armored_classic_mirror'
	bl_label = 'ARMORED Mirror'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return bool([obj for obj in context.selected_objects if obj.type == 'MESH'])

	def execute(self, context):
		selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

		for obj in selected_objects:

			# Gets the first mirror modifier it finds.
			mod = next((mod for mod in obj.modifiers if mod.type == 'MIRROR'), None)

			if mod is None:
				self._add_mirror_modifier(context, obj=obj)
				continue
			
			# Must do this inside the loop in case objects 
			# have different Mirror modifier settings.
			self._apply_mirror_to_data(context, obj=obj, mod=mod)

		return {'FINISHED'}
	

	# PRIVATE METHODS __________________________________________________

	def _add_mirror_modifier(self, context, obj) -> bpy.types.Modifier:
		context.view_layer.objects.active = obj

		last_modifier_is_subsurf = bool(obj.modifiers and obj.modifiers[-1].type == 'SUBSURF')

		mod = obj.modifiers.new(type='MIRROR', name='Mirror')

		mod.use_axis             = True,  False, False
		mod.use_bisect_axis      = True,  True,  True
		mod.use_bisect_flip_axis = False, True,  False

		mod.use_clip = True

		if last_modifier_is_subsurf:
			move_modifier_up(context, obj=obj, modifier_name=mod.name)

		return mod
	
	def _apply_mirror_to_data(self, context, obj: bpy.types.Object, mod: bpy.types.Modifier) -> None:
		'''
		Apply the Mirror modifier and re-link any previously linked users.
		'''

		last_mode = context.obj.mode

		if last_mode != 'OBJECT':
			bpy.ops.object.mode_set(mode='OBJECT')

		linked_users = []

		if obj.data.users > 1:
			original_mesh = obj.data
			original_mesh_name = original_mesh.name
			linked_users = [_obj for _obj in bpy.data.objects if _obj.type == 'MESH' and _obj.data == obj.data and _obj != obj]

		with context.temp_override(object=obj):
			try:
				bpy.ops.object.modifier_copy(modifier=mod.name)
				mod_name = obj.modifiers.active.name
				bpy.ops.object.modifier_apply(modifier=mod_name, report=True, single_user=True)

			except RuntimeError as e:
				self.report({'WARNING'}, f'Could not apply modifier {mod.name} - {e}')

				if last_mode != 'OBJECT':
					bpy.ops.object.mode_set(mode='EDIT')

				return

		if last_mode != 'OBJECT':
			bpy.ops.object.mode_set(mode=last_mode)
		
		if linked_users:
			new_mesh = obj.data

			for other_obj in linked_users:
				other_obj.data = new_mesh

			bpy.data.meshes.remove(original_mesh, do_unlink=True)
			new_mesh.name = original_mesh_name




classes = (
	MESH_OT_armored_mirror,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)