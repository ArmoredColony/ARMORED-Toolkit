version = (1, 3, 1)

import bpy
import bmesh


class ARMORED_OT_fast_bevel(bpy.types.Operator):
	'''Bevels different elements based on the selection mode.

	armoredColony.com '''
 
	bl_idname = 'mesh.armored_fast_bevel'
	bl_label = 'ARMORED Fast Bevel'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'

	def execute(self, context):
		selection_mode = context.tool_settings.mesh_select_mode[:]
 
		# VERTEX MODE
		if selection_mode[0]:
			bpy.ops.mesh.bevel('INVOKE_DEFAULT', affect='VERTICES')

			return {'FINISHED'}
			
		# FACE MODE
		if selection_mode[2]:
			self._region_to_loop(context)
		
		bpy.ops.mesh.bevel('INVOKE_DEFAULT', loop_slide=False)
		
		return {'FINISHED'}
	
	def _region_to_loop(self, context) -> None:
		'''
		Converts the current face selection to a loop selection without switching modes.
		'''
		
		# WE AVOID bpy.ops.mesh.region_to_loop() BECAUSE IS SWITCHES TO EDGE MODE,
		# WHICH PREVENTS US FROM REPEATEDLY SPAMMING fast_bevel ON THE RESULTING FACES.
		ob = context.edit_object
		me = ob.data
		bm = bmesh.from_edit_mesh(me)

		selection_border = [
			e for e in bm.edges 
				if e.select and (e.is_boundary or not all(f.select for f in e.link_faces))
				]
                
		bpy.ops.mesh.select_all(action='DESELECT')
		for e in selection_border: 
			e.select = True


classes = (
	ARMORED_OT_fast_bevel,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)