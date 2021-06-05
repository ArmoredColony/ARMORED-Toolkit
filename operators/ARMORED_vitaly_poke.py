# v1.2

import bpy, bmesh
from bpy.props import BoolProperty

def main(self, context):
    
    ob = context.edit_object
    me = ob.data
    bm = bmesh.from_edit_mesh(me)

    # Store the faces, the edges and the edge border of our current selection.
    faces = set(f for f in bm.faces if f.select)
    originalEdges = set(e for e in bm.edges if e.select)
    borderEdges = set(e for e in originalEdges 
        if (e.is_boundary or not all(f.select for f in e.link_faces)))

    # Poke the faces and select all of them minus the outer border of triangles.
    poked = bmesh.ops.poke(bm, faces=list(faces))

    if self.select_border_triangles:
        for f in poked['faces']:
                f.select = True
    else:
        for f in poked['faces']:
            f.select = not bool(set(f.edges).intersection(borderEdges))

    # Dissolve the original edges (minus the border) so we end up with a diamond pattern.
    # deleteEdges = originalEdges.difference(borderEdges)
    deleteEdges = originalEdges - borderEdges
    bmesh.ops.dissolve_edges(bm, edges=list(deleteEdges))

    # Easy way to convert our newly selected edges into faces
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

    bmesh.update_edit_mesh(me)

class ARMORED_OT_vitaly_poke(bpy.types.Operator):
    '''Converts a selection of quads into a diamond pattern by using the poke operator and some weird code.

(www.armoredColony.com)'''

    bl_idname = 'mesh.armored_vitaly_poke'
    bl_label = 'ARMORED Vitaly Poke'
    bl_options = {'REGISTER', 'UNDO'}

    select_border_triangles: BoolProperty (name='Select Border Tris', default=True)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.prop(self, 'select_border_triangles', expand=True)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}


classes = (
    ARMORED_OT_vitaly_poke,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)