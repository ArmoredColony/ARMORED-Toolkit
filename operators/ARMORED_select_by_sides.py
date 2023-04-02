version = (2, 0, 0)

import bpy
import bmesh


class Base:
	bl_options = {'REGISTER', 'UNDO'}


class SelectFacesBySides(Base):
	'''
	Abstract Class to Select Faces that match the side count criteria.
	'''

	report_name: str = NotImplemented	# Noun used in the report message (e.g. 'Ngons', 'Triangles', 'Non-Quads').

	# @classmethod
	# def poll(cls, context):
	# 	return context.mode == 'EDIT_MESH'
	
	def execute(self, context):
		if context.mode != 'EDIT_MESH':
			bpy.ops.object.mode_set(mode='EDIT')

		self.select_faces_by_sides()

		selected_face_count = self._get_selected_face_count(context)

		if selected_face_count:
			self.report({'ERROR'}, f'{selected_face_count} {self.report_name} found')
		else:
			self.report({'WARNING'}, f'No {self.report_name} found')

		return {'FINISHED'}

	def select_faces_by_sides(self) -> None:
		raise NotImplementedError

	def _get_selected_face_count(self, context) -> int:
		objects = context.objects_in_mode
		
		return sum(obj.data.total_face_sel for obj in objects)



class FilterObjectsWithFacesBySides(Base):
	'''
	Abstract class to Filter Objects with Faces that match the side count criteria.
	'''

	report_name: str = NotImplemented	# Noun used in the report message (e.g. 'Ngons', 'Triangles', 'Non-Quads').

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

		if not selected_objects:
			self.report({'WARNING'}, 'Nothing selected')

			return {'CANCELLED'}

		objects_with_match_hits = []

		for obj in selected_objects:
			bm = bmesh.new()
			bm.from_mesh(obj.data)

			if self.found_faces_by_sides(bm.faces):
				objects_with_match_hits.append(obj)
		
		bpy.ops.object.select_all(action='DESELECT')

		if objects_with_match_hits:
			for obj in objects_with_match_hits:
				obj.select_set(True)

			self.report({'ERROR'}, f'{len(objects_with_match_hits)} Objects have {self.report_name}')
		else:
			self.report({'WARNING'}, f'No Objects with {self.report_name} found')
		
		return {'FINISHED'}

	def found_faces_by_sides(self, faces: list[bmesh.types.BMFace]) -> bool:
		raise NotImplementedError


##########################################################
# OBJECT MODE OPERATORS


class OBJECT_OT_armored_filter_objects_with_ngons(bpy.types.Operator, FilterObjectsWithFacesBySides):
	'''Filter Objects with Ngons.

	armoredColony.com '''

	bl_idname = 'object.armored_filter_objects_with_ngons'
	bl_label = 'ARMORED Filter Objects with Ngons'
	report_name = 'Ngons'

	def found_faces_by_sides(self, faces: list[bmesh.types.BMFace]) -> bool:
		return any(len(face.verts) > 4 for face in faces)
	

class OBJECT_OT_armored_filter_objects_with_triangles(bpy.types.Operator, FilterObjectsWithFacesBySides):
	'''Filter Objects with Triangles.

	armoredColony.com '''

	bl_idname = 'object.armored_filter_objects_with_triangles'
	bl_label = 'ARMORED Filter Objects with Triangles'
	report_name = 'Triangles'

	def found_faces_by_sides(self, faces: list[bmesh.types.BMFace]) -> bool:
		return any(len(face.verts) == 3 for face in faces)
	

class OBJECT_OT_armored_filter_objects_with_non_quads(bpy.types.Operator, FilterObjectsWithFacesBySides):
	'''Filter Objects with Non-Quads.

	armoredColony.com '''

	bl_idname = 'object.armored_filter_objects_with_non_quads'
	bl_label = 'ARMORED Filter Objects with Non-Quads'
	report_name = 'Non-Quads'

	def found_faces_by_sides(self, faces: list[bmesh.types.BMFace]) -> bool:
		return any(len(face.verts) != 4 for face in faces)


##########################################################
# EDIT MESH OPERATORS


class MESH_OT_armored_select_ngons(bpy.types.Operator, SelectFacesBySides):
	'''Select Ngons.
	
	armoredColony.com '''

	bl_idname = 'mesh.armored_select_ngons'
	bl_label = 'ARMORED Select Ngons'
	report_name = 'Ngons'

	def select_faces_by_sides(self) -> int:
		bpy.ops.mesh.select_face_by_sides(type='GREATER', number=4, extend=False)

		
class MESH_OT_armored_select_triangles(bpy.types.Operator, SelectFacesBySides):
	'''Select Triangles.

	armoredColony.com '''

	bl_idname = 'mesh.armored_select_triangles'
	bl_label = 'ARMORED Select Triangles'
	report_name = 'Triangles'
	
	def select_faces_by_sides(self) -> int:
		bpy.ops.mesh.select_face_by_sides(type='EQUAL', number=3, extend=False)


class MESH_OT_armored_select_non_quads(bpy.types.Operator, SelectFacesBySides):
	'''Select Non-Quads.

	armoredColony.com '''

	bl_idname = 'mesh.armored_select_non_quads'
	bl_label = 'ARMORED Select Non-Quads'
	report_name = 'Non-Quads'

	def select_faces_by_sides(self) -> int:
		bpy.ops.mesh.select_face_by_sides(type='EQUAL', number=3, extend=False)
		bpy.ops.mesh.select_face_by_sides(type='GREATER', number=4, extend=True)


classes = (
	OBJECT_OT_armored_filter_objects_with_ngons,
	OBJECT_OT_armored_filter_objects_with_triangles,
	OBJECT_OT_armored_filter_objects_with_non_quads,
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