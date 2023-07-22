version = (2, 0, 1)

import bpy
import bmesh
import mathutils


def get_items(self, context):
	items = [ 
		('AVERAGE',      'Average',      'Flattens to the average face normals.'), 
		('NEAREST_AXIS', 'Nearest Axis', 'Flattens to the closest axis plane.'), 
		('ACTIVE_FACE',  'Active Face',  'Flattens to the active face normal.'),
	]

	if self.active_is_none:
		del items[2]

	return items


class MESH_OT_armored_flatten(bpy.types.Operator):
	'''Flattens your selection to the best-fitting imaginary plane.

armoredColony.com '''

	bl_idname = 'mesh.armored_flatten'
	bl_label = 'ARMORED Flatten'
	bl_options = {'REGISTER', 'UNDO'}

	alignment: bpy.props.EnumProperty(
		name='Alignment', 
		# default='AVERAGE', # Can't use this default since items come from a function?
		description='Flatten selection to',
		items=get_items)
	
	active_is_none: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE', 'HIDDEN'})
		
	def draw(self, context):
		layout = self.layout
		layout.label(text='Flattening Plane:')
		row = layout.row()
		row.prop(self, 'alignment', expand=True)

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'

	def execute(self, context):
		# self.active_is_none = False	# FLAG TO CONTROL WHAT'S DRAWN IN THE REDO PANEL.

		ob = context.edit_object
		me = ob.data
		bm = bmesh.from_edit_mesh(me)
		bm.normal_update()

		# selection_mode = context.tool_settings.mesh_select_mode[:]

		sel_verts = {v for v in bm.verts if v.select}
		sel_faces = [f for f in bm.faces if f.select]
		
		# active_face = bm.select_history.active
		active_face = bm.faces.active	# THIS RETURNS THE ACTIVE FACE EVEN IF IT'S OUTSIDE THE CURRENT SELECTION.
		
		if active_face is None or active_face not in sel_faces:
			self.active_is_none = True
		
		if self.alignment == 'AVERAGE':

			target_normal = sum((f.normal for f in sel_faces), mathutils.Vector()).normalized()
			target_center = sum((v.co for v in sel_verts), mathutils.Vector()) / len(list(sel_verts))

			for v in sel_verts:
				v.co = mathutils.geometry.intersect_line_plane(
					v.co, v.co+target_normal, target_center, target_normal)

		elif self.alignment == 'NEAREST_AXIS':

			target_normal = sum((f.normal for f in sel_faces), mathutils.Vector()).normalized()
			target_center = sum((v.co for v in sel_verts), mathutils.Vector()) / len(list(sel_verts))

			angles = self._construct_angle_to_axis_dict(self._abs_vector(target_normal))
			nearest_axis = min(angles, key=angles.get)

			for v in sel_verts:
				exec(f'v.co.{nearest_axis} = target_center.{nearest_axis}')

		elif self.alignment == 'ACTIVE_FACE':

			target_normal = active_face.normal
			target_center = active_face.calc_center_median()

			plane = [v.co for v in active_face.verts[:3]]

			for v in sel_verts:
				v.co = mathutils.geometry.intersect_line_plane(
					v.co, v.co+target_normal, plane[0], target_normal)

		bm.normal_update()
		bmesh.update_edit_mesh(me)

		return {'FINISHED'}
	

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