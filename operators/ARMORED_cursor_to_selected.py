version = (1, 0, 0)

import bpy
import bmesh
import mathutils


class MESH_OT_armored_cursor_to_selected(bpy.types.Operator):
	'''Move the cursor to the selected element and rotate it to match its normal.

armoredColony.com '''

	bl_idname = 'mesh.armored_cursor_to_selected'
	bl_label = 'ARMORED Cursor to Selected'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		ob = context.edit_object
		me = ob.data
		bm = bmesh.from_edit_mesh(me)
		# bm.normal_update()

		mode = context.tool_settings.mesh_select_mode[:]

		if mode[0]:
			verts = [v for v in bm.verts if v.select]
			if verts:
				element = verts[0]
				context.scene.cursor.location = ob.matrix_world @ element.co

		elif mode[1]:
			edges = [e for e in bm.edges if e.select]
			if edges:
				element = edges[0]
				# context.scene.cursor.location = sum(map(lambda v: ob.matrix_world @ v.co, element.verts), mathutils.Vector()) / 2
				context.scene.cursor.location = ob.matrix_world @ ((element.verts[0].co + element.verts[1].co) / 2)
		
		elif mode[2]:
			faces = [f for f in bm.faces if f.select]
			if faces:
				element = faces[0]
				context.scene.cursor.location = ob.matrix_world @ element.calc_center_median_weighted()
		
		element.normal_update()

		if isinstance(element, bmesh.types.BMEdge):
			direction_vector = sum(map(lambda f: f.normal, element.link_faces), mathutils.Vector()) / 2
		else:
			direction_vector = element.normal

		up = mathutils.Vector((0, 0, 1))
		rotation = up.rotation_difference(direction_vector).to_euler()

		context.scene.cursor.rotation_euler = rotation

		return {'FINISHED'}


classes = (
	MESH_OT_armored_cursor_to_selected,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)