# v2.3

import bpy, bmesh
from bpy.props import IntProperty, FloatProperty, BoolProperty

    
class ARMORED_OT_connect(bpy.types.Operator):
    '''Inserts edges based on the context of your selection, it basically combines vert connect, subdivide and knife.

(www.armoredColony.com)'''

    bl_idname = 'mesh.armored_connect'
    bl_label = 'ARMORED Connect'
    bl_options = {'REGISTER', 'UNDO'}

    edge_count : IntProperty   (name='Edge Count', default=1, min=1,   max=20, options={'SKIP_SAVE'})
    stretch    : FloatProperty (name='Stretch',    default=0, min=-99, max=99, options={'SKIP_SAVE'})
    grid_fill  : BoolProperty  (name='Grid Fill',  default=True, description='Affects intersecting edge loops')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.prop(self, 'edge_count')

        sub = layout.row()
        sub.prop(self, 'stretch')
        sub.enabled = self.edge_count > 1 

        layout.prop(self, 'grid_fill')
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        ob = context.edit_object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)

        sel_mode = bpy.context.tool_settings.mesh_select_mode[:]

        # VERTEX MODE
        if sel_mode[0]:
            vert_sel = {v for v in bm.verts if v.select}

            if not vert_sel or len(vert_sel) == 1:
                bpy.ops.mesh.knife_tool('INVOKE_DEFAULT')
                return {'FINISHED'}

            elif len(vert_sel) > 1:
                bpy.ops.mesh.vert_connect_path()  
                return {'FINISHED'}

        # EDGE MODE
        elif sel_mode[1]:
            edge_sel = set(e for e in bm.edges if e.select)

            if not edge_sel:
                bpy.ops.mesh.knife_tool('INVOKE_DEFAULT')
                return {'FINISHED'}

            bpy.ops.mesh.select_all(action='DESELECT')
            
            new_edges  = bmesh.ops.subdivide_edges(bm, edges=list(edge_sel), cuts=1, use_grid_fill=self.grid_fill)
            bad_edges  = set(e for e in new_edges['geom_split'] if isinstance(e, bmesh.types.BMEdge))   # Only store edges.
            
            for e in new_edges['geom_inner']:
                e.select = True
            for e in bad_edges:
                e.select = False

            bm.select_flush_mode()  
            # bpy.ops.mesh.loop_multi_select(ring=False)

            if len(edge_sel) == 1:
                if self.edge_count > 1:
                    c = self.edge_count-1
                    pc = c/(c+2) * 100
                    sel = bmesh.ops.bevel(bm, geom=new_edges['geom_inner'], affect='VERTICES', 
                                            offset_type='PERCENT', offset=pc+self.stretch, segments=self.edge_count-1, loop_slide=True,)
                    for e in sel['verts']: e.select = True

                else:
                    # Reselect that single vert
                    new_edges['geom_inner'][0].select = True

                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

            else:
                if self.edge_count > 1:
                    c = self.edge_count-1
                    pc = c/(c+2) * 100
                    sel = bmesh.ops.bevel(bm, geom=new_edges['geom_inner'], affect='EDGES', 
                                            offset_type='PERCENT', offset=pc+self.stretch, segments=self.edge_count-1, loop_slide=True,)
                    for e in sel['faces']: 
                        e.select = True
            
        # FACE MODE
        elif sel_mode[2]:
            face_sel = {f for f in bm.faces if f.select}
            edge_sel = {e for e in bm.edges if e.select}

            if not face_sel:
                bpy.ops.mesh.knife_tool('INVOKE_DEFAULT')
                return {'FINISHED'}

            if len(face_sel) == 1:
                bpy.ops.mesh.subdivide(number_cuts=self.edge_count)
                return {'FINISHED'}

            elif len(face_sel) > 1:
                # face_sel = {f for f in bm.faces if f.select}

                bpy.ops.mesh.region_to_loop()
                perimeter_edges = set(e for e in bm.edges if e.select)
                contained_edges = edge_sel - perimeter_edges
                
                # We have to do some extra stuff just in case we only selected a partial loop of faces
                # or a partial loop that changes direction
                bpy.ops.mesh.select_all(action='DESELECT')     
                for e in contained_edges: 
                    e.select = True                  

                # Extend and store the full ring because (contained_edges) is missing the first and last
                # edges of the ring if you only selected a partial loop of faces
                bpy.ops.mesh.loop_multi_select(ring=True)
                ring_edges =  set(e for e in bm.edges if e.select)

                # Extending the full ring gives us some corner edges we dont need if we changed direction so lets get them!
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                corner_edges = set(e for e in bm.edges if e.select).intersection(perimeter_edges)

                # Update our ring edges. Still just in case we had a partial loop of faces
                ring_edges -= corner_edges

                # Lets just create a new Set at this point and do everything we need in one line. It works though!
                final_ring_sel = (perimeter_edges.intersection(ring_edges) - corner_edges).union(contained_edges)

                bpy.ops.mesh.select_all(action='DESELECT')

                # SINGLE EDGE BEVEL METHOD >>
                new_edges = bmesh.ops.subdivide_edges(bm, edges=list(final_ring_sel), cuts=1, use_grid_fill=self.grid_fill)
                for e in new_edges['geom_inner']: 
                    e.select = True
            
                if self.edge_count > 1:
                    c = self.edge_count-1
                    pc = c/(c+2) * 100
                    # self.offset = pc+self.stretch
                    sel = bmesh.ops.bevel(bm, geom=new_edges['geom_inner'], offset_type='PERCENT', offset=pc+self.stretch, segments=self.edge_count-1, loop_slide=True, clamp_overlap=True, affect='EDGES')
                    for e in sel['faces']: e.select = True

                    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

        bmesh.update_edit_mesh(me)
        return {'FINISHED'}


classes = (
    ARMORED_OT_connect,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
