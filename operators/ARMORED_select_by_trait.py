# v1.0

import bpy


class SelectBySides:
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None
	
	def _get_sel_face_count(self, context):
		objects = context.objects_in_mode
		return sum(obj.data.total_face_sel for obj in objects)


class MESH_OT_armored_select_ngons(bpy.types.Operator, SelectBySides):
	'''Select Ngons.

armoredColony.com '''

	bl_idname = 'mesh.armored_select_ngons'
	bl_label = 'ARMORED Select Ngons'

	def execute(self, context):
		bpy.ops.mesh.select_face_by_sides(type='GREATER', number=5, extend=False)

		sel_count = self._get_sel_face_count(context)
		if sel_count:
			self.report({'ERROR'}, f'{sel_count} Ngons found')

		return {'FINISHED'}
	

		
class MESH_OT_armored_select_triangles(bpy.types.Operator, SelectBySides):
	'''Select Triangles.

armoredColony.com '''

	bl_idname = 'mesh.armored_select_triangles'
	bl_label = 'ARMORED Select Triangles'

	def execute(self, context):
		bpy.ops.mesh.select_face_by_sides(type='EQUAL', number=3, extend=False)

		sel_count = self._get_sel_face_count(context)
		if sel_count:
			self.report({'ERROR'}, f'{sel_count} Triangles found')
			
		return {'FINISHED'}


class MESH_OT_armored_select_non_quads(bpy.types.Operator, SelectBySides):
	'''Select Non-Quads.

armoredColony.com '''

	bl_idname = 'mesh.armored_select_non_quads'
	bl_label = 'ARMORED Select Non-Quads'

	def execute(self, context):
		bpy.ops.mesh.select_face_by_sides(type='EQUAL', number=3, extend=False)
		bpy.ops.mesh.select_face_by_sides(type='GREATER', number=4, extend=True)

		sel_count = self._get_sel_face_count(context)
		if sel_count:
			self.report({'ERROR'}, f'{sel_count} non-Quads found')
			
		return {'FINISHED'}


classes = (
	MESH_OT_armored_select_ngons,
	MESH_OT_armored_select_triangles,
	MESH_OT_armored_select_non_quads,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)