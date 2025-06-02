version = (2, 1, 0)

import bpy
import bmesh


class Base:
	bl_options = {'REGISTER', 'UNDO'}


class SelectFacesBySides(Base):
	'''
	Abstract Class to Select Faces that match the side count criteria.
	'''

	polygon_type: str = NotImplemented	# Noun used in the report message (e.g. 'Ngon', 'Triangle', 'Non-Quad').

	# @classmethod
	# def poll(cls, context):
	# 	return context.mode == 'EDIT_MESH'
	
	def execute(self, context):
		if context.mode != 'EDIT_MESH':
			bpy.ops.object.mode_set(mode='EDIT')

		bpy.ops.mesh.reveal()	# For hidden faces.
		self.select_faces_by_sides()

		selected_face_count = self._get_selected_face_count(context)

		if selected_face_count:
			plural = 's' if selected_face_count != 1 else ''
			self.report({'ERROR'}, f'{selected_face_count} {self.polygon_type}{plural} found')
		else:
			self.report({'INFO'}, f'No {self.polygon_type}s found')

		return {'FINISHED'}

	def select_faces_by_sides(self) -> None:
		raise NotImplementedError

	def _get_selected_face_count(self, context) -> int:
		objects = context.objects_in_mode
		
		return sum(obj.data.total_face_sel for obj in objects)



class FilterObjectsWithFacesBySides(Base):
	'''
	Abstract class to Filter Objects with Faces that have the specified side count.
	'''

	polygon_type: str = NotImplemented	# Noun used in the report message (e.g. 'Ngons', 'Triangles', 'Non-Quads').

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'
	
	def execute(self, context):
		selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

		if not selected_objects:
			self.report({'INFO'}, 'Nothing selected')

			return {'CANCELLED'}

		filtered_objects = []

		for obj in selected_objects:
			bm = bmesh.new()
			bm.from_mesh(obj.data)

			if self.found_faces_by_sides(bm.faces):
				filtered_objects.append(obj)
		
		bpy.ops.object.select_all(action='DESELECT')

		if filtered_objects:
			for obj in filtered_objects:
				obj.select_set(True)

			count = len(filtered_objects)
			plural = 's' if count != 1 else ''
			message = f'Found {count} Object{plural} with {self.polygon_type}s'
			
			self.report({'ERROR'}, message)
		else:
			self.report({'INFO'}, f'No Objects with {self.polygon_type}s found')
		
		return {'FINISHED'}

	def found_faces_by_sides(self, faces: list[bmesh.types.BMFace]) -> bool:
		raise NotImplementedError


# EDIT MESH OPERATORS  __________________________________________________

class MESH_OT_armored_select_ngons(bpy.types.Operator, SelectFacesBySides):
	'''Select Ngons.
	
	armoredColony.com '''

	bl_idname = 'mesh.armored_select_ngons'
	bl_label = 'ARMORED Select Ngons'
	polygon_type = 'Ngon'

	def select_faces_by_sides(self) -> int:
		bpy.ops.mesh.select_face_by_sides(type='GREATER', number=4, extend=False)

		
class MESH_OT_armored_select_triangles(bpy.types.Operator, SelectFacesBySides):
	'''Select Triangles.

	armoredColony.com '''

	bl_idname = 'mesh.armored_select_triangles'
	bl_label = 'ARMORED Select Triangles'
	polygon_type = 'Triangle'
	
	def select_faces_by_sides(self) -> int:
		bpy.ops.mesh.select_face_by_sides(type='EQUAL', number=3, extend=False)


class MESH_OT_armored_select_non_quads(bpy.types.Operator, SelectFacesBySides):
	'''Select Non-Quads.

	armoredColony.com '''

	bl_idname = 'mesh.armored_select_non_quads'
	bl_label = 'ARMORED Select Non-Quads'
	polygon_type = 'Non-Quad'

	def select_faces_by_sides(self) -> int:
		bpy.ops.mesh.select_face_by_sides(type='EQUAL', number=3, extend=False)
		bpy.ops.mesh.select_face_by_sides(type='GREATER', number=4, extend=True)



# OBJECT MODE OPERATORS  __________________________________________________

class OBJECT_OT_armored_filter_objects_with_ngons(bpy.types.Operator, FilterObjectsWithFacesBySides):
	'''Filter Objects with Ngons.

	armoredColony.com '''

	bl_idname = 'object.armored_filter_objects_with_ngons'
	bl_label = 'ARMORED Filter Objects with Ngons'
	polygon_type = 'Ngon'

	def found_faces_by_sides(self, faces: list[bmesh.types.BMFace]) -> bool:
		return any(len(face.verts) > 4 for face in faces)
	

class OBJECT_OT_armored_filter_objects_with_triangles(bpy.types.Operator, FilterObjectsWithFacesBySides):
	'''Filter Objects with Triangles.

	armoredColony.com '''

	bl_idname = 'object.armored_filter_objects_with_triangles'
	bl_label = 'ARMORED Filter Objects with Triangles'
	polygon_type = 'Triangle'

	def found_faces_by_sides(self, faces: list[bmesh.types.BMFace]) -> bool:
		return any(len(face.verts) == 3 for face in faces)
	

class OBJECT_OT_armored_filter_objects_with_non_quads(bpy.types.Operator, FilterObjectsWithFacesBySides):
	'''Filter Objects with Non-Quads.

	armoredColony.com '''

	bl_idname = 'object.armored_filter_objects_with_non_quads'
	bl_label = 'ARMORED Filter Objects with Non-Quads'
	polygon_type = 'Non-Quad'

	def found_faces_by_sides(self, faces: list[bmesh.types.BMFace]) -> bool:
		return any(len(face.verts) != 4 for face in faces)


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