version = (2, 0, 0)


import bpy
import bmesh
import mathutils
import typing


BMVertChain: typing.TypeAlias = list[bmesh.types.BMVert]


DEBUG_MODE = False


def get_selected_verts(bm):
	return [v for v in bm.verts if v.select]


def verts_are_linked(verts: list[bmesh.types.BMVert]) -> bool:
	'''
	Returns True if the verts form a single linked chain with no unselected verts inbetween.
	'''

	if len(verts) < 2:
		return False

	outer_verts = find_outer_verts(verts)
	if len(outer_verts) != 2:
		return False

	visited = set()
	stack = [outer_verts[0]]

	for _ in range(len(verts)):
		if not stack:
			break

		current = stack.pop()
		if current in visited:
			continue

		visited.add(current)

		for edge in current.link_edges:
			other = edge.other_vert(current)
			if other in verts and other not in visited:
				stack.append(other)

	return len(visited) == len(verts)


def order_verts_by_topology(verts: BMVertChain) -> list[bmesh.types.BMVert]:
	'''
	Order the verts by their topological links
	(requires a linked vert chain for valid results). 
	'''

	outer_verts = find_outer_verts(verts)
	start = outer_verts[0]

	ordered = [start]
	current = start

	for _ in range(len(verts) - 1):
		for edge in current.link_edges:
			other = edge.other_vert(current)
			if other in verts and other not in ordered:
				ordered.append(other)
				current = other
				break
		else:
			# No valid unvisited neighbor found
			break

	return ordered


def find_outer_verts(verts: BMVertChain):
	'''
	Find the first and last verts of a list of linked verts
	(requires a linked vert chain for accurate results).
	'''

	return [v for v in verts if sum(1 for e in v.link_edges if e.other_vert(v) in verts) == 1]


class Neighbors:
	'''
	Methods used to find the unselected neighbors of a vert.
	'''
	
	@staticmethod
	def most_perpendicular(vert, side_a_verts, side_b_verts):
		'''
		Uses dot product to find the most perpendicular neighbor verts.
		'''

		def get_most_perpendicular_vert(
			ref_vert: bmesh.types.BMVert, 
			ref_vector: mathutils.Vector, 
			candidate_verts: list[bmesh.types.BMVert]
		):
			closest_abs_dot = 1.0  # Max possible dot for unit vectors
			best_match = None

			for other_vert in candidate_verts:
				dir_to_other = (other_vert.co - ref_vert.co).normalized()
				dot = ref_vector.dot(dir_to_other)
				abs_dot = abs(dot)

				if abs_dot < closest_abs_dot:
					closest_abs_dot = abs_dot
					best_match = other_vert

			return best_match
		
		selected_neighbors = [e.other_vert(vert) for e in vert.link_edges if e.other_vert(vert).select]
		_prev_vert, next_vert = selected_neighbors
		
		dir_vec = (next_vert.co - vert.co).normalized()

		v1 = get_most_perpendicular_vert(vert, dir_vec, side_a_verts)
		v2 = get_most_perpendicular_vert(vert, dir_vec, side_b_verts)
		
		return v1, v2
	
	@staticmethod
	def closest(vert, side_a_verts, side_b_verts):
		v1 = min(side_a_verts, key=lambda v: (v.co - vert.co).length, default=None)
		v2 = min(side_b_verts, key=lambda v: (v.co - vert.co).length, default=None)

		return v1, v2
	
	@staticmethod
	def furthest(vert, side_a_verts, side_b_verts):
		v1 = max(side_a_verts, key=lambda v: (v.co - vert.co).length, default=None)
		v2 = max(side_b_verts, key=lambda v: (v.co - vert.co).length, default=None)

		return v1, v2
	
	@staticmethod
	def index_adjacent(vert, side_a_verts, side_b_verts):
		v1 = side_a_verts[0]
		v2 = side_b_verts[-1]

		return v1, v2
	
	@staticmethod
	def index_opposite(vert, side_a_verts, side_b_verts):
		v1 = side_a_verts[-1]
		v2 = side_b_verts[0]

		return v1, v2


class Alignment:
	'''
	Methods that return new endpoint coordinates for the desirged alignment.
	'''

	@staticmethod
	def from_endpoints(verts):
		'''
		Returns start and end points of the vector formed by endpoints.
		'''
		return verts[0].co, verts[-1].co

	@staticmethod
	def from_axis(verts, axis_strategy, matrix) -> tuple[mathutils.Vector, mathutils.Vector]:
		if axis_strategy in {'NEAREST_GLOBAL', 'NEAREST_LOCAL'}:
			return Alignment._nearest_axis(verts, matrix)
		
		if axis_strategy in {'GLOBAL_X', 'LOCAL_X'}:
			return Alignment._axis_x(verts, matrix)

		if axis_strategy in {'GLOBAL_Y', 'LOCAL_Y'}:
			return Alignment._axis_y(verts, matrix)

		if axis_strategy in {'GLOBAL_Z', 'LOCAL_Z'}:
			return Alignment._axis_z(verts, matrix)

	@staticmethod
	def _nearest_axis(verts, matrix) -> tuple[mathutils.Vector, mathutils.Vector]:
		'''
		Returns start and end points aligned to the closest global axis.
		'''
		
		xform_coords = [matrix @ v.co for v in verts]

		# Compute average position in the xform space
		avg = sum(xform_coords, mathutils.Vector()) / len(xform_coords)

		# Direction vector in xform space
		xform_start = xform_coords[ 0]
		xform_end   = xform_coords[-1]
		dir_vec = (xform_end - xform_start).normalized()

		# Global axis directions (world space)
		world_axes = {
			'X': mathutils.Vector((1, 0, 0)),
			'Y': mathutils.Vector((0, 1, 0)),
			'Z': mathutils.Vector((0, 0, 1))
		}

		# Find axis with the highest absolute alignment
		def axis_distance(axis_vec):
			return dir_vec.dot(axis_vec)

		closest_axis = max(world_axes, key=lambda a: abs(axis_distance(world_axes[a])))

		# Project start/end along the closest axis (world space)
		if closest_axis == 'X':
			start = (xform_start.x, avg.y, avg.z)
			end   = (xform_end.x,   avg.y, avg.z)
		elif closest_axis == 'Y':
			start = (avg.x, xform_start.y, avg.z)
			end   = (avg.x,   xform_end.y, avg.z)
		else:  # Z
			start = (avg.x, avg.y, xform_start.z)
			end   = (avg.x, avg.y, xform_end.z)

		# Return in object space
		return matrix.inverted() @ mathutils.Vector(start), matrix.inverted() @ mathutils.Vector(end)
	
	@staticmethod
	def _axis_x(verts, matrix) -> tuple[mathutils.Vector, mathutils.Vector]:
		avg = sum((matrix @ v.co for v in verts), mathutils.Vector()) / len(verts)

		start = ((matrix @ verts[ 0].co).x, avg.y, avg.z)
		end   = ((matrix @ verts[-1].co).x, avg.y, avg.z)

		return matrix.inverted() @ mathutils.Vector(start), matrix.inverted() @ mathutils.Vector(end)
	
	@staticmethod
	def _axis_y(verts, matrix) -> tuple[mathutils.Vector, mathutils.Vector]:
		avg = sum((matrix @ v.co for v in verts), mathutils.Vector()) / len(verts)

		start = (avg.x, (matrix @ verts[ 0].co).y, avg.z)
		end   = (avg.x, (matrix @ verts[-1].co).y, avg.z)

		return matrix.inverted() @ mathutils.Vector(start), matrix.inverted() @ mathutils.Vector(end)
	
	@staticmethod
	def _axis_z(verts, matrix) -> tuple[mathutils.Vector, mathutils.Vector]:
		avg = sum((matrix @ v.co for v in verts), mathutils.Vector()) / len(verts)

		start = (avg.x, avg.y, (matrix @ verts[ 0].co).z)
		end   = (avg.x, avg.y, (matrix @ verts[-1].co).z)

		return matrix.inverted() @ mathutils.Vector(start), matrix.inverted() @ mathutils.Vector(end)


def find_best_neighbors(vert, neighbor_strategy) -> tuple[bmesh.types.BMVert, bmesh.types.BMVert] | None:
	'''
	RETURNS:
		A pair of unselected verts based on the chosen neighbor strategy.
	'''

	# Find the two selected edges and their loops
	selected_loops = [loop for loop in vert.link_loops if loop.edge.select]

	if len(selected_loops) != 2:
		raise ValueError('Vertex must have exactly 2 selected edges - This code should be unreachable')

	loop_a, loop_b = selected_loops

	# We need to get verts on each side of the selected vert and group them separetely.
	# Each side is determined by navigating through bm_loops until a selected edge is found. 
	def find_linked_side_verts(loop_start: bmesh.types.BMLoop):
		'''
		Find unselected linked verts on one side of the selected vert.
		'''
		
		verts = []
		loop = loop_start

		for _ in range(len(vert.link_loops)):
			loop = loop.link_loop_radial_prev.link_loop_next

			if loop.edge.select:
				break

			verts.append(loop.edge.other_vert(vert))

		return verts

	side_a_verts = find_linked_side_verts(loop_start=loop_a)
	side_b_verts = find_linked_side_verts(loop_start=loop_b)

	if not side_a_verts or not side_b_verts:
		return None

	if DEBUG_MODE:
		print()
		print('side a verts', [vert.index for vert in side_a_verts])
		print('side b verts', [vert.index for vert in side_b_verts])

	if neighbor_strategy == 'MOST_PERPENDICULAR':
		return Neighbors.most_perpendicular(vert, side_a_verts, side_b_verts)
	
	if neighbor_strategy == 'CLOSEST':
		return Neighbors.closest(vert, side_a_verts, side_b_verts)

	if neighbor_strategy == 'FURTHEST':
		return Neighbors.furthest(vert, side_a_verts, side_b_verts)
	
	if neighbor_strategy == 'INDEX_ADJACENT':
		return Neighbors.index_adjacent(vert, side_a_verts, side_b_verts)

	if neighbor_strategy == 'INDEX_OPPOSITE':
		return Neighbors.index_opposite(vert, side_a_verts, side_b_verts)


class Redistribute:
	'''
	Methods that take an ordered list of verts and redistributes them between 2 coordinates.
	'''
	
	@staticmethod
	def predictive_spacing(start_co, end_co, verts, neighbor_strategy) -> None:
		'''
		Space the verts so that the unselected neighbor verts are also aligned.
		'''
		
		if len(verts) < 2:
			return
		
		# Move endpoints first and intermediate verts later.
		verts[0].co  = start_co
		verts[-1].co = end_co

		intermediate_verts = verts[1:-1]

		if not intermediate_verts:
			return

		for vert in intermediate_verts:
			# Abort if we don't have enough edges.
			if len(vert.link_edges) < 4:
				continue

			neighbor_verts = find_best_neighbors(vert, neighbor_strategy=neighbor_strategy)

			# Insufficient verts on one side.
			if neighbor_verts is None:
				continue

			n1, n2 = neighbor_verts
			if DEBUG_MODE:
				print(f'vert {vert.index} neighbors: {n1.index} and {n2.index}')

			# Get the closest points on each line to the other
			intersect = mathutils.geometry.intersect_line_line(n1.co, n2.co, start_co, end_co)
			vert.co = intersect[1]

	@staticmethod
	def even_spacing(start_co, end_co, verts, matrix, space) -> None:
		'''
		Space the verts evenly between the two endpoints.

		'''

		for i, v in enumerate(verts):
			t = i / (len(verts) - 1)
			v.co = start_co.lerp(end_co, t)
			
	@staticmethod
	def find_normalized_positions(verts) -> list[float]:
		'''
		Calculate the normalized vert positions 
		(first vert is at 0.0 and last at 1.0).
		'''

		if len(verts) < 2:
			return [0.0] * len(verts)

		cumulative = [0.0]
		total_length = 0.0

		for i in range(1, len(verts)):
			seg_len = (verts[i].co - verts[i-1].co).length
			total_length += seg_len
			cumulative.append(total_length)

		# Normalize cumulative distances to range [0, 1]
		return [d / total_length for d in cumulative]

	@staticmethod
	def relative_spacing(start_co, end_co, verts, normalized_positions) -> None:
		'''
		Space the verts between two endpoints while maintaining their relative spacing.
		'''

		if len(verts) < 2:
			return

		dir_vec = end_co - start_co

		for v, t in zip(verts, normalized_positions):
			v.co = start_co + t * dir_vec


class ARMORED_OT_align_verts(bpy.types.Operator):
	'''Aligns your selection of edges/vertices in a straignt line.

	armoredColony.com '''
	
	bl_idname = 'mesh.armored_align_verts'
	bl_label = 'ARMORED Align Vertices'
	bl_options = {'REGISTER', 'UNDO'}

	alignment: bpy.props.EnumProperty(
		name='Alignment',
		default='ENDPOINTS',
		items=[ 
			('ENDPOINTS',	'Endpoints',	'Align within the first and last verts of the selection.'), 
			('AXIS',	'Axis',		'Align with a global or local axis.'), 
		],
	)

	axis: bpy.props.EnumProperty( 
		name='Axis', 
		description='Axis the verts will align to',
		items=[
			('NEAREST_GLOBAL',	'Nearest Global',	''),
			('NEAREST_LOCAL',	'Nearest Local',	''),
			('GLOBAL_X',		'Global X',		''),
			('GLOBAL_Y',		'Global Y',		''),
			('GLOBAL_Z',		'GLobal Z',		''),
			('LOCAL_X',		'Local X',		''),
			('LOCAL_Y',		'Local Y',		''),
			('LOCAL_Z',		'Local Z',		''),
		],
	)

	spacing: bpy.props.EnumProperty( 
		name='Spacing', 
		default='RELATIVE',
		items=[ 
			('RELATIVE',	'Relative',	'Maintain the relative spacing between verts'),
			('PREDICTIVE',	'Predictive',	'Distribute the verts so that neighboring verts are also aligned'),
			('EVEN',	'Even',		'Distribute the verts evenly'),
		]
	)

	neighbors: bpy.props.EnumProperty( 
		name='Neighbors', 
		description=(
			'Method used to find the neighbor verts of the selected verts '
			'when dealing with non-quad topology.'
		),
		items=[
			('MOST_PERPENDICULAR',	'Most Perpendicular ',	''),
			('CLOSEST',		'Closest',		''),
			('FURTHEST',		'Furthest',		''),
			# ('INDEX_ADJACENT',	'Index Adjacent',	''),
			# ('INDEX_OPPOSITE',	'Index Opposite',	''),
		],
	)

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.label(text='Alignment:')
		row.prop(self, 'alignment', expand=True)

		if self.alignment == 'AXIS':
			row = layout.row()
			row.prop(self, 'axis')

		layout.separator(factor=2)
		row = layout.row()
		row.label(text='Spacing:')
		row.prop(self, 'spacing', expand=True)

		if self.spacing == 'PREDICTIVE':
			row = layout.row()
			row.prop(self, 'neighbors')
		
		layout.separator(factor=2)
		layout.operator('wm.operator_defaults', text='Reset')
		
		
	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'
	
	def execute(self, context):
		obj = context.active_object
		mesh = obj.data
		bm = bmesh.from_edit_mesh(mesh)

		selected_verts = get_selected_verts(bm)

		if verts_are_linked(selected_verts) == False:
			self.report({'WARNING'}, 'Vert selection must be continuous')
			return {'FINISHED'}
		
		verts = order_verts_by_topology(selected_verts)

		if self.alignment == 'AXIS' and self.axis in {'NEAREST_GLOBAL', 'GLOBAL_X', 'GLOBAL_Y', 'GLOBAL_Z'}:
			matrix = obj.matrix_world
		else:
			matrix = mathutils.Matrix.Identity(4)

		# This block only calculates the start and end points, no vertices are moved.
		if self.alignment == 'ENDPOINTS':
			start_co, end_co = Alignment.from_endpoints(verts)

		elif self.alignment == 'AXIS':
			start_co, end_co = Alignment.from_axis(verts, axis_strategy=self.axis, matrix=matrix)


		if self.spacing in {'RELATIVE', 'PREDICTIVE'}:
			_normalized_positions = Redistribute.find_normalized_positions(verts)
			Redistribute.relative_spacing(start_co, end_co, verts, _normalized_positions)

			if self.spacing == 'PREDICTIVE':
				# The relative spacing makes this more accurate.
				Redistribute.predictive_spacing(start_co, end_co, verts, neighbor_strategy=self.neighbors)

		elif self.spacing == 'EVEN':       
			Redistribute.even_spacing(start_co, end_co, verts, matrix, self.axis)

		bmesh.update_edit_mesh(mesh)
		
		return {'FINISHED'}


classes = (
	ARMORED_OT_align_verts,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)