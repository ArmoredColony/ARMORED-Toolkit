version = (2, 1, 0)


import bpy
import bmesh
import mathutils


def get_items(self, context):
	items = [ 
		('AVERAGE',		'Average',		'Flattens to the average face normals.'), 
		('NEAREST_ORTHO',	'Nearest Ortho',	'Flattens to the nearest orthographic plane.'), 
		('ACTIVE_FACE',		'Active Face',		'Flattens to the active face normal.'),
	]

	return items


class MESH_OT_armored_flatten(bpy.types.Operator):
	'''Flattens your selection to an imaginary plane.

	armoredColony.com '''

	bl_idname = 'mesh.armored_flatten'
	bl_label = 'ARMORED Flatten'
	bl_options = {'REGISTER', 'UNDO'}

	projection_plane: bpy.props.EnumProperty(
		name='Projection Plane', 
		default=-1,
		items=get_items,
		options={'SKIP_SAVE'},
	)
	
	active_is_none: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE', 'HIDDEN'})
		
	def draw(self, context):
		layout = self.layout
		layout.label(text='Projection Plane:')
		row = layout.row()
		row.prop(self, 'projection_plane', expand=True)

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_popup(self, event)

	def execute(self, context):
		obj = context.edit_object
		self.mesh = obj.data
		self.bm = bmesh.from_edit_mesh(self.mesh)
		self.bm.normal_update()

		sel_verts = [v for v in self.bm.verts if v.select]
		sel_faces = {f for f in self.bm.faces if f.select}
		
		active_face = self.bm.faces.active

		# Both modes use the same starting data.
		if self.projection_plane in {'AVERAGE', 'NEAREST_ORTHO'}:
			target_normal, target_center = self._average_normal_and_center(sel_faces, sel_verts)
			
	
		if self.projection_plane == 'AVERAGE':

			for v in sel_verts:
				distance = (v.co - target_center).dot(target_normal)
				v.co -= target_normal * distance

		elif self.projection_plane == 'NEAREST_ORTHO':
			
			# Finds the axis vector nearest to the average normal
			# and applies the average vert.co location in that same axis to all verts.
			angles = self._construct_angle_to_axis_dict(self._abs_vector(target_normal))
			nearest_axis = min(angles, key=angles.get)

			for v in sel_verts:
				setattr(v.co, nearest_axis, getattr(target_center, nearest_axis))

		elif self.projection_plane == 'ACTIVE_FACE':

			if active_face is None or active_face not in sel_faces:
				self.report({'WARNING'}, 'Active Face is None')
				return {'FINISHED'}

			target_normal = active_face.normal
			target_center = active_face.calc_center_median()

			for v in sel_verts:
				distance = (v.co - target_center).dot(target_normal)
				v.co -= target_normal * distance

		self.bm.normal_update()
		bmesh.update_edit_mesh(self.mesh)

		return {'FINISHED'}
	
	def _average_normal_and_center(self, faces, verts):
		'''
		Calculates the average normal and center of the selected faces and vertices.
		'''
		
		target_normal = sum((f.normal for f in faces), mathutils.Vector()).normalized()
		target_center = sum((v.co for v in verts), mathutils.Vector()) / len(verts)

		return target_normal, target_center

	def _abs_vector(self, vector: mathutils.Vector) -> mathutils.Vector:
		'''
		Returns the absolute version of the input vector.
		'''

		return mathutils.Vector([abs(axis) for axis in vector])

	
	def _construct_angle_to_axis_dict(self, vector: mathutils.Vector) -> dict:
		'''
		Returns a Dict of the angles between the input vector and the axis vectors.
		'''

		return {
			'x': vector.angle(mathutils.Vector((1, 0, 0))), 
			'y': vector.angle(mathutils.Vector((0, 1, 0))), 
			'z': vector.angle(mathutils.Vector((0, 0, 1)))
		}


classes = (
	MESH_OT_armored_flatten,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)