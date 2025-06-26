version = (2, 2, 0)


import bpy
import bmesh
import mathutils


def find_most_parallel_axis(dir_vec: mathutils.Vector) -> str:
	'''
	RETURNS:
		Key (str) of the most parallel axis.
	'''
	
	world_axes = {
		'x': mathutils.Vector((1, 0, 0)),
		'y': mathutils.Vector((0, 1, 0)),
		'z': mathutils.Vector((0, 0, 1))
	}

	# Just in case
	dir_vec = dir_vec.normalized()

	most_parallel_axis_key = max(
		world_axes, key=lambda a: 
			abs( dir_vec.dot(world_axes[a]) )
	)

	return most_parallel_axis_key


def average_face_normals(matrix: mathutils.Matrix, faces: list[bmesh.types.BMFace]) -> mathutils.Vector:
	
	M = matrix.to_3x3()
	avg = sum((f.normal for f in faces), mathutils.Vector())

	return (M @ avg).normalized()
	

def average_vert_co(matrix: mathutils.Matrix, verts: list[bmesh.types.BMVert]) -> mathutils.Vector:
	return sum((matrix @ v.co for v in verts), mathutils.Vector()) / len(verts)


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

	space: bpy.props.EnumProperty(
		name='space', 
		default='GLOBAL',
		items=[
			('GLOBAL', 'Global', ''), 
			('LOCAL',  'Local',  ''), 
		],
	)

	active_is_none: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE', 'HIDDEN'})
	
	def draw(self, context):
		layout = self.layout
		layout.label(text='Projection Plane:')
		row = layout.row()
		row.prop(self, 'projection_plane', expand=True)
	
		if self._initialized and self.projection_plane == 'NEAREST_ORTHO':
			row = layout.row()
			row.prop(self, 'space', expand=True)

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'
	
	def invoke(self, context, event):
		self._initialized = False

		return context.window_manager.invoke_props_popup(self, event)

	def execute(self, context):
		self._initialized = True
		obj = context.edit_object
		mesh = obj.data
		bm = bmesh.from_edit_mesh(mesh)
		bm.normal_update()

		sel_verts = [v for v in bm.verts if v.select]
		sel_faces = {f for f in bm.faces if f.select}
		
		active_face = bm.faces.active

		if self.projection_plane == 'NEAREST_ORTHO' and self.space == 'GLOBAL':
			matrix = obj.matrix_world
		else:
			matrix = mathutils.Matrix.Identity(4)

		# Both modes use the same starting data.
		if self.projection_plane in {'AVERAGE', 'NEAREST_ORTHO'}:
			target_normal = average_face_normals(matrix, faces=sel_faces)
			target_center = average_vert_co(matrix, verts=sel_verts)

			
		if self.projection_plane == 'AVERAGE':
			for v in sel_verts:
				distance = (v.co - target_center).dot(target_normal)
				v.co -= target_normal * distance

		elif self.projection_plane == 'NEAREST_ORTHO':
			axis_key = find_most_parallel_axis(dir_vec=target_normal)

			for v in sel_verts:
				co = matrix @ v.co                      		 # Convert to working space
				setattr(co, axis_key, getattr(target_center, axis_key))  # Flatten on that axis
				v.co = matrix.inverted() @ co                 		 # Back to local space

		elif self.projection_plane == 'ACTIVE_FACE':
			if active_face is None or active_face not in sel_faces:
				self.report({'WARNING'}, 'Active Face is None')
				return {'FINISHED'}

			target_normal = active_face.normal
			target_center = active_face.calc_center_median()

			for v in sel_verts:
				distance = (v.co - target_center).dot(target_normal)	# Same as `distance_point_to_plane`
				v.co -= target_normal * distance

		bm.normal_update()
		bmesh.update_edit_mesh(mesh)

		return {'FINISHED'}
	

classes = (
	MESH_OT_armored_flatten,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)