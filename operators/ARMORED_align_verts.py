# v1.1

import bpy, bmesh
from bpy.props import EnumProperty

import mathutils
from mathutils import Vector#, geometry


debug = False


def difference_vector(point1, point2, normalized=False):
  # Return Type (Vector)

    new_vec = [0 for coord in point1]

    for dimension, coord in enumerate(point1):
        coord_diff = point2[dimension] - coord
        new_vec[dimension] = coord_diff
      
    if normalized:
        return Vector(new_vec).normalized()
    else:
        return Vector(new_vec)
    

def get_fringe_verts(context):
    # Get the start and end vertices from a list of verts (must be linked by a single loop).
    
    me = context.object.data
    bm = bmesh.from_edit_mesh(me)

    # Get only the verts that are linked to a single other vert (ie, start and end points).
    verts = [v for v in bm.verts if v.select 
        and len([e for e in v.link_edges if e.select]) == 1]

    # bmesh.update_edit_mesh(me)

    return verts


def reorder_verts(context, start, end):
    # We need a selection list that matches the vertex order, for cases where we can't use bm.select_history).

    if debug: 
        print('REORDERING VERTS...')

    me = context.object.data
    bm = bmesh.from_edit_mesh(me)

    start, end = get_fringe_verts(context)

    ordered_verts = [start]
    previous_edges = list()

    selected_verts = [v for v in bm.verts if v.select]

    v = start
    for i in range(len(selected_verts)):
        current_edge = next((e for e in v.link_edges if e.select and e not in previous_edges), None)

        if current_edge:
            previous_edges.append(current_edge)
            if debug:
                print(f'Current Vert: {v.index}')
                print(f'Current Edge: {current_edge.index}')
        else:
            break

        next_vert = next(v for v in current_edge.verts if v.select and v not in ordered_verts)
        if debug:
            print(f'Next Vert: {next_vert.index} \n')

        ordered_verts.append(next_vert)
        v = next_vert
    
    if debug:
        ov_index = [v.index for v in ordered_verts]
        print(f'ORDERED VERTS: {ov_index} \n')

    return ordered_verts


def get_perpendicular_edges(vertex, context):
    v = vertex

    me = context.object.data
    bm = bmesh.from_edit_mesh(me)

    edges = [e for e in v.link_edges if not e.select]
    # e1 = edges[0]
    # e2 = edges[1]
    edges_index = [e.index for e in edges]
    if debug: print(f'Perpendicular Edges for Vert {v.index}: {edges_index}')

    return edges
    

def point_distance(p1, p2):
    # Takes two 3d coordinates/vectors (x, y, z).

    distance = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)**(1/2)

    # print(f'Vertex distance: {dist}')

    return distance


class ARMORED_OT_align_verts(bpy.types.Operator):
    '''Aligns your selection of edges/vertices in a straignt line (Experimental).

(www.armoredColony.com)'''
    
    bl_idname = 'mesh.armored_align_verts'
    bl_label = 'ARMORED Align Vertices'
    bl_options = {'REGISTER', 'UNDO'}

    spacing: EnumProperty( 
        name='Spacing', 
        description='Space the aligned vertices evenly or not.', 
        default='PREDICTIVE', 
        items=[ ('PREDICTIVE', 'Predictive', 'Uses perpendicular loops to determine vertex spacing'),
                ('EVEN',       'Even',       'Even vertex spacing')
            ]
        )
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        row = layout.row(align=True)
        row.prop(self, 'spacing', expand=True)
        
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):

        me = context.object.data
        bm = bmesh.from_edit_mesh(me)

        sel_count = len([v for v in bm.verts if v.select])

        if sel_count != len(bm.select_history):
            v1, v2 = get_fringe_verts(context)
            selected_verts = reorder_verts(context, start=v1, end=v2)
        
        else:
            selected_verts = [v for v in bm.select_history if isinstance(v, bmesh.types.BMVert)]
            v1, v2 = selected_verts[0], selected_verts[-1]

        # get_perpendicular_edges(v1, context)

        dist = point_distance(v1.co, v2.co)
        vec = difference_vector(v1.co, v2.co, normalized=True)

        sel_count = len(selected_verts) -1
        inc = dist / sel_count

        start_co = v1.co
        offset = 0

        for i in range(1, sel_count):

            if self.spacing == 'EVEN':
                offset += inc
                selected_verts[i].co = (start_co + offset * vec)
            
             # PREDICTIVE SPACING
            else:
                p_edges = get_perpendicular_edges(selected_verts[i], context)

                p1 = next(v for v in p_edges[0].verts if not v.select)
                if len(p_edges) == 1:
                    p2 = selected_verts[i]
                elif len(p_edges) == 2:
                    p2 = next(v for v in p_edges[1].verts if not v.select)
                else:
                    # Just for error printing, identical to elif == 2.
                    if debug: print('More that 2 Edges connected')
                    p2 = next(v for v in p_edges[1].verts if not v.select)

                if debug: print(f'Perpendicular Verts: {p1.index, p2.index}')
                a, b, c, d = v1.co, v2.co, p1.co, p2.co # I have to do this for some reason.
                
                intersection = mathutils.geometry.intersect_line_line(a, b, c, d)
                if debug: print(f'Intersection: {intersection}')

                selected_verts[i].co = intersection[0]

        bmesh.update_edit_mesh(me)

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


