# v2.0

import bpy


class BaseClass:
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects) > 0

	def _get_subd_modifiers(self, context) -> list[bpy.types.Modifier]:
		selected_objects = (ob for ob in context.selected_objects if ob.type == 'MESH')

		subd_modifiers = []
		for ob in selected_objects:
			mod = next((mod for mod in reversed(ob.modifiers) if mod.type == 'SUBSURF' and mod.show_viewport), None)
			
			if mod is None:
				mod = ob.modifiers.new(name='Subdivision', type='SUBSURF')
				mod.levels = 0

			subd_modifiers.append(mod)

		return subd_modifiers


class VIEW3D_OT_increase_subd_mod_level(bpy.types.Operator, BaseClass):
	'''Increase the current Subdivision modifier level by one (ignores non-MESH types) (adds a subD modifier if none exists).

armoredColony.com '''

	bl_idname = 'view3d.armored_increase_subd_mod_level'
	bl_label = 'ARMORED Increase SubD modifier level'

	def execute(self, context):
		subd_modifiers = super()._get_subd_modifiers(context)
		for mod in subd_modifiers:
			mod.levels += 1

		return {'FINISHED'}


class VIEW3D_OT_decrease_subd_mod_level(bpy.types.Operator, BaseClass):
	'''Decrease the current Subdivision modifier level by one (ignores non-MESH types) (adds a subD modifier if none exists).

armoredColony.com '''
    
	bl_idname = 'view3d.armored_decrease_subd_mod_level'
	bl_label = 'ARMORED Decrease SubD modifier level'

	def execute(self, context):
		subd_modifiers = super()._get_subd_modifiers(context)
		for mod in subd_modifiers:
			mod.levels -= 1

		return {'FINISHED'}


classes = (
	VIEW3D_OT_increase_subd_mod_level,
	VIEW3D_OT_decrease_subd_mod_level,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

