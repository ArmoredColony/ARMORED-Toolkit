# v1.0

import bpy
import bmesh
from bpy.props import EnumProperty, BoolProperty

from mathutils import Vector
from mathutils import geometry


class MESH_OT_armored_flatten(bpy.types.Operator):
	'''Flattens your selection to the active face or the nearest axis.

armoredColony.com '''

	bl_idname = 'mesh.armored_flatten'
	bl_label = 'ARMORED Flatten'
	bl_options = {'REGISTER', 'UNDO'}

	alignment: EnumProperty(
		name='Alignment', default='NEAREST_AXIS', 
		description='Flatten selection to',
		items=[ ('NEAREST_AXIS', 'Nearest Axis', 'The axis nearest to the last selected element normal.'), 
			('ACTIVE_FACE',  'Active Face',  'The last selected element.'),
			# ('AVERAGED',      'Average',      'The average center and normals of your selection.'), 
			])
	
	active_is_none: BoolProperty()
	
	def draw(self, context):
		layout = self.layout
		
		if self.active_is_none:
			layout.label(text='Limited to Nearest Axis (see console)')
			return

		layout.label(text='Align to:')
		row = layout.row()
		row.prop(self, 'alignment', expand=True)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		self.active_is_none = False	# Flag to control what's drawn in the Redo Panel.

		ob = context.edit_object
		me = ob.data
		bm = bmesh.from_edit_mesh(me)
		bm.normal_update()

		sel_verts = {v for v in bm.verts if v.select}
		sel_faces = [f for f in bm.faces if f.select]
		
		# active_face = bm.select_history.active
		active_face = bm.faces.active	# NOTE: This returns the active face even if it's outside the current selection.
		
		if active_face is None or active_face not in sel_faces:
			self.active_is_none = True
			self.alignment = 'NEAREST_AXIS'

		if self.alignment == 'NEAREST_AXIS':
			target_normal = sum((v.normal for v in sel_faces), Vector()).normalized()
			target_center = sum((v.co for v in sel_verts), Vector()) / len(list(sel_verts))
			angles = self._construct_angle_to_axis_dict(self._abs_vector(target_normal))
			nearest_axis = min(angles, key=angles.get)

			for v in sel_verts:
				exec(f'v.co.{nearest_axis} = target_center.{nearest_axis}')

		elif self.alignment == 'ACTIVE_FACE':
			target_normal = active_face.normal
			target_center = active_face.calc_center_median()
			plane = [v.co for v in active_face.verts[:3]]

			for v in sel_verts:
				v.co = geometry.intersect_line_plane(
					v.co, v.co+target_normal, plane[0], target_normal)
		
		elif self.alignment == 'AVERAGED':
			raise NotImplementedError

		bm.normal_update()
		bmesh.update_edit_mesh(me)
		return {'FINISHED'}
	

	def _abs_vector(self, vector: Vector) -> Vector:
		'''Returns the absolute version of the input vector.'''

		return Vector([abs(axis) for axis in vector])

	
	def _construct_angle_to_axis_dict(self, target_normal: Vector) -> dict:
		'''Returns a Dict of the angles between the normal vector and the axis vectors.'''

		return {
			'x': target_normal.angle(Vector((1, 0, 0))), 
			'y': target_normal.angle(Vector((0, 1, 0))), 
			'z': target_normal.angle(Vector((0, 0, 1)))
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