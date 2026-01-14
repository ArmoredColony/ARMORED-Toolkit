import blf
import bmesh
import gpu
import mathutils
import typing

from gpu_extras.batch import batch_for_shader


#  NEW TYPES __________________________________________________
RGBA = tuple[float, float, float, float]


def vert_or_point(elem) -> bool:
	return isinstance(elem, bmesh.types.BMVert) or isinstance(elem, mathutils.Vector)


def edge_or_line(elem) -> bool:
	if isinstance(elem, bmesh.types.BMEdge):
		return True
	
	if isinstance(elem, tuple) and len(elem) == 2:
		a, b = elem

		return isinstance(a, mathutils.Vector) and isinstance(b, mathutils.Vector)
	
	return False


def face_or_poly(elem) -> bool:
	if isinstance(elem, bmesh.types.BMFace):
		return True
	
	if isinstance(elem, tuple) and len(elem) >= 3:
		return all(isinstance(v, mathutils.Vector) for v in elem)
	
	return False


#  ABSTRACT CLASSES __________________________________________________
class Tracer(typing.Protocol):
	
	def create_shader(self) -> gpu.types.GPUShader:
		pass

	def update(self) -> None:
		pass


#  GPU DRAWING CLASSES __________________________________________________

class PointTracer():
	'''
	Draw Points or BMesh Verts.
	'''
	
	def __init__(
		self, 
		size: int = 5, 
		color: RGBA = (1, 1, 1, 1), 
		matrix: mathutils.Matrix = None, 
		depth_test: bool = False
	):
		if matrix is None:
			matrix = mathutils.Matrix.Identity(4)
			
		self.matrix = matrix
		self.color  = color
		self.size   = size
		self.shader = self.create_shader()
		self.batch  = None
		self.depth_test = depth_test

	def create_shader(self) -> gpu.types.GPUShader:
		return gpu.shader.from_builtin('UNIFORM_COLOR')
	
	def update(self) -> None:
		if self.depth_test:
			gpu.state.depth_test_set('LESS_EQUAL')
		gpu.state.blend_set('ALPHA')
		gpu.state.point_size_set(self.size)

		self.shader.bind()
		self.shader.uniform_float('color', self.color)

		self.batch.draw(self.shader)
		gpu.state.depth_test_set('NONE')
	
	def draw_points(self, points: list[mathutils.Vector | bmesh.types.BMVert]) -> None:
		'''
		Draw multiple Points or BMesh Verts.
		'''

		if not points:
			return

		coords = []
		for point in points:
			if isinstance(point, bmesh.types.BMVert):
				point = point.co

			coords.append(self.matrix @ point)
		
		self.batch = batch_for_shader(self.shader, 'POINTS', {"pos": coords})
		self.update()
	
	def draw_verts(self, verts: list[bmesh.types.BMVert]) -> None:
		'''
		Draw multiple BMesh verts with type checking.
		'''

		for _ in verts:
			if isinstance(_, bmesh.types.BMVert):
				continue

			raise TypeError(f'draw_points() recieved invalid type {type(_)}; expected <bmesh.types.BMVert>')
		
		self.draw_points(points=verts)
	

class LineTracer():
	'''
	Draw Lines or BMesh Edges.
	'''
	
	def __init__(
		self, 
		width: int = 5, 
		color: RGBA = (1, 1, 1, 1), 
		matrix: mathutils.Matrix = None, 
		depth_test: bool = False
	):
		if matrix is None:
			matrix = mathutils.Matrix.Identity(4)
			
		self.matrix = matrix
		self.color  = color
		self.width  = width
		self.shader = self.create_shader()
		self.batch  = None
		self.depth_test = depth_test

	def create_shader(self) -> gpu.types.GPUShader:
		return gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
	
	def update(self) -> None:
		if self.depth_test:
			gpu.state.depth_test_set('LESS_EQUAL')
		gpu.state.blend_set('ALPHA')

		self.shader.bind()
		self.shader.uniform_float('color', self.color)
		self.shader.uniform_float('lineWidth', self.width)
		self.shader.uniform_float("viewportSize", gpu.state.viewport_get()[2:])

		self.batch.draw(self.shader)
		gpu.state.depth_test_set('NONE')
	
	def draw_lines(self, lines: list[tuple[mathutils.Vector, mathutils.Vector] | bmesh.types.BMEdge]) -> None:
		'''
		Draw individual lines from a list of (start, end) tuples.
		'''

		if not lines:
			return

		# Create coordinates from lines.
		coords = []
		indices = []
		idx = 0
		
		for line in lines:
			if isinstance(line, bmesh.types.BMEdge):
				p1, p2 = line.verts[0].co, line.verts[1].co
			else:
				p1, p2 = line[0], line[1]

			coords.append(self.matrix @ p1)
			coords.append(self.matrix @ p2)
			# coords.append(p1)
			# coords.append(p2)

			indices.append((idx, idx+1))
			idx += 2
		
		self.batch = batch_for_shader(self.shader, 'LINES', {"pos": coords}, indices=indices)
		self.update()
	
	
	def draw_edges(self, edges: list[bmesh.types.BMEdge]) -> None:
		'''
		Draw multiple Bmesh edges with type checking.
		'''

		for _ in edges:
			if isinstance(_, bmesh.types.Edge):
				continue

			raise TypeError(f'draw_points() recieved invalid type {type(_)}; expected <bmesh.types.BMEdge>')
		
		self.draw_lines(lines=edges)


class PolyTracer():
	'''
	Draw Polygons or BMesh Faces.
	'''
	
	def __init__(
		self, 
		color: RGBA = (1, 1, 1, .5), 
		matrix: mathutils.Matrix = None, 
		depth_test: bool = False
	):
		if matrix is None:
			matrix = mathutils.Matrix.Identity(4)

		self.matrix = matrix
		self.color  = color
		self.shader = self.create_shader()
		self.batch  = None
		self.depth_test = depth_test

	def create_shader(self) -> gpu.types.GPUShader:
		return gpu.shader.from_builtin('UNIFORM_COLOR')
	
	def update(self) -> None:
		if self.depth_test:
			gpu.state.depth_test_set('LESS_EQUAL')
		gpu.state.blend_set('ALPHA')

		self.shader.bind()
		self.shader.uniform_float('color', self.color)
		self.shader.uniform_float('color', self.color)
		
		self.batch.draw(self.shader)
		gpu.state.depth_test_set('NONE')
	
	def draw_polys(self, polys: list[tuple[mathutils.Vector, ...] | bmesh.types.BMFace]) -> None:
		if not polys:
			return

		all_coords = []
		all_indices = []
		vert_offset = 0

		for poly in polys:
			if isinstance(poly, bmesh.types.BMFace):
				coords = [self.matrix @ v.co for v in poly.verts]
			else:
				coords = [self.matrix @ v for v in poly]

			n = len(coords)
			all_coords.extend(coords)

			for i in range(1, n - 1):
				all_indices.append((vert_offset, vert_offset + i, vert_offset + i + 1))

			vert_offset += n

		self.batch = batch_for_shader(self.shader, 'TRIS', {"pos": all_coords}, indices=all_indices)
		self.update()
	
	def draw_faces(self, faces: list[bmesh.types.BMFace]) -> None:
		'''
		Draw multiple BMesh faces with type checking.
		'''

		for _ in faces:
			if isinstance(_, bmesh.types.BMFace):
				continue

			raise TypeError(f'draw_points() recieved invalid type {type(_)}; expected <bmesh.types.BMFace>')
		
		self.draw_polys(polys=faces)
		


class BaseDrawingMethods:
	'''
	Allows accessing each subclass' methods more directly.
	'''
	
	def __init__(self):
		self.point_tracer: PointTracer
		self.line_tracer:  LineTracer
		self.poly_tracer:  PolyTracer
	
	def draw_points(self, points: list[mathutils.Vector]) -> None:
		self.point_tracer.draw_points(points=points)

	def draw_verts(self, verts: list[bmesh.types.BMVert]) -> None:
		self.point_tracer.draw_verts(points=verts)

	def draw_lines(self, lines: list[tuple[mathutils.Vector, mathutils.Vector]]) -> None:
		self.line_tracer.draw_lines(lines=lines)

	def draw_edges(self, edges: list[bmesh.types.BMEdge]) -> None:
		self.line_tracer.draw_edges(lines=edges)

	def draw_polys(self, polys: list[tuple[mathutils.Vector, ...]]) -> None:
		self.poly_tracer.draw_polys(polys)

	def draw_faces(self, faces: list[bmesh.types.BMFace]) -> None:
		self.poly_tracer.draw_faces(faces)


class ElementTracer():
	'''
	Drawing class for multiple element types.
	'''
	
	def __init__(
			self, 
			point_size:    int = 4, 
			line_width:    int = 2, 
			point_color:  RGBA = (1, 1, 1, 1), 
			line_color:   RGBA = (1, 1, 1, 1), 
			poly_color:   RGBA = (1, 1, 1, 1), 
			global_color: RGBA = None,
			matrix: mathutils.Matrix = None,
			depth_test: bool = False,
		):
		
		if matrix is None:
			matrix = mathutils.Matrix.Identity(4)
		
		self.point_size   = point_size
		self.line_width   = line_width
		self.point_color  = point_color
		self.line_color   = line_color
		self.poly_color   = poly_color
		self.global_color = global_color
		self.matrix       = matrix
		self.depth_test   = depth_test

		if global_color:
			point_color = global_color
			line_color  = global_color
			poly_color  = global_color

		self.point_tracer = PointTracer(
			size   = point_size, 
			color  = point_color, 
			matrix = matrix,
			depth_test = depth_test,
		)
		self.line_tracer =  LineTracer(
			width  = line_width, 
			color  = line_color, 
			matrix = matrix,
			depth_test = depth_test,
		)
		self.poly_tracer =  PolyTracer(
			color  = poly_color, 
			matrix = matrix,
			depth_test = depth_test,
		)
	
	def update_props(self):
		'''
		Update properties of the tracers.
		'''
		
		self.point_tracer.size   = self.point_size
		self.point_tracer.color  = self.point_color
		self.line_tracer.width   = self.line_width
		self.line_tracer.color   = self.line_color
		self.poly_tracer.color   = self.poly_color
		
		if self.global_color:
			self.point_tracer.color = self.global_color
			self.line_tracer.color  = self.global_color
			self.poly_tracer.color  = self.global_color
		
		self.point_tracer.matrix = self.matrix
		self.line_tracer.matrix  = self.matrix
		self.poly_tracer.matrix  = self.matrix

		self.point_tracer.depth_test = self.depth_test
		self.line_tracer.depth_test  = self.depth_test
		self.poly_tracer.depth_test  = self.depth_test
	
	def draw(self, elements: list):
		self.update_props()

		for elem in elements:
			if vert_or_point(elem):
				self.point_tracer.draw_points([elem])
				
			elif edge_or_line(elem):
				self.line_tracer.draw_lines([elem])
			
			elif face_or_poly(elem):
				self.poly_tracer.draw_polys([elem])
			
			else:
				print(f'ElementTracer: Unsupported element type {type(elem)}. Skipping draw.')
				continue
			
	




class ElementTracerCompositor(BaseDrawingMethods):
	'''
	Compositor for drawing multiple element types.
	'''
	
	def __init__(self, point_tracer: PointTracer, line_tracer: LineTracer, poly_tracer: PolyTracer):
		self.point_tracer = point_tracer
		self.line_tracer = line_tracer
		self.poly_tracer = poly_tracer


def draw_points(points:list, size: int = 5, color: RGBA = (1, 1, 1, 1), matrix: mathutils.Matrix = None):
	if matrix is None:
		matrix = mathutils.Matrix.Identity(4)

	point_tracer = PointTracer(
			size   = size, 
			color  = color, 
			matrix = matrix,
		)
	
	point_tracer.draw_points(points=points)



def text_2d(
	text, 
	coords: 	tuple[int, int] = (0, 0),
	offset: 	tuple[int, int] = (0, 0), 
	color:  	RGBA = (1, 1, 1, 1), 
	shadow:		bool = True,
	shadow_color: 	RGBA = (0, 0, 0, 1), 
	font_id:   	int = 0, 
	font_size: 	int = 14,
):
	'''
	Draw screenspace text over the viewport.
	'''

	offset = mathutils.Vector(offset)
	# coords = mathutils.Vector(offset)
	
	mouse_x, mouse_y = coords

	# draw_scale = addon.get_preferences().draw_scale
	draw_scale = 1.25

	blf.size(font_id, int(font_size * draw_scale))
	blf.color(font_id, *color)

	text_width, text_height = blf.dimensions(font_id, text)

	# Subtract half the text wdimensions to center it with the mouse position.
	adjusted_x = mouse_x + (offset.x * draw_scale) - (text_width  / 2)
	adjusted_y = mouse_y + (offset.y * draw_scale) - (text_height / 2)

	blf.position(font_id, adjusted_x, adjusted_y, 1)

	if shadow:
		blf.enable(font_id, blf.SHADOW)
		blur_level = 3	# (0, 3, 5) or outline (6).
		blf.shadow(font_id, blur_level, *shadow_color)
		blf.shadow_offset(font_id, int(1 * draw_scale), int(-1 * draw_scale))

	blf.draw(font_id, text)
	blf.disable(font_id, blf.SHADOW)