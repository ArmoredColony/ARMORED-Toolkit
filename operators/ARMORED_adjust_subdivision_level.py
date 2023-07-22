version = (2, 2, 1)

import bpy


class AdjustSubdivisionLevel:
	'''
	Abstract class to increse/decrease the Subsurf Modifier level by the specified integer.
	'''

	bl_options = {'REGISTER'}
	subd_add: int = NotImplemented	# How many levels you want to add/remove (ideally 1 or -1)

	# @classmethod
	# def poll(cls, context):
	# 	return context.selected_objects
	
	def execute(self, context):
		subd_modifiers = self._get_subd_modifiers(context.selected_objects)

		for mod in subd_modifiers:
			mod.levels += self.subd_add
		
		return {'FINISHED'}

	def _get_subd_modifiers(self, selected_objects: list[bpy.types.Object]) -> list[bpy.types.Modifier]:
		'''
		Creates a new Subsurf Modifier for each selected object that does NOT have one.
		'''

		selected_objects = (ob for ob in selected_objects if ob.type in {'MESH'})

		subd_modifiers = []
		for ob in selected_objects:
			mod = next((mod for mod in reversed(ob.modifiers) if mod.type == 'SUBSURF'), None)
			
			if mod is None:
				mod = ob.modifiers.new(name='Subdivision', type='SUBSURF')
				mod.levels = 0
			
			subd_modifiers.append(mod)

		return subd_modifiers


class VIEW3D_OT_increase_subd_mod_level(bpy.types.Operator, AdjustSubdivisionLevel):
	'''Increase the current Subdivision modifier level by one (adds a subD modifier if none exists).

	armoredColony.com '''

	bl_idname = 'view3d.armored_increase_subd_mod_level'
	bl_label = 'ARMORED Increase SubD modifier level'
	subd_add = 1


class VIEW3D_OT_decrease_subd_mod_level(bpy.types.Operator, AdjustSubdivisionLevel):
	'''Decrease the current Subdivision modifier level by one (adds a subD modifier if none exists).

	armoredColony.com '''
    
	bl_idname = 'view3d.armored_decrease_subd_mod_level'
	bl_label = 'ARMORED Decrease SubD modifier level'
	subd_add = -1


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

